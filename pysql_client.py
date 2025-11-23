"""
PySql - A lightweight MySQL client using tkinter and mysql-connector-python
Single-file application. Features:
- Connection dialog (host, user, password, database)
- SQL editor area (Text widget)
- Quick-action toolbar with Insert/Update/Delete templates
- Execute button to run queries and show results in a Treeview
- History panel that stores previous queries and reloads on click
- Export results to CSV
- Status bar for errors and messages

Dependencies:
- python 3.8+
- mysql-connector-python (pip install mysql-connector-python)

Run: python pysql_app.py

"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import mysql.connector
from mysql.connector import Error
import csv
import datetime

# -----------------------------
# Helper / Utility Functions
# -----------------------------

def safe_commit(conn):
    try:
        conn.commit()
    except Exception:
        # ignore commit errors here; handled at callsite
        pass

# -----------------------------
# Connection Dialog
# -----------------------------
class ConnectionDialog(simpledialog.Dialog):
    """Modal dialog for entering connection parameters."""
    def __init__(self, parent, title=None, defaults=None):
        self.defaults = defaults or {}
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Host:").grid(row=0, column=0, sticky="e")
        tk.Label(master, text="Username:").grid(row=1, column=0, sticky="e")
        tk.Label(master, text="Password:").grid(row=2, column=0, sticky="e")
        tk.Label(master, text="Database:").grid(row=3, column=0, sticky="e")

        self.host_var = tk.StringVar(value=self.defaults.get("host", "localhost"))
        self.user_var = tk.StringVar(value=self.defaults.get("user", "root"))
        self.pass_var = tk.StringVar(value=self.defaults.get("password", ""))
        self.db_var = tk.StringVar(value=self.defaults.get("database", ""))

        self.host_entry = tk.Entry(master, textvariable=self.host_var)
        self.user_entry = tk.Entry(master, textvariable=self.user_var)
        self.pass_entry = tk.Entry(master, textvariable=self.pass_var, show="*")
        self.db_entry = tk.Entry(master, textvariable=self.db_var)

        self.host_entry.grid(row=0, column=1, padx=8, pady=4)
        self.user_entry.grid(row=1, column=1, padx=8, pady=4)
        self.pass_entry.grid(row=2, column=1, padx=8, pady=4)
        self.db_entry.grid(row=3, column=1, padx=8, pady=4)

        return self.host_entry

    def apply(self):
        self.result = {
            "host": self.host_var.get().strip(),
            "user": self.user_var.get().strip(),
            "password": self.pass_var.get(),
            "database": self.db_var.get().strip(),
        }

# -----------------------------
# Main Application
# -----------------------------
class PySqlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PySql")
        self.geometry("1000x650")

        # state
        self.conn = None
        self.cursor = None
        self.history = []  # list of (timestamp, query)
        self.current_results = None  # tuple (columns, rows)

        self._create_widgets()
        self._layout_widgets()
        self._bind_events()

        # ask for connection immediately
        self.after(100, self.open_connection_dialog)

    # -----------------------------
    # UI Creation
    # -----------------------------
    def _create_widgets(self):
        # Top toolbar frame
        self.toolbar = ttk.Frame(self)

        self.btn_insert_template = ttk.Button(self.toolbar, text="Insert Template", command=self._insert_insert_template)
        self.btn_update_template = ttk.Button(self.toolbar, text="Update Template", command=self._insert_update_template)
        self.btn_delete_template = ttk.Button(self.toolbar, text="Delete Template", command=self._insert_delete_template)

        self.btn_execute = ttk.Button(self.toolbar, text="Execute", command=self.execute_query)
        self.btn_export = ttk.Button(self.toolbar, text="Export CSV", command=self.export_csv)
        self.btn_connect = ttk.Button(self.toolbar, text="Reconnect", command=self.open_connection_dialog)

        # Main frames
        self.main_pane = ttk.Panedwindow(self, orient=tk.HORIZONTAL)

        # Left: history panel
        self.history_frame = ttk.Frame(self.main_pane, width=220)
        self.history_label = ttk.Label(self.history_frame, text="History")
        self.history_listbox = tk.Listbox(self.history_frame)
        self.history_scroll = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=self.history_scroll.set)

        # Center: editor + results
        self.center_frame = ttk.Frame(self.main_pane)

        self.editor_label = ttk.Label(self.center_frame, text="SQL Editor")
        self.editor_text = tk.Text(self.center_frame, wrap="none", height=8)
        self.editor_vscroll = ttk.Scrollbar(self.center_frame, orient=tk.VERTICAL, command=self.editor_text.yview)
        self.editor_hscroll = ttk.Scrollbar(self.center_frame, orient=tk.HORIZONTAL, command=self.editor_text.xview)
        self.editor_text.configure(yscrollcommand=self.editor_vscroll.set, xscrollcommand=self.editor_hscroll.set, undo=True)

        # Results label + treeview
        self.results_label = ttk.Label(self.center_frame, text="Results")
        self.results_frame = ttk.Frame(self.center_frame)
        self.result_tree = ttk.Treeview(self.results_frame, show="headings")
        self.result_vscroll = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_hscroll = ttk.Scrollbar(self.results_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=self.result_vscroll.set, xscrollcommand=self.result_hscroll.set)

        # Status bar
        self.statusbar = ttk.Frame(self)
        self.status_label = ttk.Label(self.statusbar, text="Not connected", anchor="w")

    def _layout_widgets(self):
        # toolbar
        self.toolbar.pack(fill=tk.X, padx=4, pady=4)
        self.btn_insert_template.pack(side=tk.LEFT, padx=4)
        self.btn_update_template.pack(side=tk.LEFT, padx=4)
        self.btn_delete_template.pack(side=tk.LEFT, padx=4)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        self.btn_execute.pack(side=tk.LEFT, padx=4)
        self.btn_export.pack(side=tk.LEFT, padx=4)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        self.btn_connect.pack(side=tk.LEFT, padx=4)

        # panes
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0,6))
        self.main_pane.add(self.history_frame, weight=0)
        self.main_pane.add(self.center_frame, weight=1)

        # history frame
        self.history_label.pack(anchor="w", padx=6, pady=(6,0))
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,0), pady=6)
        self.history_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,6), pady=6)

        # center frame - editor
        self.editor_label.grid(row=0, column=0, sticky="w", padx=6)
        self.editor_text.grid(row=1, column=0, sticky="nsew", padx=(6,0), pady=(4,4))
        self.editor_vscroll.grid(row=1, column=1, sticky="ns", pady=(4,4))
        self.editor_hscroll.grid(row=2, column=0, sticky="ew", padx=(6,0))

        # results
        self.results_label.grid(row=3, column=0, sticky="w", padx=6, pady=(6,0))
        self.results_frame.grid(row=4, column=0, sticky="nsew", padx=6, pady=(4,6))
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.result_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_hscroll.pack(side=tk.BOTTOM, fill=tk.X)

        # configure grid weights for resizability
        self.center_frame.rowconfigure(1, weight=0)  # editor height remains small
        self.center_frame.rowconfigure(4, weight=1)  # results grow
        self.center_frame.columnconfigure(0, weight=1)

        # status bar
        self.statusbar.pack(fill=tk.X)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=4)

    def _bind_events(self):
        self.history_listbox.bind("<<ListboxSelect>>", self._on_history_select)
        # keyboard shortcuts
        self.bind_all("<Control-Return>", lambda e: self.execute_query())
        self.bind_all("<Control-s>", lambda e: self.export_csv())

    # -----------------------------
    # Templates
    # -----------------------------
    def _insert_insert_template(self):
        snippet = "INSERT INTO table_name (column1, column2) VALUES (value1, value2);\n"
        self._insert_into_editor(snippet)

    def _insert_update_template(self):
        snippet = "UPDATE table_name SET column1 = value1 WHERE condition;\n"
        self._insert_into_editor(snippet)

    def _insert_delete_template(self):
        snippet = "DELETE FROM table_name WHERE condition;\n"
        self._insert_into_editor(snippet)

    def _insert_into_editor(self, text):
        self.editor_text.insert(tk.INSERT, text)
        self.editor_text.focus_set()

    # -----------------------------
    # Connection Handling
    # -----------------------------
    def open_connection_dialog(self):
        defaults = {"host": "localhost", "user": "root"}
        dlg = ConnectionDialog(self, title="Connect to MySQL", defaults=defaults)
        if dlg.result:
            params = dlg.result
            self._connect(params)

    def _connect(self, params):
        # close previous
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except Exception:
            pass

        try:
            self.status_label.config(text="Connecting...")
            self.update_idletasks()
            self.conn = mysql.connector.connect(
                host=params.get("host"),
                user=params.get("user"),
                password=params.get("password"),
                database=params.get("database"),
                autocommit=False,
            )
            self.cursor = self.conn.cursor(buffered=True)
            self.status_label.config(text=f"Connected to {params.get('database')}@{params.get('host')}")
        except Error as e:
            self.conn = None
            self.cursor = None
            self.status_label.config(text=f"Connection error: {e}")
            messagebox.showerror("Connection Error", str(e))

    # -----------------------------
    # Query Execution and Results
    # -----------------------------
    def execute_query(self):
        query = self.editor_text.get("1.0", tk.END).strip()
        if not query:
            self.status_label.config(text="No query to execute")
            return

        # Save to history with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.insert(0, (timestamp, query))
        self._refresh_history()

        if not self.conn or not self.cursor:
            self.status_label.config(text="Not connected. Please connect first.")
            messagebox.showwarning("Not connected", "Please connect to a MySQL database first.")
            return

        try:
            # Try to detect if it's a SELECT to fetch results
            sql = query.strip()
            first_word = sql.split()[0].lower()

            if first_word == 'select' or sql.lower().startswith('with'):
                self.cursor.execute(sql)
                columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
                rows = self.cursor.fetchall()
                self.current_results = (columns, rows)
                self._display_results(columns, rows)
                self.status_label.config(text=f"Query executed: {len(rows)} rows returned")
            else:
                # For non-select, execute possibly multiple statements separated by semicolon
                # mysql-connector supports multi=True
                executed = False
                if ';' in sql:
                    # execute as a single batch using multi
                    for result in self.cursor.execute(sql, multi=True):
                        executed = True
                        # if it produces rows, fetch them (rare for non-select)
                        try:
                            if result.with_rows:
                                cols = [d[0] for d in result.description]
                                rows = result.fetchall()
                                self.current_results = (cols, rows)
                                self._display_results(cols, rows)
                        except Exception:
                            pass
                else:
                    self.cursor.execute(sql)
                    affected = self.cursor.rowcount
                    safe_commit(self.conn)
                    self.current_results = ([], [])
                    self._clear_results()
                    self.status_label.config(text=f"Statement executed: {affected} rows affected")

        except Error as e:
            self.status_label.config(text=f"SQL Error: {e}")
            messagebox.showerror("SQL Error", str(e))
        except Exception as e:
            self.status_label.config(text=f"Execution error: {e}")
            messagebox.showerror("Execution Error", str(e))

    def _display_results(self, columns, rows):
        # clear existing
        for col in self.result_tree.get_children():
            self.result_tree.delete(col)
        self.result_tree['columns'] = columns
        # set headings and column config
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=120, anchor='w')

        # insert rows
        for row in rows:
            # convert row values to strings; handle bytes/None
            processed = [self._format_cell(v) for v in row]
            self.result_tree.insert('', tk.END, values=processed)

    def _format_cell(self, v):
        if v is None:
            return "NULL"
        # convert bytes to repr
        if isinstance(v, (bytes, bytearray)):
            return repr(v)
        return str(v)

    def _clear_results(self):
        self.result_tree['columns'] = []
        for r in self.result_tree.get_children():
            self.result_tree.delete(r)

    # -----------------------------
    # History
    # -----------------------------
    def _refresh_history(self):
        self.history_listbox.delete(0, tk.END)
        for ts, q in self.history:
            # show short preview
            preview = q.replace('\n', ' ')[:80]
            self.history_listbox.insert(tk.END, f"{ts} — {preview}")

    def _on_history_select(self, event):
        sel = self.history_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        ts, q = self.history[index]
        # load the full query into editor
        self.editor_text.delete('1.0', tk.END)
        self.editor_text.insert(tk.END, q)
        self.status_label.config(text=f"Loaded query from history ({ts})")

    # -----------------------------
    # Export
    # -----------------------------
    def export_csv(self):
        if not self.current_results or not self.current_results[0]:
            messagebox.showinfo("No data", "There is no tabular result to export.")
            return
        columns, rows = self.current_results
        default_name = f"pysql_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(defaultextension='.csv', initialfile=default_name, filetypes=[('CSV files', '*.csv'), ('All files','*.*')])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                for row in rows:
                    writer.writerow([self._csv_safe_cell(c) for c in row])
            self.status_label.config(text=f"Exported {len(rows)} rows to {path}")
            messagebox.showinfo("Export Complete", f"Exported {len(rows)} rows to {path}")
        except Exception as e:
            self.status_label.config(text=f"Export error: {e}")
            messagebox.showerror("Export Error", str(e))

    def _csv_safe_cell(self, v):
        if v is None:
            return ''
        if isinstance(v, (bytes, bytearray)):
            return repr(v)
        return str(v)

# -----------------------------
# Run the app
# -----------------------------
if __name__ == '__main__':
    try:
        app = PySqlApp()
        app.mainloop()
    except Exception as exc:
        # Top-level catch so errors are visible rather than silently failing
        tk.Tk().withdraw()
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{exc}")
"""
