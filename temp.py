import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Query to fetch all users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

# Print all users
print("Users:")
for user in users:
    print(user)

# Close the connection
conn.close()

