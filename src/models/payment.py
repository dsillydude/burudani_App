# burudani_backend/src/models/payment.py

from datetime import datetime
from uuid import uuid4
from sqlalchemy.schema import ForeignKey
from sqlalchemy import Integer, String, Float, DateTime, Boolean # Import types
from .user import db # Import db from user model, assuming it's the main db instance

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True) # SERIAL NOT NULL corresponds to Integer in SQLAlchemy
    order_id = db.Column(db.String(100), unique=True, nullable=False)
    
    # FIX: Change user_id type to String to match User.id type
    user_id = db.Column(db.String(36), ForeignKey('users.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='TZS') # Default currency
    payment_status = db.Column(db.String(20), default='PENDING') # PENDING, INITIATED, COMPLETED, FAILED, CANCELLED, EXPIRED
    payment_method = db.Column(db.String(20), default='MOBILE_MONEY') # MOBILE_MONEY, CARD, PIN
    
    # Buyer info from payment request
    buyer_phone = db.Column(db.String(15), nullable=False)
    buyer_email = db.Column(db.String(100), nullable=False)
    buyer_name = db.Column(db.String(100), nullable=False)
    
    # ZenoPay specific fields
    transaction_id = db.Column(db.String(100)) # ZenoPay's transid
    reference = db.Column(db.String(100))      # ZenoPay's reference
    channel = db.Column(db.String(20))         # e.g., MPESA-TZ, TIGO-TZ
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User (optional, for easier querying from Payment side)
    user = db.relationship('User', backref='payments', lazy=True) # 'User' is class name from user.py

    def __repr__(self):
        return f"<Payment {self.order_id} - {self.payment_status}>"

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'buyer_phone': self.buyer_phone,
            'buyer_email': self.buyer_email,
            'buyer_name': self.buyer_name,
            'transaction_id': self.transaction_id,
            'reference': self.reference,
            'channel': self.channel,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }