from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = 'your_secret_key'  # Change this to a secure random key
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    conn = get_db_connection()
    blog_posts = conn.execute(
        "SELECT * FROM blog_posts ORDER BY date DESC LIMIT 3"
    ).fetchall()
    conn.close()
    return render_template('index.html', blog_posts=blog_posts)


@app.route('/blog_posts', methods=['GET', 'POST'])
def blog_posts_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all unique blog categories for the filter dropdown
    cursor.execute("SELECT DISTINCT blog_category FROM blog_posts")
    categories = [row[0] for row in cursor.fetchall()]

    # Handle filtering
    selected_category = request.args.get('category', 'all')  # Default to 'all'
    if selected_category == 'all':
        cursor.execute("SELECT * FROM blog_posts")
    else:
        cursor.execute("SELECT * FROM blog_posts WHERE blog_category = ?", (selected_category,))
    blog_posts = cursor.fetchall()

    conn.close()
    return render_template('blog_posts.html', blog_posts=blog_posts, categories=categories, selected_category=selected_category)

@app.route('/temp_blog_post')
def temp_blog_post():
    conn = get_db_connection()
    blog_posts = conn.execute("SELECT * FROM blog_posts").fetchall()
    conn.close()
    return render_template('temp_blog_post.html', blog_posts=blog_posts)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Insert data into the users table
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
            (username, name, email, password)
        )
        conn.commit()
        conn.close()

        flash('User added successfully!', 'success')
        # Redirect to the profile page for the newly created user
        return redirect(url_for('profile', username=username))

    return render_template('add_user.html')


@app.route('/add_blog_post', methods=['GET', 'POST'])
def add_blog_post():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to add a blog post.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        blog_category = request.form['blog_category']
        title = request.form['title']
        date = request.form['date']
        body = request.form['body']
        blog_type = request.form['blog_type']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO blog_posts (user_id, blog_category, title, date, body, blog_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, blog_category, title, date, body, blog_type))
        conn.commit()
        conn.close()

        flash('Blog post added successfully!', 'success')
        return redirect(url_for('blog_posts_page'))

    return render_template('add_blog_post.html', user_id=user_id)

@app.route('/user_list')
def user_list():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [{'username': row[0]} for row in cursor.fetchall()]
    conn.close()
    return render_template('user_list.html', users=users)

@app.route('/blog_post/<int:post_id>', methods=['GET', 'POST'])
def blog_post(post_id):
    conn = get_db_connection()
    if request.method == 'POST':
        user_id = request.form['user_id']
        comment_body = request.form['body']
        conn.execute(
            "INSERT INTO comments (user_id, post_id, body) VALUES (?, ?, ?)",
            (user_id, post_id, comment_body)
        )
        conn.commit()
        flash('Comment added successfully!', 'success')
    
    post = conn.execute("SELECT * FROM blog_posts WHERE post_id = ?", (post_id,)).fetchone()
    comments = conn.execute(
        "SELECT c.body, u.username FROM comments c JOIN users u ON c.user_id = u.user_id WHERE c.post_id = ?",
        (post_id,)
    ).fetchall()
    conn.close()

    if post:
        return render_template('blog_post.html', post=post, comments=comments)
    else:
        flash('Blog post not found!', 'danger')
        return redirect(url_for('blog_posts_page'))

@app.route('/delete_blog_posts')
def delete_blog_posts_page():
    conn = get_db_connection()
    blog_posts = conn.execute("SELECT post_id, title, blog_category, date FROM blog_posts").fetchall()
    conn.close()
    return render_template('delete_blog_post.html', blog_posts=blog_posts)

@app.route('/delete_blog_post/<int:post_id>', methods=['POST'])
def delete_blog_post(post_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM blog_posts WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('delete_blog_posts_page'))

@app.route('/admin')
def admin_index():
    return render_template('admin_index.html')

@app.route('/edit_blog_post', methods=['GET'])
def edit_blog_post():
    conn = get_db_connection()
    blog_posts = conn.execute("SELECT post_id, title, blog_category, date FROM blog_posts").fetchall()
    conn.close()
    return render_template('edit_blog_post.html', blog_posts=blog_posts)

    
@app.route('/edit_blog_post_instance/<int:post_id>', methods=['GET', 'POST'])
def edit_blog_post_instance(post_id):
    conn = get_db_connection()
    if request.method == 'POST':
        user_id = request.form['user_id']
        blog_category = request.form['blog_category']
        title = request.form['title']
        date = request.form['date']
        body = request.form['body']
        blog_type = request.form['blog_type']
        conn.execute(
            "UPDATE blog_posts SET user_id = ?, blog_category = ?, title = ?, date = ?, body = ?, blog_type = ? WHERE post_id = ?",
            (user_id, blog_category, title, date, body, blog_type, post_id)
        )
        conn.commit()
        conn.close()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('edit_blog_post'))
    else:
        post = conn.execute("SELECT * FROM blog_posts WHERE post_id = ?", (post_id,)).fetchone()
        users = conn.execute("SELECT user_id, username FROM users").fetchall()
        conn.close()
        return render_template('edit_blog_post_instance.html', post=post, users=users)

@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    conn = get_db_connection()
    conn.execute("UPDATE blog_posts SET likes = likes + 1 WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()
    flash('You liked the post!', 'success')
    return redirect(url_for('blog_post', post_id=post_id))

@app.route('/dislike_post/<int:post_id>', methods=['POST'])
def dislike_post(post_id):
    conn = get_db_connection()
    conn.execute("UPDATE blog_posts SET dislikes = dislikes + 1 WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()
    flash('You disliked the post!', 'warning')
    return redirect(url_for('blog_post', post_id=post_id))

# User Registration & Authentification
@app.route('/register')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']

    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('index'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert the new user into the database
    cursor.execute("INSERT INTO users (username, password, name) VALUES (?, ?, ?)", (username, password, name))
    conn.commit()

    # Get the ID of the newly created user
    user_id = cursor.lastrowid
    conn.close()

    # Log the user in by storing their ID in the session
    session['user_id'] = user_id

    flash('Registration successful! Welcome to your profile.', 'success')
    return redirect(url_for('profile'))


@app.route('/')
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
    if not user_id:
        flash('Please log in to access your profile.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('profile.html', user_name=user['name'], user_id=user['user_id'])
    else:
        flash('User not found.', 'error')
        return redirect(url_for('register'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)