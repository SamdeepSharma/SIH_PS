from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from nlp.ai_engine import process_query

nlp_bp = Blueprint('nlp', __name__)

@nlp_bp.route('/query', methods=['POST'])
@jwt_required()
def handle_query():
    data = request.get_json()
    query = data.get('query')
    result = process_query(query)
    return jsonify(result), 200
