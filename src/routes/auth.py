from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from src.models.user import User, db
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        phone_number = data.get('phone_number', '').strip()
        
        # Validation
        if not email or not validate_email(email):
            return jsonify({'error': 'Valid email is required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        if phone_number:
            existing_phone = User.query.filter_by(phone_number=phone_number).first()
            if existing_phone:
                return jsonify({'error': 'User with this phone number already exists'}), 409
        
        # Create new user
        user = User(email=email, phone_number=phone_number if phone_number else None)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        print(f"--- Login Attempt ---") # Debug print
        print(f"Received data: {data}") # Debug print

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        print(f"Attempting login for email: {email}") # Debug print
        print(f"Received password: {password}") # Debug print

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"User with email {email} not found in DB.") # Debug print
            return jsonify({'error': 'Invalid email or password'}), 401
        
        print(f"User found: {user.email}") # Debug print
        # Note: Do NOT print the full password hash or actual password in production!
        # This is for debugging only.
        print(f"Stored password hash (first 10 chars): {user.password_hash[:10]}...") # Debug print
        
        # This is the critical line: check_password
        if not user.check_password(password):
            print(f"Password check failed for user {user.email}.") # Debug print
            return jsonify({'error': 'Invalid email or password'}), 401
        
        print(f"Password check successful for user {user.email}!") # Debug print
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Exception during login: {str(e)}") # Debug print
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/login/google', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # In a real implementation, you would verify the Google ID token here
        # For now, we'll simulate this with mock data
        google_id = data.get('google_id')
        email = data.get('email', '').strip().lower()
        
        if not google_id or not email:
            return jsonify({'error': 'Google ID and email are required'}), 400
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if email exists with different auth method
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return jsonify({'error': 'Email already registered with different method'}), 409
            
            # Create new user
            user = User(email=email, google_id=google_id)
            db.session.add(user)
            db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Google login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email or not validate_email(email):
            return jsonify({'error': 'Valid email is required'}), 400
        
        # In a real implementation, you would send a password reset email here
        # For now, we'll just return a success message
        user = User.query.filter_by(email=email).first()
        
        # Always return success to prevent email enumeration
        return jsonify({
            'message': 'If the email exists, a password reset link has been sent'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500