from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from auth.models import User

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/user', methods=['GET'])
@jwt_required()
def user_dashboard():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "username": user.username,
        "email": user.email,
        "kyc_verified": user.kyc_verified
    }
    return jsonify(user_data), 200
