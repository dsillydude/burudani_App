from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Content(db.Model):
    __tablename__ = 'content'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50), nullable=False)  # 'movie', 'live_tv', 'sport'
    thumbnail_url = db.Column(db.String(255))
    cover_image_url = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    duration = db.Column(db.Integer)  # Duration in minutes
    is_premium = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_trending = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    streams = db.relationship('Stream', backref='content', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', secondary='content_categories', back_populates='content')
    
    def __repr__(self):
        return f'<Content {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'thumbnail_url': self.thumbnail_url,
            'cover_image_url': self.cover_image_url,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'duration': self.duration,
            'is_premium': self.is_premium,
            'is_featured': self.is_featured,
            'is_trending': self.is_trending,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'categories': [category.to_dict() for category in self.categories],
            'streams': [stream.to_dict() for stream in self.streams]
        }

class Stream(db.Model):
    __tablename__ = 'streams'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = db.Column(db.String(36), db.ForeignKey('content.id'), nullable=False)
    stream_url = db.Column(db.Text, nullable=False)
    stream_type = db.Column(db.String(50), nullable=False)  # 'normal', 'hls', 'drm'
    channel_id = db.Column(db.String(255))
    drm_license_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Stream {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content_id': self.content_id,
            'stream_url': self.stream_url,
            'stream_type': self.stream_type,
            'channel_id': self.channel_id,
            'drm_license_url': self.drm_license_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content = db.relationship('Content', secondary='content_categories', back_populates='categories')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Junction table for many-to-many relationship between Content and Category
content_categories = db.Table('content_categories',
    db.Column('content_id', db.String(36), db.ForeignKey('content.id'), primary_key=True),
    db.Column('category_id', db.String(36), db.ForeignKey('categories.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

class UserWatchHistory(db.Model):
    __tablename__ = 'user_watch_history'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content_id = db.Column(db.String(36), db.ForeignKey('content.id'), nullable=False)
    watched_duration = db.Column(db.Integer, default=0)  # Duration in seconds
    last_watched_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserWatchHistory {self.user_id}:{self.content_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'watched_duration': self.watched_duration,
            'last_watched_at': self.last_watched_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UserFavorites(db.Model):
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content_id = db.Column(db.String(36), db.ForeignKey('content.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique user-content combination
    __table_args__ = (db.UniqueConstraint('user_id', 'content_id', name='unique_user_content_favorite'),)
    
    def __repr__(self):
        return f'<UserFavorites {self.user_id}:{self.content_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

