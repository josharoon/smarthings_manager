# OAuth Authentication for SmartThings Controller

This document explains how to use the OAuth 2.0 authentication flow with the SmartThings Controller.

## Overview

The SmartThings API has moved to OAuth 2.0 authentication as the preferred method for accessing the API. Personal Access Tokens (PATs) are now limited to 24-hour validity, which makes them unsuitable for long-running applications.

This implementation:
- Uses the OAuth 2.0 authorization code flow
- Securely stores refresh tokens for automatic renewal of access tokens
- Provides a simple web server to handle the authorization flow

## Setup Instructions

### Step 1: Install Dependencies

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

### Step 2: Configure OAuth Client

Before using the OAuth flow, you need to set up your SmartThings API client. The client ID and client secret can be configured in two ways:

1. **Environment Variables**:
   ```bash
   export SMARTTHINGS_CLIENT_ID=your_client_id
   export SMARTTHINGS_CLIENT_SECRET=your_client_secret
   ```

2. **Update `config.py`** (for development only):
   The `config.py` file contains default values for the client ID and client secret, but it's recommended to use environment variables for security.

### Step 3: Initial Authentication

Run the OAuth setup script:

```bash
./setup_oauth.py
```

This will:
1. Start a local web server to handle the OAuth callback
2. Open a browser window to the SmartThings authorization page
3. Guide you through the authorization process
4. Store the tokens securely for future use

### Step 4: Using the Application

After successful authentication, the application will use the stored tokens to access the SmartThings API. The tokens will be automatically refreshed when needed.

## Token Management

The tokens are stored in a file called `tokens.json` in the application directory with restricted permissions (readable only by the owner).

If you need to force re-authentication, you can:
1. Run `./setup_oauth.py` again
2. Select "y" when asked if you want to re-authenticate
3. Follow the authorization process again

## Troubleshooting

### Authentication Failed

If the authentication process fails, check the following:
- Ensure that the client ID and client secret are correct
- Verify that the redirect URI in the SmartThings Developer Workspace matches the one used in the application (`http://localhost:8000/oauth/callback` by default)
- Check that the scopes requested are authorized for your client application

### Token Refresh Failed

If token refresh fails, you may need to re-authenticate:
- Run `./setup_oauth.py` to start a new authentication flow
- Check that your internet connection is working
- Ensure that your SmartThings account is active and in good standing

## Security Considerations

- The refresh token is stored locally and should be protected
- The application uses HTTPS for all communication with the SmartThings API
- The state parameter is used to prevent CSRF attacks during the OAuth flow
- The token file has restricted permissions to prevent unauthorized access

## References

For more details on the SmartThings OAuth flow, refer to:
- [SmartThings Developer Documentation](https://developer.smartthings.com/docs/authorization/)
- The `developer_guide.md` file in this repository
