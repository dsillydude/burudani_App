import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import main
    print("Available functions/classes in main.py:")
    for item in dir(main):
        if not item.startswith('_'):
            print(f"  - {item}")
    
    # Try to find the Flask app
    if hasattr(main, 'app'):
        print(f"\nFound Flask app: {main.app}")
        app = main.app
    elif hasattr(main, 'create_app'):
        print(f"\nFound create_app function")
        app = main.create_app()
    else:
        print("\n❌ No Flask app or create_app function found")
        exit(1)
        
    # Test app context
    with app.app_context():
        from models import User, db
        users = User.query.all()
        print(f"Users in database: {len(users)}")
        
except Exception as e:
    print(f"Error inspecting app: {e}")
    import traceback
    traceback.print_exc()
