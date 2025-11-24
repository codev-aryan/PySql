# PySql - MySQL Desktop Client

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MySQL](https://img.shields.io/badge/MySQL-Compatible-orange.svg)](https://www.mysql.com/)

A lightweight, user-friendly MySQL desktop client built with Python and Tkinter. Perfect for developers, database administrators, and students who need a simple yet powerful tool to interact with MySQL databases.

## 🌟 Features

### Core Functionality
- **🔌 Easy Database Connection** - Quick connection dialog with saved defaults
- **✍️ SQL Query Editor** - Multi-line text editor with F5 quick execution
- **📊 Dynamic Results Display** - Treeview widget that adapts to any query output
- **📝 Query History** - Sidebar panel tracking all executed queries with timestamps
- **📤 CSV Export** - Export query results to CSV format with one click

### Quick Templates
Speed up your workflow with pre-built SQL templates:
- **SELECT** - Query template for retrieving data
- **INSERT** - Template for adding new records
- **UPDATE** - Template for modifying existing data
- **DELETE** - Template for removing records

### User Experience
- Clean, intuitive interface
- Real-time status updates
- Comprehensive error handling
- Resizable windows and panels
- Keyboard shortcuts (F5 to execute)

## 📋 Requirements

- Python 3.7 or higher
- MySQL Server (local or remote)
- Required Python packages:
  - `tkinter` (usually included with Python)
  - `mysql-connector-python`

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/codev-aryan/PySql.git
cd PySql
```

### 2. Install Dependencies
```bash
pip install mysql-connector-python
```

### 3. Ensure MySQL is Running
Make sure your MySQL server is running and you have valid credentials.

### 4. Run the Application
```bash
python pysql_client.py
```

## 💻 Usage

### Connecting to Database
1. Launch the application
2. Enter your MySQL connection details:
   - **Host**: Usually `localhost` or `127.0.0.1`
   - **Username**: Your MySQL username (default: `root`)
   - **Password**: Your MySQL password
   - **Database**: Name of the database to connect to
3. Click **Connect**

### Writing Queries
1. Use the SQL Query Editor in the main window
2. Type your SQL query manually, or
3. Click a template button (SELECT, INSERT, UPDATE, DELETE) to insert a starter template
4. Modify the template with your specific table names and values

### Executing Queries
- Click the **▶ Execute** button, or Press **F5** on your keyboard

### Viewing Results
- SELECT queries display results in the table below
- INSERT/UPDATE/DELETE queries show the number of affected rows in the status bar

### Using Query History
- View all executed queries in the left sidebar
- Click any history entry to reload it into the editor
- Use **Clear History** button to reset the history

### Exporting Results
1. Execute a SELECT query to get results
2. Click **Export to CSV** button
3. Choose a location and filename
4. Results are saved in CSV format

## 📁 Project Structure

```
PySql/
│
├── pysql.py           # Main application file
├── README.md          # This file
├── LICENSE            # License file
└── screenshot.png     # Application screenshot (optional)
```

## 🎯 Use Cases

- **Database Development**: Test queries and view results quickly
- **Learning SQL**: Practice SQL commands with instant feedback
- **Data Analysis**: Extract and export data for analysis
- **Database Administration**: Perform quick maintenance tasks
- **Prototyping**: Test database schema and query logic

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Execute current query |

## 🛠️ Configuration

### Default Connection Settings
The application comes with these defaults (can be changed in the connection dialog):
- Host: `localhost`
- Username: `root`
- Password: (empty)
- Database: (must be specified)

## ⚠️ Error Handling

PySql handles various errors gracefully:
- **Connection Errors**: Displayed in a dialog box with details
- **SQL Syntax Errors**: Shown in status bar and error dialog
- **Export Errors**: Notified with specific error messages

The application will never crash unexpectedly - all errors are caught and displayed to the user.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions
- Add syntax highlighting in the query editor
- Implement query auto-completion
- Add support for other databases (PostgreSQL, SQLite)
- Create a dark theme
- Implement query bookmarks/favorites

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Aryan**
- GitHub: [@codev-aryan](https://github.com/codev-aryan)

## 🙏 Acknowledgments

- Built with Python's Tkinter for the GUI
- MySQL Connector for database connectivity
- Inspired by the need for a simple, lightweight SQL client

---

**Note**: Make sure to create a MySQL database before connecting. You can use MySQL Workbench or command line to create a test database.

---

⭐ **If you find this project useful, please consider giving it a star!** ⭐
