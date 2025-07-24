# burudani_backend/verify_database.py
import sys
import os

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import necessary components
# The 'app' imported from main.py already has db.init_app(app) called on it.
from main import app as flask_app 
from models.user import db, User # Import db (SQLAlchemy instance) and User model

# We no longer need db.init_app(flask_app) here, as it's already done in main.py
# The error "A 'SQLAlchemy' instance has already been registered" confirms this.

with flask_app.app_context():
    try:
        # Query for users
        users = User.query.all()
        print(f"Found {len(users)} users in database:")
        if len(users) == 0:
            print("- No users found. This might indicate that sample data was not loaded.")
        for user in users:
            # Check if password_hash is not None before slicing
            password_hash_display = user.password_hash[:20] + '...' if user.password_hash else '[No Hash]'
            print(f"- Email: {user.email}, Password Hash (first 20 chars): {password_hash_display}")
            if user.email == 'admin@burudani.com':
                print(f"  Admin user found!")
    except Exception as e:
        print(f"Error querying database: {e}")
        print("This might indicate that the database tables haven't been created yet, or a connection issue.")