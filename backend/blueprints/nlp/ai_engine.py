import time
import os
import logging
import re
import json
from functools import lru_cache
from typing import Dict, Any, Optional
import spacy
import requests
from cachetools import TTLCache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from PyPDF2 import PdfReader
from docx import Document
from langchain.llm import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load spaCy's English NLP model
nlp = spacy.load('en_core_web_sm')

# In-memory cache to store recent queries and their results
cache = TTLCache(maxsize=100, ttl=300)

# Session-like structure for retaining query context
query_sessions = {}

# Advanced ML model setup for classification with a pipeline
classifier = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('svc', SVC(probability=True))
])

# Setup the Hugging Face pipeline for semantic search
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
semantic_model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased')
semantic_search = pipeline('feature-extraction', model=semantic_model, tokenizer=tokenizer)

# Function to train the model (example)
def train_classifier():
    # Placeholder training data (should be replaced with real data)
    training_data = ["breach of contract", "legal precedent", "statute"]
    labels = ["contract", "case_law", "statute"]

    X = classifier.named_steps['vectorizer'].fit_transform(training_data)
    classifier.fit(X, labels)

# Call the training function (in practice, this would be done offline)
train_classifier()

def preprocess_query(query: str) -> str:
    """
    Preprocess the query to improve the results from the LLaMA model.
    - Tokenize
    - Remove stopwords and punctuation
    - Lemmatize the tokens
    - Named Entity Recognition (NER) to emphasize legal terms
    """
    doc = nlp(query)

    processed_tokens = [
        token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct
    ]

    processed_query = ' '.join(processed_tokens)
    logging.debug("Preprocessed query: %s", processed_query)
    return processed_query

def classify_query_ml(query: str) -> str:
    """
    Classify the query using a machine learning model.
    """
    X_query = classifier.named_steps['vectorizer'].transform([query])
    classification = classifier.predict(X_query)
    logging.debug("Query classification: %s", classification[0])
    return classification[0]

def web_search(query: str) -> str:
    """
    Perform a web search to retrieve external information.
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        logging.error("API key or Search Engine ID not set in .env file.")
        return "API key or Search Engine ID not set."

    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        search_results = response.json()

        # Extract relevant content (e.g., the first result's snippet)
        if 'items' in search_results:
            return search_results['items'][0]['snippet']
        
        return "No relevant results found."

    except requests.exceptions.RequestException as e:
        logging.error("Web search failed: %s", str(e))
        return "Web search failed."

def parse_document(file_path: str) -> str:
    """
    Parse a user-uploaded document (PDF, DOCX) and extract text.
    """
    try:
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                return text

        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])

        else:
            logging.error("Unsupported file format: %s", file_path)
            return "Unsupported file format."

    except Exception as e:
        logging.error("Failed to parse document %s: %s", file_path, str(e))
        return "Error processing document."

def link_documents_to_case(doc_text: str, case_database: Dict[str, str]) -> Optional[str]:
    """
    Link the content of a document to relevant legal cases by comparing semantic similarity.
    """
    try:
        doc_embedding = semantic_search(doc_text)

        best_match = None
        highest_similarity = 0
        for case_name, case_text in case_database.items():
            case_embedding = semantic_search(case_text)
            similarity = cosine_similarity(doc_embedding, case_embedding)
   
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = case_name
 
        return best_match

    except Exception as e:
        logging.error("Failed to link document to case: %s", str(e))
        return None

def cosine_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two embeddings.
    """
    # Ensure both embeddings are flattened and of the same length
    embedding1_flat = embedding1[0][0]
    embedding2_flat = embedding2[0][0]

    norm1 = sum([x ** 2 for x in embedding1_flat]) ** 0.5
    norm2 = sum([y ** 2 for y in embedding2_flat]) ** 0.5

    return sum([x * y for x, y in zip(embedding1_flat, embedding2_flat)]) / (norm1 * norm2)

@lru_cache(maxsize=32)
def cache_result(query: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cache the result for frequently asked queries.
    """
    cache[query] = result
    logging.debug("Cached result for query: %s", query)
    return result

def manage_query_context(user_id: str, query: str) -> str:
    """
    Manage the retention and context of queries for a specific user.
    """
    if user_id not in query_sessions:
        query_sessions[user_id] = []

    # Retain the current query context
    query_sessions[user_id].append(query)

    # Combine current and previous queries for context
    combined_query = " ".join(query_sessions[user_id])

    return combined_query

def process_legal_query(query: str, user_id: Optional[str] = None, user_document_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Process the legal query using LLaMA and external sources.
    - Preprocess the query
    - Classify the query type using ML
    - Fetch information from web and documents
    - Cache results for frequent queries
    - Handle context if provided
    - Use LangChain for enhanced query processing
    """
    try:
        # Validate the input query
        if not validate_query_input(query):
            raise ValueError("Invalid query format detected.")
        
        # Step 1: Preprocess the query
        processed_query = preprocess_query(query)

        # Step 2: Manage query context
        if user_id:
            processed_query = manage_query_context(user_id, processed_query)

        # Step 3: Classify the query using ML
        query_type = classify_query_ml(processed_query)
        
        logging.info("Processing a %s query: %s", query_type, processed_query)

        # Check cache before querying the model
        if processed_query in cache:
            logging.info("Cache hit for query: %s", processed_query)
            return cache[processed_query]

        # Step 4: Web search for additional information
        web_info = web_search(processed_query)

        # Step 5: Document parsing and linking to cases (optional)
        linked_case = None
        if user_document_path:
            doc_text = parse_document(user_document_path)
            linked_case = link_documents_to_case(doc_text, case_database={})
            if linked_case:
                logging.info("Document linked to case: %s", linked_case)
            else:
                logging.info("No case linked from the document.")

        # Step 6: Use LangChain for query processing
        prompt_template = PromptTemplate(
            input_variables=["query"],
            template="Given the query '{query}', provide relevant legal advice."
        )
        langchain_chain = LLMChain(llm=ollama.llama, prompt_template=prompt_template)
        langchain_result = langchain_chain.run(query=processed_query)

        # Combine results from LangChain, LLaMA, and web/document information
        combined_result = {
            "langchain_result": langchain_result,
            "web_info": web_info,
            "linked_case": linked_case
        }

        # Cache the result
        cached_result = cache_result(processed_query, {"result": combined_result, "processing_time": time.time()})

        return cached_result

    except ValueError as ve:
        logging.warning("Validation error: %s", str(ve))
        return {"error": str(ve)}
    except Exception as e:
        logging.error("General error: %s", str(e))
        return {"error": "An unexpected error occurred. Please try again later."}

# Additional security measure: input validation
def validate_query_input(query: str) -> bool:
    """
    Validate the input query to prevent injection attacks and ensure it meets the expected format.
    """
    # Basic validation: only allow alphanumeric characters, common punctuation, and legal symbols
    if not re.match(r'^[a-zA-Z0-9\s,.\'\-()\[\]]+$', query):
        logging.warning("Invalid input detected: %s", query)
        return False
    return True
