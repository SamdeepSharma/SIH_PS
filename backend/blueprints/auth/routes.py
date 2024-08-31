from flask import Blueprint, request, jsonify
from extensions import db
from auth.models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity={'email': user.email})
        return jsonify(access_token=access_token), 200
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/kyc', methods=['POST'])
def kyc_verification():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.kyc_verified = True
    db.session.commit()
    return jsonify({"message": "KYC verified successfully"}), 200
