# How to Get a Valid SmartThings Personal Access Token

This guide will show you how to generate a valid Personal Access Token (PAT) for the SmartThings API.

## 1. Prerequisites

- A Samsung account
- SmartThings app installed and set up on your mobile device
- At least one SmartThings device connected to your account

## 2. Creating a Personal Access Token

1. Go to the SmartThings Developer Portal: https://developer.smartthings.com/

2. Log in with your Samsung account (the same one you use for your SmartThings app)

3. Once logged in, navigate to the "Personal Access Tokens" section:
   - Click on your profile in the upper right corner
   - Select "Personal access tokens" from the dropdown menu

4. Create a new token:
   - Click the "Generate new token" button
   - Give your token a name (e.g., "SmartThings Controller App")
   - For permissions, select all the scopes you need:
     - `r:devices:*` (to read device information)
     - `w:devices:*` (to control devices)
     - `r:locations:*` (to read location information)
     - `w:locations:*` (if you need to update locations)
     - `r:scenes:*` (if you want to access scenes)
     - `x:scenes:*` (if you want to execute scenes)

5. Click "Generate token"

6. **IMPORTANT**: Copy the token immediately and save it somewhere secure. You will not be able to see it again after you leave this page!

## 3. Using Your Token

1. Open the following files in your project:
   - `main.py`
   - `status_report.py`
   - `test_status.py`
   - `check_token.py`

2. Replace the existing token with your new one:
   ```python
   SMARTTHINGS_TOKEN = "your-new-token-here"
   ```

3. Test that your token works:
   ```bash
   python check_token.py
   ```

## 4. Token Security Best Practices

- Never commit your token to a public repository
- Consider using environment variables or a secure configuration file
- Set up token rotation if this is for a production application

## 5. Token Expiration

Personal Access Tokens (PATs) do not expire by default, but they can be revoked at any time from the Developer Portal.

If you need to revoke and regenerate your token:
1. Go back to the SmartThings Developer Portal
2. Navigate to "Personal access tokens" section
3. Find your token and click "Revoke"
4. Generate a new token following the steps above
