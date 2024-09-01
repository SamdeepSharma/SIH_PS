"""Routes for the documents blueprint."""
import os
from flask import Blueprint, request, jsonify, send_from_directory, abort, current_app as app
from werkzeug.utils import secure_filename
from blueprints.documents.models import Document, db
from blueprints.auth.models import User  # Assuming the User model is available

documents_bp = Blueprint('documents_bp', __name__)

# Ensure this directory exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    Route to handle document uploads.
    """
    if 'file' not in request.files or 'title' not in request.form:
        return jsonify({"error": "File and title are required"}), 400

    file = request.files['file']
    title = request.form['title']
    description = request.form.get('description', '')
    # Ensure owner_id is provided (you can fetch it from session instead)
    owner_id = request.form.get('owner_id')

    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    document = Document(
        title=title,
        description=description,
        filename=filename,
        file_path=file_path,
        owner_id=owner_id
    )
    document.save_file(file)

    db.session.add(document)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully", "document_id": document.id}), 201

@documents_bp.route('/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """
    Route to retrieve document details.
    """
    document = Document.query.get_or_404(doc_id)
    return jsonify({
        "id": document.id,
        "title": document.title,
        "description": document.description,
        "filename": document.filename,
        "upload_date": document.upload_date.isoformat(),
        "file_url": document.file_url
    })

@documents_bp.route('/documents/<doc_id>/download', methods=['GET'])
def download_document(doc_id):
    """
    Route to download the document file.
    """
    document = Document.query.get_or_404(doc_id)
    return send_from_directory(UPLOAD_FOLDER, document.filename, as_attachment=True)

@documents_bp.route('/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """
    Route to delete a document.
    """
    document = Document.query.get_or_404(doc_id)

    # Remove from the database
    db.session.delete(document)
    db.session.commit()

    # Remove the file from the filesystem
    document.delete_file()

    return jsonify({"message": "Document deleted successfully"}), 200

@documents_bp.route('/documents', methods=['GET'])
def list_documents():
    """
    Route to list all documents for a user.
    """
    owner_id = request.args.get('owner_id')
    if not owner_id:
        return jsonify({"error": "Owner ID is required"}), 400

    documents = Document.query.filter_by(owner_id=owner_id).all()
    return jsonify([{
        "id": doc.id,
        "title": doc.title,
        "description": doc.description,
        "filename": doc.filename,
        "upload_date": doc.upload_date.isoformat(),
        "file_url": doc.file_url
    } for doc in documents])
