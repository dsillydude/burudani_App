from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.content import Content, Stream, db
import hashlib
import time
import json

streaming_bp = Blueprint('streaming', __name__)

def generate_mock_drm_token(stream_url, channel_id, user_id):
    """Generate a mock DRM token based on the provided parameters"""
    # Create a hash based on the input parameters and current time
    token_data = f"{stream_url}:{channel_id}:{user_id}:{int(time.time() // 300)}"  # 5-minute window
    token_hash = hashlib.sha256(token_data.encode()).hexdigest()
    
    # Create a mock token structure similar to what might be expected
    mock_token = {
        'token': f"nv-auth-{token_hash[:32]}",
        'expires_at': int(time.time()) + 3600,  # 1 hour from now
        'license_url': 'https://azy4sj9b.anycast.nagra.com/TENANTID/wvls/contentlicenseservice/v1/licenses',
        'headers': {
            'nv-authorizations': f"nv-auth-{token_hash[:32]}",
            'Referer': 'app.burudanimax.com',
            'User-Agent': 'BurudaniApp/1.0.0'
        }
    }
    
    return mock_token

@streaming_bp.route('/stream/link', methods=['POST'])
@jwt_required()
def get_stream_link():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content_id = data.get('content_id')
        channel_id = data.get('channel_id')  # For backward compatibility
        
        if not content_id and not channel_id:
            return jsonify({'error': 'content_id or channel_id is required'}), 400
        
        # If channel_id is provided, try to find content by channel_id in streams
        if channel_id and not content_id:
            stream = Stream.query.filter_by(channel_id=channel_id).first()
            if stream:
                content_id = stream.content_id
        
        if not content_id:
            return jsonify({'error': 'Content not found'}), 404
        
        # Get content and its streams
        content = Content.query.get(content_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Get the primary stream (first one for now)
        stream = Stream.query.filter_by(content_id=content_id).first()
        if not stream:
            return jsonify({'error': 'No stream available for this content'}), 404
        
        # Simulate the API response structure from the tutorial
        response_data = {
            'streamURLAndroid': stream.stream_url,
            'stream_type': stream.stream_type,
            'channel_id': stream.channel_id or content_id,
            'content': content.to_dict()
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get stream link: {str(e)}'}), 500

@streaming_bp.route('/stream/drm-token', methods=['POST'])
@jwt_required()
def get_drm_token():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        stream_url = data.get('stream_url')
        content_id = data.get('content_id')
        channel_id = data.get('channel_id')
        
        if not stream_url:
            return jsonify({'error': 'stream_url is required'}), 400
        
        if not content_id and not channel_id:
            return jsonify({'error': 'content_id or channel_id is required'}), 400
        
        # Generate mock DRM token
        drm_token_data = generate_mock_drm_token(
            stream_url, 
            channel_id or content_id, 
            current_user_id
        )
        
        # Simulate the API response structure from the tutorial
        response_data = {
            'data': {
                'token': drm_token_data['token'],
                'expires_at': drm_token_data['expires_at'],
                'license_url': drm_token_data['license_url']
            },
            'headers': drm_token_data['headers']
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get DRM token: {str(e)}'}), 500

@streaming_bp.route('/stream/validate', methods=['POST'])
@jwt_required()
def validate_stream():
    """Validate if a user has access to a specific stream"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content_id = data.get('content_id')
        
        if not content_id:
            return jsonify({'error': 'content_id is required'}), 400
        
        # Get content
        content = Content.query.get(content_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Check if content is premium (in a real app, you'd check user subscription)
        if content.is_premium:
            # For now, we'll allow access to premium content
            # In a real implementation, you'd check user subscription status
            pass
        
        return jsonify({
            'valid': True,
            'content': content.to_dict(),
            'message': 'Stream access granted'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Stream validation failed: {str(e)}'}), 500

