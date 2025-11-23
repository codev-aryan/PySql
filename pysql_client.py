import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import mysql.connector
from mysql.connector import Error
import csv
from datetime import datetime

class PySqlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PySql - Lightweight SQL Client")
        self.root.geometry("1000x700")
        
        # State variables
        self.conn = None
        self.cursor = None
        self.query_history = []
        self.current_results = []
        self.current_columns = []

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Start with the connection dialog
        self.show_connection_dialog()

    def show_connection_dialog(self):
        """Displays the initial connection window."""
        self.connect_frame = ttk.Frame(self.root, padding="20 20 20 20")
        self.connect_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(self.connect_frame, text="Connect to MySQL", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Host
        ttk.Label(self.connect_frame, text="Host:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.host_entry = ttk.Entry(self.connect_frame, width=30)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=1, column=1, pady=5)

        # User
        ttk.Label(self.connect_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.user_entry = ttk.Entry(self.connect_frame, width=30)
        self.user_entry.insert(0, "root")
        self.user_entry.grid(row=2, column=1, pady=5)

        # Password
        ttk.Label(self.connect_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.pass_entry = ttk.Entry(self.connect_frame, width=30, show="*")
        self.pass_entry.grid(row=3, column=1, pady=5)

        # Database
        ttk.Label(self.connect_frame, text="Database:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.db_entry = ttk.Entry(self.connect_frame, width=30)
        self.db_entry.grid(row=4, column=1, pady=5)

        # Connect Button
        self.connect_btn = ttk.Button(self.connect_frame, text="Connect", command=self.attempt_connection)
        self.connect_btn.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky=tk.EW)

    def attempt_connection(self):
        """Tries to connect to the database with provided credentials."""
        host = self.host_entry.get()
        user = self.user_entry.get()
        password = self.pass_entry.get()
        database = self.db_entry.get()

        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.conn.is_connected():
                self.cursor = self.conn.cursor()
                self.connect_frame.destroy()
                self.build_main_interface()
                self.status_var.set(f"Connected to {database}@{host}")
        except Error as e:
            messagebox.showerror("Connection Error", f"Failed to connect:\n{e}")

    def build_main_interface(self):
        """Builds the main query execution interface."""
        
        # Main layout: PanedWindow to separate History (left) and Workspace (right)
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # --- Left Panel: History ---
        self.history_frame = ttk.Frame(self.paned_window, width=200, padding=5)
        self.paned_window.add(self.history_frame, weight=1)

        ttk.Label(self.history_frame, text="Query History", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.history_listbox = tk.Listbox(self.history_frame, borderwidth=1, relief="solid")
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        self.history_listbox.bind('<<ListboxSelect>>', self.load_history_query)

        # --- Right Panel: Workspace ---
        self.workspace_frame = ttk.Frame(self.paned_window, padding=5)
        self.paned_window.add(self.workspace_frame, weight=4)

        # 1. Toolbar
        self.toolbar_frame = ttk.Frame(self.workspace_frame)
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(self.toolbar_frame, text="▶ Execute", command=self.execute_query).pack(side=tk.LEFT, padx=2)
        ttk.Separator(self.toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(self.toolbar_frame, text="Insert Tpl", command=lambda: self.insert_template("INSERT")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar_frame, text="Update Tpl", command=lambda: self.insert_template("UPDATE")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar_frame, text="Delete Tpl", command=lambda: self.insert_template("DELETE")).pack(side=tk.LEFT, padx=2)
        ttk.Separator(self.toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(self.toolbar_frame, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=2)

        # 2. Query Editor
        ttk.Label(self.workspace_frame, text="SQL Query Editor:").pack(anchor=tk.W)
        self.query_text = scrolledtext.ScrolledText(self.workspace_frame, height=8, font=('Consolas', 10))
        self.query_text.pack(fill=tk.X, pady=(0, 10))

        # 3. Results View
        ttk.Label(self.workspace_frame, text="Results:").pack(anchor=tk.W)
        
        # Treeview with scrollbars
        self.tree_frame = ttk.Frame(self.workspace_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(self.tree_frame, show='headings', 
                                 yscrollcommand=self.tree_scroll_y.set, 
                                 xscrollcommand=self.tree_scroll_x.set)
        
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)
        
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 4. Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def insert_template(self, template_type):
        """Inserts SQL templates into the editor."""
        templates = {
            "INSERT": "INSERT INTO table_name (column1, column2) VALUES (value1, value2);",
            "UPDATE": "UPDATE table_name SET column1 = value1 WHERE condition;",
            "DELETE": "DELETE FROM table_name WHERE condition;"
        }
        snippet = templates.get(template_type, "")
        self.query_text.insert(tk.INSERT, snippet)
        self.query_text.focus_set()

    def execute_query(self):
        """Executes the SQL query from the text area."""
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            return

        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        self.current_results = []
        self.current_columns = []
        
        try:
            self.status_var.set("Executing...")
            self.root.update_idletasks()
            
            # Execute
            self.cursor.execute(query)
            
            # Check if it's a SELECT query or returns rows
            if self.cursor.description:
                columns = [col[0] for col in self.cursor.description]
                rows = self.cursor.fetchall()
                
                self.setup_tree_columns(columns)
                for row in rows:
                    self.tree.insert("", tk.END, values=row)
                
                self.current_columns = columns
                self.current_results = rows
                msg = f"Success. {len(rows)} rows returned."
            else:
                # For INSERT, UPDATE, DELETE
                self.conn.commit()
                msg = f"Success. {self.cursor.rowcount} rows affected."
                # Clear tree columns for non-select queries
                self.tree['columns'] = []
            
            self.status_var.set(msg)
            self.add_to_history(query)
            
        except Error as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("SQL Execution Error", str(e))

    def setup_tree_columns(self, columns):
        """Configures the Treeview columns dynamically."""
        self.tree['columns'] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            # Rough estimation of width based on header length
            width = max(len(col) * 10, 100)
            self.tree.column(col, width=width, minwidth=50)

    def add_to_history(self, query):
        """Adds executed query to history list and UI."""
        # Avoid duplicate consecutive entries
        if not self.query_history or self.query_history[-1] != query:
            self.query_history.append(query)
            # Display truncated version in listbox
            display_text = query[:30].replace("\n", " ") + "..." if len(query) > 30 else query.replace("\n", " ")
            self.history_listbox.insert(tk.END, display_text)
            self.history_listbox.yview(tk.END)

    def load_history_query(self, event):
        """Loads selected query from history into editor."""
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            query = self.query_history[index]
            self.query_text.delete("1.0", tk.END)
            self.query_text.insert("1.0", query)

    def export_csv(self):
        """Exports the current Treeview results to a CSV file."""
        if not self.current_results:
            messagebox.showinfo("Export Info", "No results to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(self.current_columns)
                    writer.writerows(self.current_results)
                self.status_var.set(f"Exported to {file_path}")
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save file:\n{e}")

    def on_closing(self):
        """Cleanup connection on close."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PySqlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
