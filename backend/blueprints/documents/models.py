"""Define the Document model."""
from datetime import datetime
import uuid
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Document(db.Model):
    """
    Document model for storing document information.
    """
    __tablename__ = 'documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(200), nullable=False)
    owner_id = db.Column(db.Integer,
                         db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Document {self.title} - {self.filename}>'

    @property
    def file_url(self):
        """Generate the file URL for serving the document."""
        return os.path.join('/uploads/', self.filename)

    def save_file(self, file):
        """Save the file to the filesystem."""
        file.save(self.file_path)

    def delete_file(self):
        """Delete the file from the filesystem."""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
