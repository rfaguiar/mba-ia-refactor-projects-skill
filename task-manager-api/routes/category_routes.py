from flask import Blueprint

from controllers import category_controller as c

category_bp = Blueprint('categories', __name__)

category_bp.add_url_rule('/categories', view_func=c.list_categories, methods=['GET'])
category_bp.add_url_rule('/categories', view_func=c.create_category, methods=['POST'])
category_bp.add_url_rule('/categories/<int:category_id>', view_func=c.update_category, methods=['PUT'])
category_bp.add_url_rule('/categories/<int:category_id>', view_func=c.delete_category, methods=['DELETE'])
