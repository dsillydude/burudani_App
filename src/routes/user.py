from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.content import Content, UserWatchHistory, UserFavorites

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user profile: {str(e)}'}), 500

@user_bp.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update phone number if provided
        phone_number = data.get('phone_number', '').strip()
        if phone_number:
            # Check if phone number is already taken by another user
            existing_phone = User.query.filter(
                User.phone_number == phone_number,
                User.id != current_user_id
            ).first()
            
            if existing_phone:
                return jsonify({'error': 'Phone number already taken'}), 409
            
            user.phone_number = phone_number
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@user_bp.route('/user/history', methods=['GET'])
@jwt_required()
def get_user_history():
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's watch history with content details
        history_query = db.session.query(UserWatchHistory, Content).join(
            Content, UserWatchHistory.content_id == Content.id
        ).filter(UserWatchHistory.user_id == current_user_id).order_by(
            UserWatchHistory.last_watched_at.desc()
        )
        
        history_list = []
        for history, content in history_query.all():
            history_dict = history.to_dict()
            history_dict['content'] = content.to_dict()
            history_list.append(history_dict)
        
        return jsonify(history_list), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get watch history: {str(e)}'}), 500

@user_bp.route('/user/history', methods=['POST'])
@jwt_required()
def add_to_history():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content_id = data.get('content_id')
        watched_duration = data.get('watched_duration', 0)
        
        if not content_id:
            return jsonify({'error': 'content_id is required'}), 400
        
        # Verify content exists
        content = Content.query.get(content_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Check if history entry already exists
        existing_history = UserWatchHistory.query.filter_by(
            user_id=current_user_id,
            content_id=content_id
        ).first()
        
        if existing_history:
            # Update existing entry
            existing_history.watched_duration = watched_duration
            existing_history.last_watched_at = db.func.now()
        else:
            # Create new history entry
            history = UserWatchHistory(
                user_id=current_user_id,
                content_id=content_id,
                watched_duration=watched_duration
            )
            db.session.add(history)
        
        db.session.commit()
        
        return jsonify({'message': 'Watch history updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update watch history: {str(e)}'}), 500

@user_bp.route('/user/favorites', methods=['GET'])
@jwt_required()
def get_user_favorites():
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's favorites with content details
        favorites_query = db.session.query(UserFavorites, Content).join(
            Content, UserFavorites.content_id == Content.id
        ).filter(UserFavorites.user_id == current_user_id).order_by(
            UserFavorites.created_at.desc()
        )
        
        favorites_list = []
        for favorite, content in favorites_query.all():
            content_dict = content.to_dict()
            content_dict['favorited_at'] = favorite.created_at.isoformat()
            favorites_list.append(content_dict)
        
        return jsonify(favorites_list), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get favorites: {str(e)}'}), 500

@user_bp.route('/user/favorites', methods=['POST'])
@jwt_required()
def add_to_favorites():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content_id = data.get('content_id')
        
        if not content_id:
            return jsonify({'error': 'content_id is required'}), 400
        
        # Verify content exists
        content = Content.query.get(content_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Check if already in favorites
        existing_favorite = UserFavorites.query.filter_by(
            user_id=current_user_id,
            content_id=content_id
        ).first()
        
        if existing_favorite:
            return jsonify({'message': 'Content already in favorites'}), 200
        
        # Add to favorites
        favorite = UserFavorites(
            user_id=current_user_id,
            content_id=content_id
        )
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({'message': 'Content added to favorites successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add to favorites: {str(e)}'}), 500

@user_bp.route('/user/favorites/<content_id>', methods=['DELETE'])
@jwt_required()
def remove_from_favorites(content_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Find the favorite entry
        favorite = UserFavorites.query.filter_by(
            user_id=current_user_id,
            content_id=content_id
        ).first()
        
        if not favorite:
            return jsonify({'error': 'Content not in favorites'}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': 'Content removed from favorites successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove from favorites: {str(e)}'}), 500
