from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.content import Content, Stream, Category, UserWatchHistory, UserFavorites, db
from sqlalchemy import or_, and_

content_bp = Blueprint('content', __name__)

@content_bp.route('/content', methods=['GET'])
@jwt_required()
def get_content():
    try:
        # Get query parameters
        content_type = request.args.get('type')
        category_id = request.args.get('category_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = Content.query
        
        if content_type:
            query = query.filter(Content.type == content_type)
        
        if category_id:
            query = query.join(Content.categories).filter(Category.id == category_id)
        
        # Paginate results
        content_list = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'content': [content.to_dict() for content in content_list.items],
            'total': content_list.total,
            'pages': content_list.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch content: {str(e)}'}), 500

@content_bp.route('/content/<content_id>', methods=['GET'])
@jwt_required()
def get_content_by_id(content_id):
    try:
        content = Content.query.get_or_404(content_id)
        return jsonify(content.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch content: {str(e)}'}), 500

@content_bp.route('/content/featured', methods=['GET'])
@jwt_required()
def get_featured_content():
    try:
        featured_content = Content.query.filter(Content.is_featured == True).all()
        return jsonify([content.to_dict() for content in featured_content]), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch featured content: {str(e)}'}), 500

@content_bp.route('/content/trending', methods=['GET'])
@jwt_required()
def get_trending_content():
    try:
        trending_content = Content.query.filter(Content.is_trending == True).all()
        return jsonify([content.to_dict() for content in trending_content]), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch trending content: {str(e)}'}), 500

@content_bp.route('/content/search', methods=['GET'])
@jwt_required()
def search_content():
    try:
        query_param = request.args.get('query', '').strip()
        
        if not query_param:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Search in title and description
        search_results = Content.query.filter(
            or_(
                Content.title.ilike(f'%{query_param}%'),
                Content.description.ilike(f'%{query_param}%')
            )
        ).all()
        
        return jsonify([content.to_dict() for content in search_results]), 200
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@content_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch categories: {str(e)}'}), 500

@content_bp.route('/categories/<category_id>/content', methods=['GET'])
@jwt_required()
def get_content_by_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        content_list = category.content
        
        return jsonify({
            'category': category.to_dict(),
            'content': [content.to_dict() for content in content_list]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch content by category: {str(e)}'}), 500

