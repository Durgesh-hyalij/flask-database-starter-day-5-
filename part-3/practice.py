"""
Part 3: Flask-SQLAlchemy ORM
============================
Say goodbye to raw SQL! Use Python classes to work with databases.

What You'll Learn:
- Setting up Flask-SQLAlchemy
- Creating Models (Python classes = database tables)
- ORM queries instead of raw SQL
- Relationships between tables (One-to-Many)

Prerequisites: Complete part-1 and part-2
Install: pip install flask-sqlalchemy
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'  # Database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable warning

db = SQLAlchemy(app)  # Initialize SQLAlchemy with app


# =============================================================================
# MODELS (Python Classes = Database Tables)
# =============================================================================

class Course(db.Model):  # Course table
    id = db.Column(db.Integer, primary_key=True)  # Auto-increment ID ->when integer and primary key comes together it means it will auto increment 
    name = db.Column(db.String(100), nullable=False)  # Course name
    description = db.Column(db.Text)  # Optional description

    # Relationship: One Course has Many Students
    students = db.relationship('Student', backref='course', lazy=True)   # general structure -> <collection_name> = db.relationship('<RelatedModel>', backref='<reverse_name>', lazy=<loading_strategy>)

    teachers = db.relationship('Teacher', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.name}>'


class Student(db.Model):  # Student table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # unique=True means no duplicates
    email = db.Column(db.String(100),  nullable=False)
    
    # Foreign Key: Links student to a course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  #<column_name> = db.Column(db.<Type>, db.ForeignKey('<parent_table>.<parent_pk>'), nullable=<True/False>)

    def __repr__(self):
        return f'<Student {self.name}>'

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable = False)

    # Foreign key → one Teacher belongs to one Course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Teacher {self.name}>'
    
#  Read this
# course.teachers      # list of teachers for a course
# teacher.course       # course of this teacher

# course.students      # list of students
# student.course       # course of this student

# =============================================================================
# ROUTES - Using ORM instead of raw SQL
# =============================================================================

@app.route('/')
def index():
    # OLD WAY (raw SQL): conn.execute('SELECT * FROM students').fetchall()
    # NEW WAY (ORM):
    students = Student.query.all()  # Get all students
    teachers = Teacher.query.all()  # Get all students
    return render_template('index.html', students=students , teachers = teachers) 


@app.route('/courses')
def courses():
    all_courses = Course.query.all()  # Get all courses
    return render_template('courses.html', courses=all_courses)


# @app.route('/add', methods=['GET', 'POST'])
# def add_student():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         course_id = request.form['course_id']

#         # OLD WAY: conn.execute('INSERT INTO students...')
#         # NEW WAY:
#         new_student = Student(name=name, email=email, course_id=course_id)  # Create object
#         db.session.add(new_student)  # Add to session
#         db.session.commit()  # Save to database

#         flash('Student added successfully!', 'success')
#         return redirect(url_for('index'))

#     courses = Course.query.all()  # Get courses for dropdown
#     return render_template('add.html', courses=courses)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # 1️⃣ Get form data safely
        name = request.form.get('name')
        email = request.form.get('email')
        course_id = request.form.get('course_id')

        # 2️⃣ Required field validation
        if not name or not email or not course_id:
            flash('All fields are required', 'danger')
            return redirect(url_for('add_student'))

        # 3️⃣ Check duplicate email (business validation)
        if Student.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('add_student'))

        # 4️⃣ Validate course exists
        course = Course.query.get(course_id)
        if not course:
            flash('Invalid course selected', 'danger')
            return redirect(url_for('add_student'))

        # 5️⃣ Try database insert safely
        try:
            new_student = Student(
                name=name,
                email=email,
                course_id=course_id
            )
            db.session.add(new_student)
            db.session.commit()

            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))

        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'danger')
            return redirect(url_for('add_student'))

    # GET request
    courses = Course.query.all()
    return render_template('add.html', courses=courses)


# @app.route('/edit/<int:id>', methods=['GET', 'POST'])
# def edit_student(id):
#     # OLD WAY: conn.execute('SELECT * FROM students WHERE id = ?', (id,))
#     # NEW WAY:
#     student = Student.query.get_or_404(id)  # Get by ID or show 404 error

#     if request.method == 'POST':
#         student.name = request.form['name']  # Just update the object
#         student.email = request.form['email']
#         student.course_id = request.form['course_id']

#         db.session.commit()  # Save changes
#         flash('Student updated!', 'success')
#         return redirect(url_for('index'))

#     courses = Course.query.all()
#     return render_template('edit.html', student=student, courses=courses)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    # OLD WAY: conn.execute('SELECT * FROM students WHERE id = ?', (id,))
    # NEW WAY:
    student = Student.query.get_or_404(id)  # Get by ID or show 404 error

    if request.method == 'POST':
        # student.name = request.form['name']  # Just update the object
        # student.email = request.form['email']
        # student.course_id = request.form['course_id']

        name = request.form.get('name')
        email = request.form.get('email')
        course_id = request.form.get('course_id')

        if not name or not email or not course_id:
            flash('ALL Filelds are required' , 'danger')
            return redirect(url_for('edit_student' , id = id))
        
        course = Course.query.get(course_id)
        if not course:
            flash('Invalid course selected' , 'danger')
            return redirect(url_for('edit_student' , id = id))
        
        existing_student = Student.query.filter( 
            Student.email == email ,
            Student.id != id   
        ).first()

        if existing_student:
            flash('Email already exist' , 'danger')
            return redirect(url_for('edit_student' , id=id))

        try:
            student.name = name
            student.email = email
            student.course_id = course_id

            flash('Student updated!', 'success')
            db.session.commit()  # Save changes
            return redirect(url_for('index'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred', 'danger')
            return redirect(url_for('edit_teacher', id=id))

      

    courses = Course.query.all()
    return render_template('edit.html', student=student, courses=courses)


@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)   #This line fetches a Student by its ID, and if it does not exist, Flask automatically returns a 404 Not Found error.
    db.session.delete(student)  # Delete the object
    db.session.commit()

    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')  # Optional field

        new_course = Course(name=name, description=description)
        db.session.add(new_course)
        db.session.commit()

        flash('Course added!', 'success')
        return redirect(url_for('courses'))

    return render_template('add_course.html')

@app.route('/teachers')
def teachers():
    teacher_list = Teacher.query.all()
    
    return render_template('teacher.html' , teachers = teacher_list)

# @app.route('/add-teacher' , methods = ['GET' , 'POST'])
# def add_teacher():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         course_id = request.form.get('course_id')

#         new_teacher = Teacher(name = name, email=email , course_id = course_id)
#         db.session.add(new_teacher)
#         db.session.commit()

#         flash('teacher added successfully' , 'success')
#         return redirect(url_for('teachers'))

#     courses = Course.query.all()
#     return render_template("add_teacher.html" , courses=courses )


@app.route('/add-teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        # 1️⃣ Get form data safely
        name = request.form.get('name')
        email = request.form.get('email')
        course_id = request.form.get('course_id')

        # 2️⃣ Required field validation
        if not name or not email or not course_id:
            flash('All fields are required', 'danger')
            return redirect(url_for('add_teacher'))

        # 3️⃣ Check duplicate email (business validation)
        if Student.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('add_teacher'))

        # 4️⃣ Validate course exists
        course = Course.query.get(course_id)
        if not course:
            flash('Invalid course selected', 'danger')
            return redirect(url_for('add_teacher'))

        # 5️⃣ Try database insert safely
        try:
            new_teacher = Teacher(
                name=name,
                email=email,
                course_id=course_id
            )
            db.session.add(new_teacher)
            db.session.commit()

            flash('Teacher added successfully!', 'success')
            return redirect(url_for('index'))

        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'danger')
            return redirect(url_for('add_teacher'))

    # GET request
    courses = Course.query.all()
    return render_template('add_teacher.html', courses=courses)






# @app.route('/edit_teacher/<int:id>' , methods=['GET' , 'POST'])
# def edit_teacher(id):
#     teacher = Teacher.query.get_or_404(id)

#     if request.method == 'POST':
#         teacher.name = request.form.get('name')
#         teacher.email = request.form.get('email')
#         teacher.course_id = request.form.get('course_id')

#         db.session.commit()
#         flash('teacher updated successfully')
#         return redirect(url_for('teachers'))
    
#     courses = Course.query.all()
#     return render_template('edit_teacher.html', teacher = teacher , courses = courses)


@app.route('/edit_teacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        course_id = request.form.get('course_id')

        # 1️⃣ Required fields
        if not name or not email or not course_id:
            flash('All fields are required', 'danger')
            return redirect(url_for('edit_teacher', id=id))

        # 2️⃣ Validate course
        course = Course.query.get(course_id)
        if not course:
            flash('Invalid course selected', 'danger')
            return redirect(url_for('edit_teacher', id=id))

        # 3️⃣ Email uniqueness check (exclude current teacher)
        existing_teacher = Teacher.query.filter(
            Teacher.email == email,
            Teacher.id != id
        ).first()

        if existing_teacher:
            flash('Email already exists', 'danger')
            return redirect(url_for('edit_teacher', id=id))

        # 4️⃣ Update object
        try:
            teacher.name = name
            teacher.email = email
            teacher.course_id = course_id

            db.session.commit()
            flash('Teacher updated successfully', 'success')
            return redirect(url_for('teachers'))

        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred', 'danger')
            return redirect(url_for('edit_teacher', id=id))

    # GET request
    courses = Course.query.all()
    return render_template(
        'edit_teacher.html',
        teacher=teacher,
        courses=courses
    )


@app.route('/delete_teacher/<int:id>')
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)

    db.session.delete(teacher)
    db.session.commit()

    flash('Student deleted!', 'danger')
    return redirect(url_for('teachers'))

# =============================================================================
# CREATE TABLES AND ADD SAMPLE DATA
# =============================================================================

def init_db():
    """Create tables and add sample courses if empty"""
    with app.app_context():
        db.create_all()  # Create all tables based on models

        # Add sample courses if none exist
        if Course.query.count() == 0:
            sample_courses = [
                Course(name='Python Basics', description='Learn Python programming fundamentals'),
                Course(name='Web Development', description='HTML, CSS, JavaScript and Flask'),
                Course(name='Data Science', description='Data analysis with Python'),
            ]
            db.session.add_all(sample_courses)  # Add multiple at once
            db.session.commit()
            print('Sample courses added!')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# ORM vs RAW SQL COMPARISON:
# =============================================================================
#
# Operation      | Raw SQL                          | SQLAlchemy ORM
# ---------------|----------------------------------|---------------------------
# Get all        | SELECT * FROM students           | Student.query.all()
# Get by ID      | SELECT * WHERE id = ?            | Student.query.get(id)
# Filter         | SELECT * WHERE name = ?          | Student.query.filter_by(name='John')
# Insert         | INSERT INTO students VALUES...   | db.session.add(student)
# Update         | UPDATE students SET...           | student.name = 'New'; db.session.commit()
# Delete         | DELETE FROM students WHERE...    | db.session.delete(student)
#
# =============================================================================
# COMMON QUERY METHODS:
# =============================================================================
#
# Student.query.all()                    - Get all records
# Student.query.first()                  - Get first record
# Student.query.get(1)                   - Get by primary key
# Student.query.get_or_404(1)            - Get or show 404 error
# Student.query.filter_by(name='John')   - Filter by exact value
# Student.query.filter(Student.name.like('%john%'))  - Filter with LIKE
# Student.query.order_by(Student.name)   - Order results
# Student.query.count()                  - Count records
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Add a `Teacher` model with a relationship to Course
# 2. Try different query methods: `filter()`, `order_by()`, `limit()`
#
# =============================================================================

