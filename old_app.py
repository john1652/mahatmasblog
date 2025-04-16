from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = 'your_secret_key'  # Change this to a secure random key
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template("index.html", students=students)

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        major = request.form["major"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO students (name, age, major) VALUES (?, ?, ?)", 
            (name, age, major)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("add_student.html")

@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        major = request.form["major"]
        conn.execute("UPDATE students SET name = ?, age = ?, major = ? WHERE id = ?", (name, age, major, student_id))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    
    conn.close()
    return render_template("edit_student.html", student=student)

@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


## 3/24/25 User Registration
@app.route('/registration')
def index():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('index'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    flash('Registration successful', 'success')
    return redirect(url_for('index'))

## @app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('login'))

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user is None or user[2] != password:
            flash('Invalid username or password', 'error')
        else:
            session['user_id'] = user[0]
            flash('Login successful', 'success')
            return redirect(url_for('profile'))

    return render_template('login.html')

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if user_id is None:
        flash('Please log in to access your profile', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    user_name = user['username']
    return render_template('profile.html', user_name=user_name, user_id=user_id)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

### adding for assignment 7
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to view the dashboard.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()

    import datetime
    now = datetime.datetime.now()
    quote = "Keep pushing forward! 💪"

    return render_template('dashboard.html', total_users=total_users, now=now, quote=quote)

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if 'user_id' not in session:
        flash('Please log in to access notes.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        content = request.form['content']
        cursor.execute("INSERT INTO notes (user_id, content) VALUES (?, ?)", (session['user_id'], content))
        conn.commit()

    cursor.execute("SELECT content, timestamp FROM notes WHERE user_id = ? ORDER BY timestamp DESC", (session['user_id'],))
    notes = cursor.fetchall()
    conn.close()

    return render_template('notes.html', notes=notes)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        flash('Please log in to manage your account.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        new_password = request.form['new_password']
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, session['user_id']))
        conn.commit()
        flash('Password updated.', 'success')

    cursor.execute("SELECT username FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    return render_template('settings.html', username=user[0])



if __name__ == "__main__":
    app.run(debug=True)
