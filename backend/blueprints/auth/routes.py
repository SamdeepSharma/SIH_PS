"""Routes for the authentication blueprint."""
import json
from flask import Blueprint, redirect, url_for, session, request, jsonify
from flask import current_app as app
from oauthlib.oauth2 import WebApplicationClient
import requests
from blueprints.auth.models import User, db

auth_bp = Blueprint('auth_bp', __name__)

# Initialize the OAuth2 client
client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])

@auth_bp.route('/login')
def login():
    """
    Login route for Google's OAuth2 authentication
    """
    # Get Google's authorization endpoint
    google_provider_cfg = requests.get(app.config['GOOGLE_DISCOVERY_URL'], timeout=5).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Prepare the request URI
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for('auth_bp.callback', _external=True),
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route('/login/callback')
def callback():
    """
    Callback for Google's OAuth2 authentication
    """
    # Get the authorization code from the request
    code = request.args.get("code")

    # Get Google's token endpoint
    google_provider_cfg = requests.get(app.config['GOOGLE_DISCOVERY_URL'], timeout=5).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare the token request
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_uri=url_for('auth_bp.callback', _external=True),
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET']),
        timeout=5
    )

    # Parse the token response
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get the user's profile information
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body, timeout=5)

    # Store the user's information in session
    user_info = userinfo_response.json()
    email = user_info["email"]

    # Check if the user exists in the database
    user = User.query.filter_by(email=email).first()

    if not user:
        # Create a new user
        user = User(
            email=email,
            name=user_info["name"],
            google_id=user_info["sub"]  # 'sub' is the unique Google ID for the user
        )
        db.session.add(user)
        db.session.commit()

    # Update session with the user information
    session['user'] = {
        'email': user.email,
        'name': user.name,
        'google_id': user.google_id
    }
    session['email'] = user.email

    # Redirect to the dashboard or home page
    return redirect(url_for('dashboard_bp.dashboard'))

@auth_bp.route('/logout')
def logout():
    """
    Logout route to clear the session
    """
    # Clear the session
    session.clear()
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/profile')
def profile():
    """
    Example profile route to display user information
    """
    # Example profile route to display user information
    if 'user' not in session:
        return redirect(url_for('auth_bp.login'))

    return jsonify(session['user'])
