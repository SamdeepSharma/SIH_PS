from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from auth.models import User
from documents.models import Document
from extensions import db
import os

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        content = file.read().decode('utf-8')
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user['email']).first()

        document = Document(user_id=user.id, filename=filename, content=content)
        db.session.add(document)
        db.session.commit()

        return jsonify({"message": "File uploaded successfully"}), 201
    return jsonify({"error": "No file provided"}), 400

@documents_bp.route('/download/<int:document_id>', methods=['GET'])
@jwt_required()
def download_document(document_id):
    document = Document.query.get_or_404(document_id)
    return send_file(document.content, attachment_filename=document.filename)

@documents_bp.route('/link_to_case/<int:document_id>', methods=['POST'])
@jwt_required()
def link_document_to_case(document_id):
    document = Document.query.get_or_404(document_id)
    # Link document content to case logic here (similar to earlier discussed)
    linked_case = link_documents_to_case(document.content, case_database={})
    
    if linked_case:
        return jsonify({"linked_case": linked_case}), 200
    return jsonify({"message": "No case linked"}), 200
