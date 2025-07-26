# burudani_backend/src/routes/payments.py

import os
import uuid
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User

payments_bp = Blueprint('payments', __name__)

# Zeno API Configuration
ZENO_API_URL = "https://zenoapi.com/api/payments/mobile_money_tanzania"
ZENO_API_KEY = "ELyri3n4iLR6nqwixrwkjefTBFuxHSWlbho-esVC4fHYrQeZ4fKlOXa91MVrPfjI3nAYvmZO842Nle37tsK3lw"
ZENO_ORDER_STATUS_URL = "https://zenoapi.com/api/payments/order-status"

# Payment model (you might want to create a separate model file for this)
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='TZS')
    payment_status = db.Column(db.String(20), default='PENDING')
    payment_method = db.Column(db.String(20), default='ZENO_USSD')
    buyer_phone = db.Column(db.String(15), nullable=False)
    buyer_email = db.Column(db.String(100), nullable=False)
    buyer_name = db.Column(db.String(100), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    channel = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('payments', lazy=True))
    
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

@payments_bp.route('/payments/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    """Initiate a Zeno PUSH USSD payment"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'buyer_phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate unique order ID
        order_id = str(uuid.uuid4())
        
        # Prepare payment data for Zeno API
        payment_data = {
            "order_id": order_id,
            "buyer_email": data.get('buyer_email', user.email),
            "buyer_name": data.get('buyer_name', f"{user.email.split('@')[0]}"),
            "buyer_phone": data['buyer_phone'],
            "amount": int(data['amount'])  # Ensure amount is integer
        }
        
        # Add webhook URL if available
        webhook_url = data.get('webhook_url')
        if webhook_url:
            payment_data['webhook_url'] = webhook_url
        
        # Create payment record in database
        payment = Payment(
            order_id=order_id,
            user_id=current_user_id,
            amount=float(data['amount']),
            buyer_phone=data['buyer_phone'],
            buyer_email=payment_data['buyer_email'],
            buyer_name=payment_data['buyer_name'],
            payment_status='PENDING'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Make request to Zeno API
        headers = {
            "x-api-key": ZENO_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            ZENO_API_URL,
            headers=headers,
            json=payment_data,
            timeout=30
        )
        
        if response.status_code == 200:
            zeno_response = response.json()
            
            # Update payment record with Zeno response
            payment.payment_status = 'INITIATED'
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Payment initiated successfully',
                'order_id': order_id,
                'zeno_response': zeno_response,
                'payment': payment.to_dict()
            }), 200
        else:
            # Update payment status to failed
            payment.payment_status = 'FAILED'
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': 'Failed to initiate payment with Zeno',
                'details': response.text
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@payments_bp.route('/payments/status/<order_id>', methods=['GET'])
@jwt_required()
def check_payment_status(order_id):
    """Check payment status from both local database and Zeno API"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get payment from local database
        payment = Payment.query.filter_by(order_id=order_id, user_id=current_user_id).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Check status from Zeno API
        headers = {
            "x-api-key": ZENO_API_KEY
        }
        
        response = requests.get(
            f"{ZENO_ORDER_STATUS_URL}?order_id={order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            zeno_response = response.json()
            
            # Update local payment record if status changed
            if 'data' in zeno_response and zeno_response['data']:
                payment_data = zeno_response['data'][0]
                
                if payment_data.get('payment_status') != payment.payment_status:
                    payment.payment_status = payment_data.get('payment_status', payment.payment_status)
                    payment.transaction_id = payment_data.get('transid')
                    payment.reference = payment_data.get('reference')
                    payment.channel = payment_data.get('channel')
                    payment.updated_at = datetime.utcnow()
                    db.session.commit()
            
            return jsonify({
                'success': True,
                'payment': payment.to_dict(),
                'zeno_response': zeno_response
            }), 200
        else:
            return jsonify({
                'success': True,
                'payment': payment.to_dict(),
                'zeno_error': response.text
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@payments_bp.route('/payments/webhook', methods=['POST'])
def payment_webhook():
    """Handle Zeno payment webhook notifications"""
    try:
        # Verify API key from header
        api_key = request.headers.get('x-api-key')
        if api_key != ZENO_API_KEY:
            return jsonify({'error': 'Invalid API key'}), 403
        
        data = request.get_json()
        
        if not data or 'order_id' not in data:
            return jsonify({'error': 'Invalid webhook payload'}), 400
        
        order_id = data['order_id']
        payment_status = data.get('payment_status', 'UNKNOWN')
        reference = data.get('reference')
        metadata = data.get('metadata', {})
        
        # Find and update payment record
        payment = Payment.query.filter_by(order_id=order_id).first()
        
        if payment:
            payment.payment_status = payment_status
            payment.reference = reference
            payment.updated_at = datetime.utcnow()
            
            # Store metadata if needed
            if metadata:
                # You might want to add a metadata column to store this
                pass
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Webhook processed successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Payment not found',
                'order_id': order_id
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Webhook processing error: {str(e)}'}), 500

@payments_bp.route('/payments/user', methods=['GET'])
@jwt_required()
def get_user_payments():
    """Get all payments for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        payments = Payment.query.filter_by(user_id=current_user_id).order_by(Payment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'payments': [payment.to_dict() for payment in payments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@payments_bp.route('/payments/verify-pin', methods=['POST'])
@jwt_required()
def verify_payment_pin():
    """Verify PIN for payment authorization"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        pin = data.get('pin')
        
        if not pin:
            return jsonify({'error': 'PIN is required'}), 400
        
        # For now, we'll use a simple PIN verification
        # You can implement your own PIN logic here
        # This is a placeholder - replace with your actual PIN verification
        if pin == "1234":  # Default PIN for demo
            return jsonify({
                'success': True,
                'message': 'PIN verified successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid PIN'
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

