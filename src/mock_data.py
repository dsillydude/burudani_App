import json
import random
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add the parent directory to the path to import from src
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import User, db
from src.models.content import Content, Category, UserFavorites, UserWatchHistory, Stream
from src.main import app

# Mock data for categories
CATEGORIES = [
    {"name": "Action", "description": "Action-packed movies and shows"},
    {"name": "Comedy", "description": "Funny movies and shows"},
    {"name": "Drama", "description": "Dramatic content"},
    {"name": "Horror", "description": "Scary movies and shows"},
    {"name": "Romance", "description": "Romantic content"},
    {"name": "Sci-Fi", "description": "Science fiction content"},
    {"name": "Documentary", "description": "Educational documentaries"},
    {"name": "Sports", "description": "Sports content and events"},
    {"name": "News", "description": "News and current affairs"},
    {"name": "Kids", "description": "Content for children"},
]

# Mock content data
MOCK_CONTENT = [
    # Movies
    {
        "title": "The Lion King",
        "description": "A young lion prince flees his kingdom only to learn the true meaning of responsibility and bravery.",
        "type": "movie",
        "category": "Kids",
        "duration": 118,
        "release_date": "2019-07-19",
        "is_premium": False,
        "is_featured": True,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMjIwMjE1Nzc4NV5BMl5BanBnXkFtZTgwNDg4OTA1NzM@._V1_.jpg",
        "cover_image_url": "https://images.hdqwalls.com/wallpapers/the-lion-king-2019-movie-4k-ej.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    },
    {
        "title": "Black Panther",
        "description": "T'Challa, heir to the hidden but advanced kingdom of Wakanda, must step forward to lead his people into a new future.",
        "type": "movie",
        "category": "Action",
        "duration": 134,
        "release_date": "2018-02-16",
        "is_premium": True,
        "is_featured": True,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMTg1MTY2MjYzNV5BMl5BanBnXkFtZTgwMTc4NTMwNDI@._V1_.jpg",
        "cover_image_url": "https://wallpaperaccess.com/full/1074507.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
    },
    {
        "title": "Avengers: Endgame",
        "description": "After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos' actions.",
        "type": "movie",
        "category": "Action",
        "duration": 181,
        "release_date": "2019-04-26",
        "is_premium": True,
        "is_featured": True,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_.jpg",
        "cover_image_url": "https://wallpapercave.com/wp/wp4056410.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    },
    {
        "title": "Joker",
        "description": "A failed comedian begins his slow descent into madness as he transforms into the criminal mastermind known as the Joker.",
        "type": "movie",
        "category": "Drama",
        "duration": 122,
        "release_date": "2019-10-04",
        "is_premium": True,
        "is_featured": False,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BNGVjNWI4ZGUtNzE0MS00YTJmLWE0ZDctN2ZiYTk2YmI3NTYyXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_.jpg",
        "cover_image_url": "https://wallpapercave.com/wp/wp4678226.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
    },
    {
        "title": "Parasite",
        "description": "A poor family schemes to become employed by a wealthy family by infiltrating their household.",
        "type": "movie",
        "category": "Drama",
        "duration": 132,
        "release_date": "2019-05-30",
        "is_premium": True,
        "is_featured": False,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BYWZjMjk3ZTItODQ2ZC00NTY5LWE0ZDYtZTI3MjcwN2Q5NTVkXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1_.jpg",
        "cover_image_url": "https://wallpapercave.com/wp/wp5750508.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
    },
    
    # TV Shows
    {
        "title": "Stranger Things",
        "description": "When a young boy disappears, his mother, a police chief and his friends must confront terrifying supernatural forces.",
        "type": "tv_show",
        "category": "Sci-Fi",
        "duration": 50,
        "release_date": "2016-07-15",
        "is_premium": True,
        "is_featured": True,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BN2ZmYjg1YmItNWQ4OC00YWM0LWE0ZDktYThjOTZiZjhhN2Q2XkEyXkFqcGdeQXVyNjgxNTQ3Mjk@._V1_.jpg",
        "cover_image_url": "https://wallpapercave.com/wp/wp2002478.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4"
    },
    {
        "title": "The Office",
        "description": "A mockumentary on a group of typical office workers, where the workday consists of ego clashes and inappropriate behavior.",
        "type": "tv_show",
        "category": "Comedy",
        "duration": 22,
        "release_date": "2005-03-24",
        "is_premium": False,
        "is_featured": False,
        "thumbnail_url": "https://m.media-amazon.com/images/M/MV5BMDNkOTE4NDQtMTNmYi00MWE0LWE4ZTktYTc0NzhhNWIzNzJiXkEyXkFqcGdeQXVyMzQ2MDI5NjU@._V1_.jpg",
        "cover_image_url": "https://wallpapercave.com/wp/wp2446876.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4"
    },
    
    # Live TV Channels
    {
        "title": "CNN International",
        "description": "24-hour international news channel",
        "type": "live_tv",
        "category": "News",
        "duration": 0,
        "release_date": "1985-06-01",
        "is_premium": False,
        "is_featured": True,
        "thumbnail_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/CNN.svg/1200px-CNN.svg.png",
        "cover_image_url": "https://wallpapercave.com/wp/wp2446876.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
    },
    {
        "title": "ESPN",
        "description": "Sports entertainment programming network",
        "type": "live_tv",
        "category": "Sports",
        "duration": 0,
        "release_date": "1979-09-07",
        "is_premium": True,
        "is_featured": True,
        "thumbnail_url": "https://logoeps.com/wp-content/uploads/2013/03/espn-vector-logo.png",
        "cover_image_url": "https://wallpapercave.com/wp/wp2446876.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4"
    },
    
    # Sports Content
    {
        "title": "Premier League Highlights",
        "description": "Best moments from the English Premier League",
        "type": "sport",
        "category": "Sports",
        "duration": 45,
        "release_date": "2024-01-15",
        "is_premium": True,
        "is_featured": True,
        "thumbnail_url": "https://logos-world.net/wp-content/uploads/2020/06/Premier-League-Logo.png",
        "cover_image_url": "https://wallpapercave.com/wp/wp2446876.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
    },
    {
        "title": "UEFA Champions League",
        "description": "Europe's premier club football competition",
        "type": "sport",
        "category": "Sports",
        "duration": 90,
        "release_date": "2024-02-20",
        "is_premium": True,
        "is_featured": True,
        "thumbnail_url": "https://logoeps.com/wp-content/uploads/2013/03/uefa-champions-league-vector-logo.png",
        "cover_image_url": "https://wallpapercave.com/wp/wp2446876.jpg",
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4"
    },
]

# Mock users
MOCK_USERS = [
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
    },
    {
        "email": "premium@example.com",
        "password": "premium123",
        "phone_number": "+255555666777",
        "is_premium": True
    }
]

def create_mock_data():
    """Create mock data for the application"""
    with app.app_context():
        # Import all models to ensure they're registered
        from src.models.user import User
        from src.models.content import Content, Category, UserFavorites, UserWatchHistory, Stream
        
        # Clear existing data and recreate tables
        db.drop_all()
        db.create_all()
        
        print("Creating categories...")
        # Create categories
        categories = {}
        for cat_data in CATEGORIES:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.session.add(category)
            db.session.flush()
            categories[cat_data["name"]] = category.id
        
        print("Creating users...")
        # Create users
        users = []
        for user_data in MOCK_USERS:
            user = User(
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),
                phone_number=user_data.get("phone_number"),
                is_premium=user_data.get("is_premium", False),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()
            users.append(user)
        
        print("Creating content...")
        # Create content
        content_items = []
        for content_data in MOCK_CONTENT:
            content = Content(
                title=content_data["title"],
                description=content_data["description"],
                type=content_data["type"],
                duration=content_data.get("duration"),
                release_date=datetime.strptime(content_data["release_date"], "%Y-%m-%d").date() if content_data.get("release_date") else None,
                is_premium=content_data.get("is_premium", False),
                is_featured=content_data.get("is_featured", False),
                thumbnail_url=content_data.get("thumbnail_url"),
                cover_image_url=content_data.get("cover_image_url"),
                created_at=datetime.utcnow()
            )
            db.session.add(content)
            db.session.flush()
            
            # Add category relationship
            if content_data.get("category") and content_data["category"] in categories:
                category = Category.query.get(categories[content_data["category"]])
                if category:
                    content.categories.append(category)
            
            # Add stream data
            if content_data.get("stream_url"):
                stream = Stream(
                    content_id=content.id,
                    stream_url=content_data["stream_url"],
                    stream_type="normal"
                )
                db.session.add(stream)
            
            content_items.append(content)
        
        print("Creating user favorites and history...")
        # Create some user favorites and history
        for user in users:
            # Add random favorites
            favorite_content = random.sample(content_items, min(3, len(content_items)))
            for content in favorite_content:
                favorite = UserFavorites(
                    user_id=user.id,
                    content_id=content.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(favorite)
            
            # Add random watch history
            history_content = random.sample(content_items, min(5, len(content_items)))
            for content in history_content:
                history = UserWatchHistory(
                    user_id=user.id,
                    content_id=content.id,
                    watched_duration=random.randint(60, content.duration * 60 if content.duration else 3600),
                    last_watched_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(history)
        
        # Commit all changes
        db.session.commit()
        print("Mock data created successfully!")
        
        # Print summary
        print(f"Created {len(CATEGORIES)} categories")
        print(f"Created {len(MOCK_USERS)} users")
        print(f"Created {len(MOCK_CONTENT)} content items")
        print("\nTest users:")
        for user_data in MOCK_USERS:
            print(f"  Email: {user_data['email']}, Password: {user_data['password']}")

if __name__ == "__main__":
    create_mock_data()

