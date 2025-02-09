import sqlite3

# Connect to the database
conn = sqlite3.connect("sql.db")
cursor = conn.cursor()

# Enable foreign keys for referential integrity
cursor.execute("PRAGMA foreign_keys = ON;")

# Create users table (if not exists)
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password TEXT NOT NULL,
                    country TEXT,
                    state TEXT,
                    sex TEXT,
                    profile_pic TEXT DEFAULT 'default.jpg')''')  # Default profile pic

# Create searches table (if not exists)

cursor.execute('''CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    query TEXT NOT NULL,
                    image_url TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user) REFERENCES users(username) ON DELETE CASCADE)''')

# Create rooms table (if not exists)
cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id TEXT UNIQUE NOT NULL,
                    created_by TEXT NOT NULL,
                    FOREIGN KEY (created_by) REFERENCES users(username) ON DELETE CASCADE)''')

# Create room_members table (if not exists)
cursor.execute('''CREATE TABLE IF NOT EXISTS room_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    text TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE)''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        destination TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        transport TEXT NOT NULL,
        budget INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES users(username)
    )
''')

# Commit and close
conn.commit()
conn.close()
print("✅ Database and tables created successfully!")