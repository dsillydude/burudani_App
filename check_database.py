import os
import sqlite3
import sys

# Check if database file exists
db_path = os.path.join('src', 'database', 'app.db')
print(f"Checking database at: {db_path}")

if not os.path.exists(db_path):
    print("❌ Database file does not exist!")
    print("The database hasn't been created yet.")
    sys.exit(1)

try:
    # Connect directly to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    users_table = cursor.fetchone()
    
    if not users_table:
        print("❌ Users table doesn't exist!")
        print("Database exists but tables haven't been created.")
    else:
        print("✅ Users table exists!")
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"Found {user_count} users in database")
        
        if user_count > 0:
            # Show all users
            cursor.execute("SELECT email, first_name, last_name FROM users;")
            users = cursor.fetchall()
            print("Users in database:")
            for user in users:
                print(f"  - {user[0]} ({user[1]} {user[2]})")
        else:
            print("⚠️  No users found in database!")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error accessing database: {e}")
