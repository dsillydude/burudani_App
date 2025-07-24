import os
import sys
import json
from werkzeug.security import generate_password_hash

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_database():
    try:
        # Import after adding src to path
        from main import create_app
        from models import db, User, Category, Content
        
        print("Creating Flask app...")
        app = create_app()
        
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            
            # Check if users already exist
            existing_users = User.query.count()
            if existing_users > 0:
                print(f"Database already has {existing_users} users. Skipping user creation.")
                return
            
            print("Creating sample users...")
            
            # Create admin user
            admin_user = User(
                email='admin@burudani.com',
                password_hash=generate_password_hash('admin123'),
                first_name='Admin',
                last_name='User',
                is_premium=True
            )
            
            # Create regular user
            regular_user = User(
                email='user@example.com',
                password_hash=generate_password_hash('user123'),
                first_name='Test',
                last_name='User',
                is_premium=False
            )
            
            db.session.add(admin_user)
            db.session.add(regular_user)
            
            # Load and create categories if they exist
            categories_file = os.path.join('sample_data', 'categories.json')
            if os.path.exists(categories_file):
                print("Loading categories...")
                with open(categories_file, 'r') as f:
                    categories_data = json.load(f)
                    
                for cat_data in categories_data:
                    category = Category(
                        id=cat_data['id'],
                        name=cat_data['name'],
                        description=cat_data.get('description', '')
                    )
                    db.session.add(category)
            
            # Load and create content if it exists
            content_file = os.path.join('sample_data', 'content.json')
            if os.path.exists(content_file):
                print("Loading content...")
                with open(content_file, 'r') as f:
                    content_data = json.load(f)
                    
                for content_item in content_data:
                    content = Content(
                        id=content_item['id'],
                        title=content_item['title'],
                        description=content_item.get('description', ''),
                        type=content_item.get('type', 'movie'),
                        category=content_item.get('category', ''),
                        duration=content_item.get('duration', 0),
                        is_premium=content_item.get('is_premium', False),
                        is_featured=content_item.get('is_featured', False),
                        thumbnail_url=content_item.get('thumbnail_url', ''),
                        cover_image_url=content_item.get('cover_image_url', ''),
                        stream_url=content_item.get('stream_url', '')
                    )
                    db.session.add(content)
            
            # Commit all changes
            db.session.commit()
            print("✅ Database setup completed successfully!")
            
            # Verify users were created
            users = User.query.all()
            print(f"Created {len(users)} users:")
            for user in users:
                print(f"  - {user.email}")
                
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    setup_database()
