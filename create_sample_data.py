
#!/usr/bin/env python3
"""
Simple script to create sample data for the Burudani app
"""

import json
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import app, db
from models.user import User

# Sample content data (unchanged)
sample_content = [
    {
        "id": "1",
        "title": "The Lion King",
        "description": "A young lion prince flees his kingdom only to learn the true meaning of responsibility and bravery.",
        "type": "movie",
        "category": "Kids",
        "duration": 118,
        "is_premium": False,
        "is_featured": True,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMjIwMjE1Nzc4NV5BMl5BanBnXkFtZTgwNDg4OTA1NzM@._V1_.jpg",
        "cover_image_url": "https://images.hdqwalls.com/wallpapers/the-lion-king-2019-movie-4k-ej.jpg"
    },
    {
        "id": "2",
        "title": "Black Panther",
        "description": "T'Challa, heir to the hidden but advanced kingdom of Wakanda, must step forward to lead his people into a new future.",
        "type": "movie",
        "category": "Action",
        "duration": 134,
        "is_premium": True,
        "is_featured": True,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMTg1MTY2MjYzNV5BMl5BanBnXkFtZTgwMTc4NTMwNDI@._V1_.jpg",
        "cover_image_url": "https://wallpaperaccess.com/full/1074507.jpg"
    },
    {
        "id": "3",
        "title": "CNN International",
        "description": "24-hour international news channel",
        "type": "live_tv",
        "category": "News",
        "duration": 0,
        "is_premium": False,
        "is_featured": True,
        "thumbnail_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/CNN.svg/1200px-CNN.svg.png",
        "cover_image_url": "https://wallpapercave.com/wp/wp2446876.jpg"
    },
    {
        "id": "4",
        "title": "Premier League Highlights",
        "description": "Best moments from the English Premier League",
        "type": "sport",
        "category": "Sports",
        "duration": 45,
        "is_premium": True,
        "is_featured": True,
        "thumbnail_url": "https://logos-world.net/wp-content/uploads/2020/06/Premier-League-Logo.png",
        "cover_image_url": "https://wallpapercave.com/wp/wp2446876.jpg"
    }
]

# Sample categories (unchanged)
sample_categories = [
    {"id": "1", "name": "Action", "description": "Action-packed movies and shows"},
    {"id": "2", "name": "Comedy", "description": "Funny movies and shows"},
    {"id": "3", "name": "Drama", "description": "Dramatic content"},
    {"id": "4", "name": "Sports", "description": "Sports content and events"},
    {"id": "5", "name": "News", "description": "News and current affairs"},
    {"id": "6", "name": "Kids", "description": "Content for children"}
]

# Sample users with passwords for direct DB insertion
sample_users_with_passwords = [
    {
        "email": "admin@burudani.com",
        "password": "admin123",
        "phone_number": "+255123456789",
        "is_premium": True
    },
    {
        "email": "user@example.com",
        "password": "user123",
        "phone_number": "+255987654321",
        "is_premium": False
    }
]

def create_sample_files_and_db_entries():
    """Create JSON files with sample data and populate the database"""
    
    # Create data directory for JSON files
    data_dir = "sample_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Write content data to JSON
    with open(f"{data_dir}/content.json", "w") as f:
        json.dump(sample_content, f, indent=2)
    
    # Write categories data to JSON
    with open(f"{data_dir}/categories.json", "w") as f:
        json.dump(sample_categories, f, indent=2)
    
    # Write users data to JSON (without passwords for security)
    users_for_json = [{
        "id": str(idx + 1),
        "email": user["email"],
        "is_premium": user["is_premium"],
        "phone_number": user["phone_number"]
    } for idx, user in enumerate(sample_users_with_passwords)]
    with open(f"{data_dir}/users.json", "w") as f:
        json.dump(users_for_json, f, indent=2)
    
    print("Sample data JSON files created successfully!")
    print(f"- {data_dir}/content.json ({len(sample_content)} items)")
    print(f"- {data_dir}/categories.json ({len(sample_categories)} items)")
    print(f"- {data_dir}/users.json ({len(users_for_json)} items)")
    
    # Populate database
    with app.app_context():
        # Clear existing users to prevent duplicates on re-run
        db.session.query(User).delete()
        db.session.commit()

        for user_data in sample_users_with_passwords:
            user = User(
                email=user_data["email"],
                phone_number=user_data["phone_number"]
            )
            user.set_password(user_data["password"])
            db.session.add(user)
        
        db.session.commit()
        print("Sample users populated in the database successfully!")
    
    print("\nTest credentials:")
    print("Email: admin@burudani.com, Password: admin123")
    print("Email: user@example.com, Password: user123")

if __name__ == "__main__":
    create_sample_files_and_db_entries()


