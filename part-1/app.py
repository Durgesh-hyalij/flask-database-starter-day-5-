"""
Part 1: Basic Flask with SQLite Database
=========================================
Your first step into databases! Moving from hardcoded lists to real database.

What You'll Learn:
- Connecting Flask to SQLite database
- Creating a table
- Inserting data (Create)
- Reading data (Read)j

Prerequisites: You should know Flask basics (routes, templates, render_template)
"""

from flask import Flask, render_template
import sqlite3  # Built-in Python library for SQLite database

app = Flask(__name__)

DATABASE = 'students.db'  # Database file name (will be created automatically if not exist)


# =============================================================================
# DATABASE HELPER FUNCTIONS
# =============================================================================

def get_db_connection():
    """Create a connection to the database"""
    conn = sqlite3.connect(DATABASE)  # Connect to database file
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name (like dict)
    return conn   #return conn means it will return something and any body can use that further init_db(), / , /add will use


def init_db():
    """Create the table if it doesn't exist"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')  # SQL command to create table with 4 columns
    conn.commit()  # Save changes to database
    conn.close()  # Close connection (so avoid memory fault)


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Home page - Display all students from database"""
    conn = get_db_connection()  # Step 1: Connect to database (open the database)
    students = conn.execute('SELECT * FROM students').fetchall()  # Step 2: Get all rows
    conn.close()  # Step 3: Close connection
    return render_template('index.html', students=students)


@app.route('/add')
def add_sample_student():
    """Add a sample student to database (for testing)"""
    conn = get_db_connection()   # Step 1: Connect to database (open the database)
    conn.execute(
        'INSERT INTO students (name, email, course) VALUES (?, ?, ?)',
        ('Durgesh Hyalij', 'durgesh@example.com', 'Python')  # ? are placeholders (safe from SQL injection)
    )
    conn.commit()  # Don't forget to commit!
    conn.close()    # Step 3: Close connection
    return 'Student added! <a href="/">Go back to home</a>'


if __name__ == '__main__':
    init_db()  # Create table when app starts
    app.run(debug=True)








# =============================================================================
# KEY CONCEPTS EXPLAINED:
# =============================================================================
#
# 1. SQLite: A lightweight database stored in a single file (.db)
#    - No server needed (unlike MySQL/PostgreSQL)
#    - Perfect for learning and small projects
#
# 2. Connection Flow:
#    connect → execute SQL → commit (if changing data) → close
#
# 3. SQL Commands Used:
#    - CREATE TABLE: Define table structure
#    - SELECT * FROM: Get all data
#    - INSERT INTO: Add new data
#
# 4. row_factory = sqlite3.Row:
#    - Without this: row[0], row[1] (access by index)
#    - With this: row['name'], row['email'] (access by column name)
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# Try modifying `add_sample_student()` to add different students with
# different names!
#
# =============================================================================
