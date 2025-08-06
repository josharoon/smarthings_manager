"""
Webhook Server Example for SmartThings OAuth Integration.

This is an example of how to integrate the OAuth manager with your webhook server.
"""

from flask import Flask, request, jsonify
import json
import oauth_manager

app = Flask(__name__)

# This is the endpoint that SmartThings will ping
@app.route('/oauth/callback', methods=['POST'])
def handle_webhook():
    data = request.json
    print("Received Webhook from SmartThings:", json.dumps(data, indent=2))

    # SmartThings sends a PING to verify the endpoint.
    # We must respond with the challenge value to pass verification.
    if data.get('lifecycle') == 'PING':
        challenge = data.get('ping', {}).get('challenge')
        print("Received PING challenge. Responding...")
        return jsonify({'challenge': challenge})
        
    # Handle OAuth callback
    if data.get('lifecycle') == 'OAUTH_CALLBACK':
        print("Received OAuth callback. Processing...")
        success = oauth_manager.handle_webhook_callback(data)
        if success:
            print("OAuth authentication successful!")
        else:
            print("OAuth authentication failed.")
        
    # For now, we just acknowledge other requests.
    return '', 200

if __name__ == '__main__':
    # Make sure to run on the same port ngrok is tunneling to.
    # For example, if you started ngrok with: ngrok http 8080
    print("Starting Flask server on http://localhost:8080")
    print("Webhook URL: https://c78ea69ef759.ngrok-free.app/oauth/callback")
    app.run(host='0.0.0.0', port=8080, debug=True)
