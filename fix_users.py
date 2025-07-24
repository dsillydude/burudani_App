import sqlite3
import os
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

db_path = os.path.join('src', 'database', 'app.db')

if not os.path.exists(db_path):
    print("❌ Database doesn't exist. Please run the backend server first.")
    exit(1)

print(f"Connecting to database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check current table structure
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("Current users table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check if admin user already exists
    cursor.execute("SELECT * FROM users WHERE email = 'admin@burudani.com'")
    existing_admin = cursor.fetchone()
    
    if existing_admin:
        print("✅ Admin user already exists!")
    else:
        # Create admin user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash('admin123')
        created_at = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO users (id, email, password_hash, first_name, last_name, is_premium, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 'admin@burudani.com', password_hash, 'Admin', 'User', 1, created_at))
        
        print("✅ Admin user created!")
    
    # Check if regular user exists
    cursor.execute("SELECT * FROM users WHERE email = 'user@example.com'")
    existing_user = cursor.fetchone()
    
    if existing_user:
        print("✅ Regular user already exists!")
    else:
        # Create regular user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash('user123')
        created_at = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO users (id, email, password_hash, first_name, last_name, is_premium, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 'user@example.com', password_hash, 'Test', 'User', 0, created_at))
        
        print("✅ Regular user created!")
    
    # Commit changes
    conn.commit()
    
    # Verify users were created
    cursor.execute("SELECT email, first_name, last_name, is_premium FROM users")
    users = cursor.fetchall()
    
    print(f"\n🎉 Database now contains {len(users)} users:")
    for user in users:
        premium_status = "Premium" if user[3] else "Regular"
        print(f"  - {user[0]} ({user[1]} {user[2]}) - {premium_status}")
    
    print("\n✅ Test credentials:")
    print("Email: admin@burudani.com, Password: admin123")
    print("Email: user@example.com, Password: user123")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    conn.close()
