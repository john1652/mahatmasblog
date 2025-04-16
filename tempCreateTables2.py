import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Users Table

cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('DROP TABLE IF EXISTS blog_posts')
cursor.execute('DROP TABLE IF EXISTS comments')
cursor.execute('DROP TABLE IF EXISTS attachments')



cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    password TEXT NOT NULL,
                    profile_image TEXT, -- Path to the image file
                    username TEXT NOT NULL
                )''')

# Blog Posts Table
cursor.execute('''CREATE TABLE IF NOT EXISTS blog_posts (
                    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    blog_category TEXT CHECK(blog_category IN ('Top 10s', 'John''s Journeys', 'Moments to Memories', 'Reviews') OR blog_category IS NULL),
                    title TEXT NOT NULL,
                    date TEXT DEFAULT CURRENT_TIMESTAMP, -- Automatically records the current date and time
                    body TEXT NOT NULL,
                    blog_type TEXT,
                    likes INTEGER DEFAULT 0, -- New column for likes
                    dislikes INTEGER DEFAULT 0, -- New column for dislikes
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )''')

# Comments Table
cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    post_id INTEGER NOT NULL,
                    datetime TEXT DEFAULT CURRENT_TIMESTAMP, -- Automatically records the current date and time
                    body TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (post_id) REFERENCES blog_posts(post_id)
                )''')

# Attachments Table
cursor.execute('''CREATE TABLE IF NOT EXISTS attachments (
                    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    attachment_type TEXT, -- Type of the attachment (e.g., image, video, document)
                    attachment_file TEXT, -- Path to the attachment file
                    FOREIGN KEY (post_id) REFERENCES blog_posts(post_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )''')

# Check if 'likes' column exists, and add it if not
cursor.execute("PRAGMA table_info(blog_posts)")
columns = [column[1] for column in cursor.fetchall()]
if 'likes' not in columns:
    cursor.execute('ALTER TABLE blog_posts ADD COLUMN likes INTEGER DEFAULT 0')

# Check if 'dislikes' column exists, and add it if not
if 'dislikes' not in columns:
    cursor.execute('ALTER TABLE blog_posts ADD COLUMN dislikes INTEGER DEFAULT 0')

conn.commit()
conn.close()