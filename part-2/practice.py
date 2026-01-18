from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)  #connect databasefile  
    conn.row_factory = sqlite3.Row  
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        conn = get_db_connection()
        conn.execute(
        'INSERT INTO students (name, email, course) VALUES (?,?,?)' , (name, email, course)
)
        conn.commit()
        conn.close()

        flash('student submit successfully' , 'success')
        return redirect(url_for('index'))
    
    return render_template("add.html")

@app.route('edit/<int:id>' , methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form('name')
        email = request.form('email')
        course = request.form('course')

        conn.execute(
        'UPDATE student SET name =? , email = ?, course =? WHERE id= ?',
        (name,email,course,id)
    )
        
    conn.commit()
    conn.close()

    flash('Students updated successfully!' , 'success')
    return redirect(url_for('index'))

    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit.html', student = student)


@app.route('/search' , method = ['GET' , 'POST'])
def search():
    conn = get_db_connection()

    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('SELECT id,name,email,course FROM students where id = id,name = name, email=email,course=course')
        conn.commit()
        conn.close()

        flash('student search sucessfully' , 'success')
        return render_template("search.html")

@app.route('/delete/<id:int>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM student WHERE id=?' , (id,))
    conn.close()

    flash('student deleted successfully' , 'danger')
    return redirect('url_for(index)')



if __name__ == '__main__':
    init_db()
    app.run(debug=True)




                            











