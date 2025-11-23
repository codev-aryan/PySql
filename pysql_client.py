import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import mysql.connector
from mysql.connector import Error
import csv
from datetime import datetime

class PySqlClient:
    """Main application class for PySql MySQL client"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.query_history = []
        
        # Create connection dialog first
        self.create_connection_dialog()
    
    def create_connection_dialog(self):
        """Create the initial connection dialog window"""
        self.conn_window = tk.Tk()
        self.conn_window.title("PySql - Connect to MySQL")
        self.conn_window.geometry("400x300")
        self.conn_window.resizable(False, False)
        
        # Center the window
        self.center_window(self.conn_window, 400, 300)
        
        # Title label
        title = tk.Label(
            self.conn_window, 
            text="MySQL Connection", 
            font=("Arial", 16, "bold")
        )
        title.pack(pady=20)
        
        # Connection frame
        conn_frame = ttk.Frame(self.conn_window, padding="20")
        conn_frame.pack(fill=tk.BOTH, expand=True)
        
        # Host
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.host_entry = ttk.Entry(conn_frame, width=30)
        self.host_entry.grid(row=0, column=1, pady=5)
        self.host_entry.insert(0, "localhost")
        
        # Username
        ttk.Label(conn_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_entry = ttk.Entry(conn_frame, width=30)
        self.user_entry.grid(row=1, column=1, pady=5)
        self.user_entry.insert(0, "root")
        
        # Password
        ttk.Label(conn_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.pass_entry = ttk.Entry(conn_frame, width=30, show="*")
        self.pass_entry.grid(row=2, column=1, pady=5)
        
        # Database
        ttk.Label(conn_frame, text="Database:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.db_entry = ttk.Entry(conn_frame, width=30)
        self.db_entry.grid(row=3, column=1, pady=5)
        
        # Connect button
        connect_btn = ttk.Button(
            conn_frame, 
            text="Connect", 
            command=self.connect_to_database
        )
        connect_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.conn_window.mainloop()
    
    def center_window(self, window, width, height):
        """Center a window on the screen"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def connect_to_database(self):
        """Establish connection to MySQL database"""
        host = self.host_entry.get()
        user = self.user_entry.get()
        password = self.pass_entry.get()
        database = self.db_entry.get()
        
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                messagebox.showinfo("Success", "Connected to MySQL database successfully!")
                self.conn_window.destroy()
                self.create_main_window()
        
        except Error as e:
            messagebox.showerror("Connection Error", f"Error connecting to MySQL:\n{str(e)}")
    
    def create_main_window(self):
        """Create the main application window"""
        self.main_window = tk.Tk()
        self.main_window.title("PySql - MySQL Client")
        self.main_window.geometry("1200x700")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main container with paned window
        main_paned = ttk.PanedWindow(self.main_window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - History
        self.create_history_panel(main_paned)
        
        # Right panel - Query and Results
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=4)
        
        # Query section
        self.create_query_section(right_frame)
        
        # Results section
        self.create_results_section(right_frame)
        
        # Status bar
        self.create_status_bar()
        
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.main_window.mainloop()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.main_window)
        self.main_window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Query", command=self.clear_query)
        edit_menu.add_command(label="Clear Results", command=self.clear_results)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_history_panel(self, parent):
        """Create the query history sidebar"""
        history_frame = ttk.Frame(parent)
        parent.add(history_frame, weight=1)
        
        # Title
        title = ttk.Label(history_frame, text="Query History", font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        # Clear history button
        clear_btn = ttk.Button(
            history_frame, 
            text="Clear History", 
            command=self.clear_history
        )
        clear_btn.pack(pady=5)
        
        # History listbox with scrollbar
        list_frame = ttk.Frame(history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            font=("Courier", 9)
        )
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        
        self.history_listbox.bind('<<ListboxSelect>>', self.load_history_query)
    
    def create_query_section(self, parent):
        """Create the query editor section"""
        query_frame = ttk.LabelFrame(parent, text="SQL Query Editor", padding="10")
        query_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)
        
        # Toolbar with template buttons
        toolbar = ttk.Frame(query_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            toolbar, 
            text="▶ Execute (F5)", 
            command=self.execute_query
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Label(toolbar, text="Templates:").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar, 
            text="SELECT", 
            command=lambda: self.insert_template("SELECT")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar, 
            text="INSERT", 
            command=lambda: self.insert_template("INSERT")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar, 
            text="UPDATE", 
            command=lambda: self.insert_template("UPDATE")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar, 
            text="DELETE", 
            command=lambda: self.insert_template("DELETE")
        ).pack(side=tk.LEFT, padx=2)
        
        # Query text area
        self.query_text = scrolledtext.ScrolledText(
            query_frame, 
            height=8, 
            font=("Courier", 11),
            wrap=tk.WORD
        )
        self.query_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind F5 key to execute
        self.query_text.bind('<F5>', lambda e: self.execute_query())
    
    def create_results_section(self, parent):
        """Create the results display section"""
        results_frame = ttk.LabelFrame(parent, text="Query Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Results toolbar
        results_toolbar = ttk.Frame(results_frame)
        results_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            results_toolbar, 
            text="Export to CSV", 
            command=self.export_to_csv
        ).pack(side=tk.LEFT, padx=2)
        
        self.result_label = ttk.Label(results_toolbar, text="No results")
        self.result_label.pack(side=tk.LEFT, padx=20)
        
        # Treeview for results
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.results_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.results_tree.yview)
        hsb.config(command=self.results_tree.xview)
    
    def create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_bar = ttk.Label(
            self.main_window, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def insert_template(self, template_type):
        """Insert SQL template into query editor"""
        templates = {
            "SELECT": "SELECT column1, column2\nFROM table_name\nWHERE condition;",
            "INSERT": "INSERT INTO table_name (column1, column2)\nVALUES (value1, value2);",
            "UPDATE": "UPDATE table_name\nSET column1 = value1\nWHERE condition;",
            "DELETE": "DELETE FROM table_name\nWHERE condition;"
        }
        
        template = templates.get(template_type, "")
        self.query_text.insert(tk.INSERT, template)
        self.query_text.focus()
    
    def execute_query(self):
        """Execute the SQL query and display results"""
        query = self.query_text.get("1.0", tk.END).strip()
        
        if not query:
            self.update_status("No query to execute", error=True)
            return
        
        try:
            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            history_entry = f"[{timestamp}] {query[:50]}..."
            self.query_history.append(query)
            self.history_listbox.insert(0, history_entry)
            
            # Execute query
            self.cursor.execute(query)
            
            # Check if query returns results
            if self.cursor.description:
                # SELECT query - fetch results
                columns = [desc[0] for desc in self.cursor.description]
                results = self.cursor.fetchall()
                
                self.display_results(columns, results)
                self.update_status(f"Query executed successfully. {len(results)} rows returned.")
            else:
                # INSERT, UPDATE, DELETE query
                self.connection.commit()
                affected = self.cursor.rowcount
                self.clear_results()
                self.update_status(f"Query executed successfully. {affected} rows affected.")
        
        except Error as e:
            self.update_status(f"Error: {str(e)}", error=True)
            messagebox.showerror("Query Error", f"SQL Error:\n{str(e)}")
    
    def display_results(self, columns, rows):
        """Display query results in the treeview"""
        # Clear existing results
        self.results_tree.delete(*self.results_tree.get_children())
        
        # Configure columns
        self.results_tree['columns'] = columns
        self.results_tree['show'] = 'headings'
        
        # Set column headings and widths
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150, minwidth=100)
        
        # Insert rows
        for row in rows:
            self.results_tree.insert('', tk.END, values=row)
        
        # Update result label
        self.result_label.config(text=f"{len(rows)} rows × {len(columns)} columns")
    
    def clear_results(self):
        """Clear the results treeview"""
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree['columns'] = []
        self.result_label.config(text="No results")
    
    def load_history_query(self, event):
        """Load selected query from history into editor"""
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.query_history):
                query = self.query_history[-(index + 1)]
                self.query_text.delete("1.0", tk.END)
                self.query_text.insert("1.0", query)
    
    def clear_history(self):
        """Clear query history"""
        self.query_history.clear()
        self.history_listbox.delete(0, tk.END)
        self.update_status("History cleared")
    
    def clear_query(self):
        """Clear the query editor"""
        self.query_text.delete("1.0", tk.END)
        self.update_status("Query editor cleared")
    
    def export_to_csv(self):
        """Export current results to CSV file"""
        if not self.results_tree.get_children():
            messagebox.showwarning("No Data", "No results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                columns = self.results_tree['columns']
                writer.writerow(columns)
                
                # Write rows
                for item in self.results_tree.get_children():
                    values = self.results_tree.item(item)['values']
                    writer.writerow(values)
            
            self.update_status(f"Results exported to {filename}")
            messagebox.showinfo("Success", f"Results exported successfully to:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
    
    def update_status(self, message, error=False):
        """Update status bar with message"""
        self.status_bar.config(text=message)
        if error:
            self.status_bar.config(foreground="red")
        else:
            self.status_bar.config(foreground="black")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About PySql",
            "PySql - MySQL Desktop Client\n\n"
            "A lightweight SQL client for MySQL databases.\n\n"
            "Features:\n"
            "• Execute SQL queries\n"
            "• Query templates\n"
            "• Query history\n"
            "• Export to CSV\n\n"
            "Version 1.0"
        )
    
    def on_closing(self):
        """Handle application closing"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
        self.main_window.destroy()


if __name__ == "__main__":
    app = PySqlClient()