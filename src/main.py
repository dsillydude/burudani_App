# burudani_backend/src/main.py

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db, User # Import User model as well
from src.models.content import Content, Stream, Category, UserWatchHistory, UserFavorites
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.content import content_bp
from src.routes.streaming import streaming_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize JWT
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(content_bp, url_prefix='/api')
app.register_blueprint(streaming_bp, url_prefix='/api')

# Database configuration
# Use DATABASE_URL environment variable for production (Render), fallback to SQLite for local
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Function to create or update admin user (remains from previous debug)
def create_admin_user_on_startup():
    with app.app_context():
        print("--- Checking/Creating Admin User ---")
        admin_email = 'admin@burudani.com'
        admin_password = 'admin123'

        user = User.query.filter_by(email=admin_email).first()
        if not user:
            print(f"Admin user '{admin_email}' not found. Creating...")
            admin_user = User(email=admin_email, phone_number='1234567890') # Add dummy phone
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user '{admin_email}' created successfully!")
        else:
            print(f"Admin user '{admin_email}' already exists.")
        print("--- Admin User Check Complete ---")

# Hook to run code after app context is pushed
@app.before_first_request
def create_db_and_admin():
    db.create_all() # Create all database tables
    create_admin_user_on_startup() # Ensure admin user exists

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'message': 'Burudani Backend API is running'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)