"""Asynchronous tasks for processing documents and legal queries."""
import logging
from extensions import celery, db
from services.caching import cache_set
from blueprints.documents.models import Document
from blueprints.nlp.ai_engine import process_legal_query

@celery.task(bind=True)
def process_document_async(self, document_id):
    """
    Asynchronously processes a document.
    :param document_id: ID of the document to be processed.
    :return: None
    """
    try:
        # Fetch the document from the database
        document = Document.query.get(document_id)
        if not document:
            logging.error("Document with ID %s not found.", document_id)
            return

        # Process the document content
        # (e.g., extract text, link to legal cases, etc.)
        # Example: assuming `process_legal_query` can also process documents.
        result = process_legal_query(document.content)

        # Save the processed result back to the database or another storage
        document.processed_data = result  # Assuming Document model has a processed_data field
        db.session.commit()
        logging.info("Document with ID %s processed successfully.", document_id)

    except Exception as e:
        logging.error("Failed to process document with ID %s: {str(e)}", document_id)
        self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True)
def process_query_async(self, query, user_id):
    """
    Asynchronously processes a legal query.
    :param query: The query string to be processed.
    :param user_id: The ID of the user who submitted the query.
    :return: Result of the query processing.
    """
    try:
        # Process the query using the AI engine
        result = process_legal_query(query, user_id=user_id)

        # You can save the result to the database or cache if needed
        # Example: caching the result
        cache_key = f"user:{user_id}:query:{query}"
        cache_set(cache_key, result, timeout=600)  # Cache for 10 minutes

        logging.info("Query processed successfully for user {user_id}.")
        return result

    except Exception as e:
        logging.error("Failed to process query for user {user_id}: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)
