# Integrating OAuth with Your SmartThings Webhook Server

This document explains how to integrate the OAuth flow with your existing webhook server running at `https://c78ea69ef759.ngrok-free.app`.

## Overview

The SmartThings OAuth flow has been configured to redirect to your webhook server after successful authorization. Your webhook server needs to handle the OAuth callback to complete the authentication process.

## Setup in SmartThings Developer Portal

Make sure you have registered your application in the SmartThings Developer Portal with the following settings:

- **App Type**: API Access
- **Redirect URI**: `https://c78ea69ef759.ngrok-free.app/oauth/callback`
- **Scopes**: The appropriate permissions for your app (e.g., r:devices:*, w:devices:*, etc.)

## Integration Steps

### 1. Update Your Webhook Server

Your webhook server needs to handle two types of callbacks:

#### a) The PING Challenge

```python
if data.get('lifecycle') == 'PING':
    challenge = data.get('ping', {}).get('challenge')
    print("Received PING challenge. Responding...")
    return jsonify({'challenge': challenge})
```

#### b) The OAuth Callback

```python
if data.get('lifecycle') == 'OAUTH_CALLBACK':
    # Call the oauth_manager to handle the callback
    try:
        # Extract the code from the webhook data
        code = data.get('oauthCallbackData', {}).get('code')
        redirect_uri = "https://c78ea69ef759.ngrok-free.app/oauth/callback"
        
        # Import the OAuth manager
        import oauth_manager
        
        # Exchange the code for tokens
        token_data = oauth_manager.exchange_code_for_tokens(code, redirect_uri)
        print("OAuth authentication successful!")
    except Exception as e:
        print(f"Error processing OAuth callback: {e}")
```

### 2. Starting the OAuth Flow

To start the OAuth flow, run:

```bash
python setup_oauth.py
```

This script will:
1. Generate an authorization URL using your ngrok redirect URI
2. Open a browser to the SmartThings authorization page
3. After authorization, SmartThings will redirect to your webhook server

### 3. Using the Tokens in Your Application

After your webhook server processes the OAuth callback and saves the tokens, you can use them in your application:

```python
from smart_things_controller import SmartThingsController

# Initialize with OAuth token (no arguments needed)
controller = SmartThingsController()

# Use the controller as usual
devices = await controller.get_all_devices()
```

## Troubleshooting

If you encounter issues with the OAuth flow:

1. **Check Redirect URI**: Make sure the redirect URI in the SmartThings Developer Portal exactly matches `https://c78ea69ef759.ngrok-free.app/oauth/callback`
2. **Check Ngrok Status**: Ensure your ngrok tunnel is still active (they expire after a while on the free plan)
3. **Debug Webhook**: Add more logging to your webhook server to see what's happening during the callback
4. **Check Tokens**: Use `python -c "import oauth_manager; print(oauth_manager.is_authenticated())"` to verify if tokens have been saved

Remember that if your ngrok URL changes, you'll need to update:
1. Your app registration in the SmartThings Developer Portal
2. The REDIRECT_URI in auth_server.py
3. The webhook_url in setup_oauth.py

## Testing

To test the OAuth flow:

1. Start your webhook server
2. Run `python setup_oauth.py`
3. Complete the authorization in the browser
4. Check your webhook server logs to ensure it received and processed the callback
5. Run `python main.py` to use the new OAuth tokens

## Security Considerations

- Keep your client ID and client secret confidential
- Protect the tokens.json file which contains your refresh token
- Use HTTPS for all communication (which ngrok provides automatically)
- Verify the state parameter in the OAuth callback to prevent CSRF attacks
