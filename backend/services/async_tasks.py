from extensions import celery

@celery.task
def process_document_sync(document_id):
    # Code to process document synchronously
    pass

@celery.task
def process_query_async(query):
    # Code to process query asynchronously
    pass