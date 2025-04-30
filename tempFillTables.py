import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Insert sample data into users table
cursor.execute("INSERT INTO users (name, password, username) VALUES (?, ?, ?)",
               ('Jordan Love', 'password123', 'jordan_love'))
cursor.execute("INSERT INTO users (name, password, username) VALUES (?, ?,  ?)",
               ('James Harden',  'securepass', 'james_harden'))
cursor.execute("INSERT INTO users (name, password, username) VALUES (?, ?,  ?)",
               ('LeBron James', 'kingjames', 'lebron_james'))

# Insert sample data into blog_posts table
cursor.execute("INSERT INTO blog_posts (user_id, blog_category, title, body, blog_type) VALUES (?, ?, ?, ?, ?)",
               (3, 'Top 10s', 'Top 10 Hidden Gems in the World', 'Discover the most underrated travel destinations that will blow your mind!', 'published'))
cursor.execute("INSERT INTO blog_posts (user_id, blog_category, title, body, blog_type) VALUES (?, ?, ?, ?, ?)",
               (2, 'John\'s Journeys', 'Lost in Tokyo: A Foodie Adventure', 'Join me as I explore the bustling streets of Tokyo and indulge in the best sushi, ramen, and street food!', 'draft'))
cursor.execute("INSERT INTO blog_posts (user_id, blog_category, title, body, blog_type) VALUES (?, ?, ?, ?, ?)",
               (1, 'Top 10s', 'Top 10 Beaches for the Perfect Sunset', 'These beaches offer the most breathtaking sunsets you’ll ever see. Don’t forget your camera!', 'published'))
cursor.execute("INSERT INTO blog_posts (user_id, blog_category, title, body, blog_type) VALUES (?, ?, ?, ?, ?)",
               (2, 'Moments to Memories', 'Camping Under the Northern Lights', 'A magical night spent under the dancing auroras in the Arctic Circle. Truly unforgettable!', 'draft'))
cursor.execute("INSERT INTO blog_posts (user_id, blog_category, title, body, blog_type) VALUES (?, ?, ?, ?, ?)",
               (3, 'John\'s Journeys', 'Surviving the Amazon: A Wild Adventure', 'From dodging snakes to spotting rare wildlife, my Amazon journey was nothing short of thrilling!', 'published'))
cursor.execute("INSERT INTO blog_posts (user_id, blog_category, title, body, blog_type) VALUES (?, ?, ?, ?, ?)",
               (1, 'Moments to Memories', 'The Ultimate Family BBQ Picnic', 'A day filled with laughter, grilled burgers, and unforgettable family moments.', 'private'))
cursor.execute("INSERT INTO blog_posts (user_id, blog_category, title, body, blog_type) VALUES (?, ?, ?, ?, ?)",
               (2, 'Top 10s', 'Top 10 Castles Straight Out of a Fairytale', 'Step into a world of magic and wonder with these enchanting castles.', 'published'))
cursor.execute("INSERT INTO blog_posts (user_id, blog_category, title, body, blog_type) VALUES (?, ?, ?, ?, ?)",
               (3, 'Reviews', 'The Great American Road Trip: Coast to Coast', 'From the Golden Gate Bridge to Times Square, here’s my ultimate guide to a cross-country adventure.', 'draft'))

# Insert sample data into comments table
cursor.execute("INSERT INTO comments (user_id, post_id, body) VALUES (?, ?, ?)",
               (3, 3, 'Great post!'))
cursor.execute("INSERT INTO comments (user_id, post_id, body) VALUES (?, ?, ?)",
               (4, 4, 'Very informative!'))


# Commit the changes
conn.commit()

# Retrieve and print all data from each table
print("Users:")
for row in cursor.execute("SELECT * FROM users"):
    print(row)

print("\nBlog Posts:")
for row in cursor.execute("SELECT * FROM blog_posts"):
    print(row)

print("\nComments:")
for row in cursor.execute("SELECT * FROM comments"):
    print(row)

print("\nAttachments:")
for row in cursor.execute("SELECT * FROM attachments"):
    print(row)

# Close the connection
conn.close()