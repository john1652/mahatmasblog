from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from forms import RegistrationForm, LoginForm, BlogPostForm, EditBlogPostForm
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/images')
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key-replace-in-production')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max file upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

    form = BlogPostForm()
    if form.validate_on_submit():
        blog_category = form.blog_category.data
        title = form.title.data
        date = form.date.data
        body = form.body.data
        blog_type = form.blog_type.data

        # Insert blog post into the database
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

    return render_template('add_blog_post.html', form=form, user_id=user_id)

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
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to comment.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch the blog post
    cursor.execute("SELECT * FROM blog_posts WHERE post_id = ?", (post_id,))
    post = cursor.fetchone()

    # Fetch comments for the blog post
    cursor.execute("""
        SELECT c.body, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.post_id = ?
    """, (post_id,))
    comments = cursor.fetchall()

    # Fetch the logged-in user's username
    cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    username = user['username']

    if request.method == 'POST':
        body = request.form['body']
        cursor.execute("INSERT INTO comments (user_id, post_id, body) VALUES (?, ?, ?)", (user_id, post_id, body))
        conn.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('blog_post', post_id=post_id))

    conn.close()
    return render_template('blog_post.html', post=post, comments=comments, username=username)

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
    
    # Get all users for the dropdown
    users = conn.execute("SELECT user_id, username FROM users").fetchall()
    
    # Create form and set user choices
    form = EditBlogPostForm()
    form.user_id.choices = [(user['user_id'], user['username']) for user in users]
    
    if request.method == 'GET':
        # Get the current post data
        post = conn.execute("SELECT * FROM blog_posts WHERE post_id = ?", (post_id,)).fetchone()
        if post:
            # Populate form with existing data
            form.user_id.data = post['user_id']
            form.title.data = post['title']
            form.blog_category.data = post['blog_category']
            form.date.data = datetime.strptime(post['date'], '%Y-%m-%d') if post['date'] else None
            form.body.data = post['body']
            form.blog_type.data = post['blog_type']
        else:
            flash('Blog post not found.', 'error')
            return redirect(url_for('edit_blog_post'))
    
    if form.validate_on_submit():
        try:
            conn.execute(
                """UPDATE blog_posts 
                   SET user_id = ?, blog_category = ?, title = ?, 
                       date = ?, body = ?, blog_type = ? 
                   WHERE post_id = ?""",
                (form.user_id.data, form.blog_category.data, form.title.data,
                 form.date.data.strftime('%Y-%m-%d'), form.body.data, 
                 form.blog_type.data, post_id)
            )
            conn.commit()
            flash('Blog post updated successfully!', 'success')
            return redirect(url_for('edit_blog_post'))
        except Exception as e:
            flash(f'Error updating blog post: {str(e)}', 'error')
    
    post = conn.execute("SELECT * FROM blog_posts WHERE post_id = ?", (post_id,)).fetchone()
    conn.close()
    return render_template('edit_blog_post_instance.html', form=form, post=post)

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
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        name = form.name.data
        email = form.email.data

        # Check if username already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, password, name, email) VALUES (?, ?, ?, ?)", 
                      (username, password, name, email))
        conn.commit()

        # Get the ID of the newly created user
        user_id = cursor.lastrowid
        conn.close()

        # Log the user in by storing their ID in the session
        session['user_id'] = user_id
        flash('Registration successful! Welcome to your profile.', 'success')
        return redirect(url_for('profile'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query the database for the user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        # Validate the user
        if user and user['password'] == password:  # Replace with hashed password check in production
            session['user_id'] = user['user_id']
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

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

@app.route('/user_info', methods=['GET', 'POST'])
def user_info():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, password, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('user_info.html', users=users)

@app.route('/view_all_images')
def view_all_images():
    # Get the list of all files in the static/images directory
    image_folder = app.config['UPLOAD_FOLDER']
    images = []
    if os.path.exists(image_folder):
        images = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return render_template('view_all_images.html', images=images)

if __name__ == "__main__":
    app.run(debug=True)