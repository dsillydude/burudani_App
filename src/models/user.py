# burudani_backend/src/models/user.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for Google sign-in users
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        # Debug prints for set_password
        print(f"DEBUG (set_password): Input password type: {type(password)}, value: '{password}'")
        encoded_password = password.encode('utf-8')
        print(f"DEBUG (set_password): Encoded password type: {type(encoded_password)}, value: '{encoded_password}'")
        hashed_bytes = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
        print(f"DEBUG (set_password): Hashed bytes type: {type(hashed_bytes)}, value: '{hashed_bytes}'")
        self.password_hash = hashed_bytes.decode('utf-8')
        print(f"DEBUG (set_password): Stored password_hash type: {type(self.password_hash)}, value: '{self.password_hash[:20]}...'") # Print first 20 chars

    def check_password(self, password):
        # Debug prints for check_password
        print(f"DEBUG (check_password): Input password type: {type(password)}, value: '{password}'")
        print(f"DEBUG (check_password): Stored password_hash type: {type(self.password_hash)}, value: '{self.password_hash[:20]}...'") # Print first 20 chars

        if not self.password_hash:
            print("DEBUG (check_password): No password_hash stored for user.")
            return False
        
        # Ensure both are bytes for bcrypt.checkpw
        encoded_input_password = password.encode('utf-8')
        encoded_stored_hash = self.password_hash.encode('utf-8')

        print(f"DEBUG (check_password): Encoded input password: '{encoded_input_password}'")
        print(f"DEBUG (check_password): Encoded stored hash: '{encoded_stored_hash}'")

        try:
            result = bcrypt.checkpw(encoded_input_password, encoded_stored_hash)
            print(f"DEBUG (check_password): bcrypt.checkpw result: {result}")
            return result
        except ValueError as e:
            print(f"DEBUG (check_password): ValueError during bcrypt.checkpw: {e}")
            print("DEBUG (check_password): This often means the stored hash is malformed or not a bcrypt hash.")
            return False


    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone_number': self.phone_number,
            'google_id': self.google_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_admin': self.email == 'admin@burudani.com', # Added this back for frontend
            'username': self.email.split('@')[0] # Added this back for frontend
        }