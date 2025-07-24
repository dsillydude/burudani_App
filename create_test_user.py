import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models import User, db
from main import create_app

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"Found {len(users)} users in database:")
    for user in users:
        print(f"- {user.email}")
