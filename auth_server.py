"""
Authentication Server for SmartThings OAuth Flow.

This module provides a simple Flask web server to handle the OAuth 2.0 flow
for SmartThings API authentication. It implements two main routes:
- /login: Initiates the OAuth flow
- /oauth/callback: Handles the callback from SmartThings

To start the server, run:
    python auth_server.py
"""

import os
import webbrowser
from flask import Flask, request, redirect, url_for, session, jsonify
import oauth_manager

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Configuration - Update with your server's details
HOST = '0.0.0.0'  # Allow connections from all interfaces
PORT = 8080

# Using the ngrok URL for the redirect URI
REDIRECT_URI = "https://c78ea69ef759.ngrok-free.app/oauth/callback"

# Print the redirect URI to ensure it matches what's registered in SmartThings Developer Portal
print(f"\nImportant: Make sure this exact URI is registered in SmartThings Developer Portal:")
print(f"Redirect URI: {REDIRECT_URI}")

@app.route('/')
def index():
    """
    Root endpoint providing information about the authentication server.
    """
    # Print diagnostic information
    client_id = oauth_manager.config.get_client_id()
    print(f"\nDiagnostics:")
    print(f"Client ID: {client_id}")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Scopes: {' '.join(oauth_manager.DEFAULT_SCOPES)}")
    print(f"Make sure these match your SmartThings developer portal settings\n")
    if oauth_manager.is_authenticated():
        return '''
            <h1>SmartThings Authentication</h1>
            <p>You are authenticated with SmartThings!</p>
            <a href="/refresh">Refresh Token</a>
            <a href="/logout">Logout</a>
        '''
    else:
        return '''
            <h1>SmartThings Authentication</h1>
            <p>You are not authenticated with SmartThings.</p>
            <a href="/login">Login with SmartThings</a>
        '''

@app.route('/login')
def login():
    """
    Initiates the OAuth flow by redirecting to SmartThings authorization page.
    """
    try:
        # Generate a state parameter for security
        state = os.urandom(16).hex()
        session['oauth_state'] = state
        
        # Print diagnostics before redirecting
        client_id = oauth_manager.config.get_client_id()
        print(f"\n--- OAuth Login Diagnostics ---")
        print(f"Client ID: {client_id}")
        print(f"Redirect URI: {REDIRECT_URI}")
        print(f"State: {state}")
        print(f"Scopes: {' '.join(oauth_manager.DEFAULT_SCOPES)}")
        
        # Generate the authorization URL
        auth_url = oauth_manager.generate_auth_url(
            redirect_uri=REDIRECT_URI,
            state=state
        )
        
        print(f"Authorization URL: {auth_url}")
        print("Redirecting to SmartThings authorization page...")
        
        # Redirect the user to the SmartThings authorization page
        return redirect(auth_url)
    except Exception as e:
        print(f"Error in login route: {str(e)}")
        return f"Error starting OAuth flow: {str(e)}", 500

# Note: The /oauth/callback route is now handled by your webhook server
# We're removing it from here to avoid conflict

@app.route('/refresh')
def refresh():
    """
    Refreshes the access token.
    """
    try:
        access_token = oauth_manager.refresh_access_token()
        return jsonify({'message': 'Token refreshed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """
    Clears the stored tokens.
    """
    oauth_manager.clear_tokens()
    return redirect(url_for('index'))

@app.route('/token-status')
def token_status():
    """
    Provides status information about the current tokens.
    """
    if oauth_manager.is_authenticated():
        return jsonify({'authenticated': True})
    else:
        return jsonify({'authenticated': False})
        
@app.route('/oauth-settings')
def oauth_settings():
    """
    Display current OAuth settings for troubleshooting.
    """
    client_id = oauth_manager.config.get_client_id()
    # Mask the client secret for security
    client_secret = oauth_manager.config.get_client_secret()
    if client_secret:
        masked_secret = client_secret[:4] + '*' * (len(client_secret) - 8) + client_secret[-4:]
    else:
        masked_secret = "Not configured"
    
    settings = {
        'client_id': client_id,
        'client_secret_masked': masked_secret,
        'redirect_uri': REDIRECT_URI,
        'scopes': oauth_manager.DEFAULT_SCOPES,
    }
    
    return f"""
    <h1>SmartThings OAuth Settings</h1>
    <p>These are your current OAuth settings. Make sure they match what's in your SmartThings Developer Portal.</p>
    <pre>{settings}</pre>
    <h2>Registration Instructions</h2>
    <ol>
        <li>Go to <a href="https://developer.smartthings.com/" target="_blank">SmartThings Developer Portal</a></li>
        <li>Register an "API Access" application</li>
        <li>Set the Redirect URI to exactly: <code>{REDIRECT_URI}</code></li>
        <li>Request all needed scopes (they must match the ones listed above)</li>
    </ol>
    <p><a href="/">Return to home</a></p>
    """

def start_server():
    """
    Starts the authentication server and opens the browser for login.
    """
    print(f"Starting authentication server at http://{HOST}:{PORT}")
    webbrowser.open(f"http://{HOST}:{PORT}/login")
    app.run(host=HOST, port=PORT, debug=True)

if __name__ == '__main__':
    start_server()
