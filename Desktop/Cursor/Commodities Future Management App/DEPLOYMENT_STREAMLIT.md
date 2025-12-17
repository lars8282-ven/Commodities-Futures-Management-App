# Streamlit Cloud Deployment Guide

This guide will help you deploy the Commodities Futures Management App to Streamlit Cloud with simple password protection.

## Prerequisites

1. GitHub account with the code pushed to a repository
2. Streamlit Cloud account (free tier available)
3. Supabase account and credentials

## Step 1: Deploy to Streamlit Cloud

1. **Sign in to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App:**
   - Click **New app**
   - Select your repository: `lars8282-ven/Commodities-Futures-Management-App`
   - Branch: `master` (or your main branch)
   - Main file path: `app.py`

3. **Configure Secrets:**
   - In the app settings, go to **⚙️ Settings** > **Secrets**
   - Paste the following configuration (replace with your actual values):

   ```toml
   # Supabase Configuration
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-supabase-anon-key"

   # Simple Password Protection
   [password]
   password = "your-secure-password-here"
   ```

   **Important:**
   - Choose a strong password (at least 12 characters, mix of letters, numbers, symbols)
   - Share this password only with authorized users
   - Never commit the password to git

4. **Deploy:**
   - Click **Deploy!**
   - Streamlit will install dependencies and start your app

## Step 2: Verify Password Protection

1. **Test Password:**
   - Visit your deployed app URL
   - You should see a password input form
   - Enter the password you set in secrets
   - You should gain access to the app

2. **Test Incorrect Password:**
   - Try entering a wrong password
   - You should see an error message and remain locked out

## Local Development

For local testing:

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Fill in your actual credentials:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-supabase-anon-key"
   
   [password]
   password = "your-local-password"
   ```
3. Run: `streamlit run app.py`

## Password Management

### Changing the Password

To change the password:
1. Go to Streamlit Cloud > Your App > **⚙️ Settings** > **Secrets**
2. Update the password value in the `[password]` section
3. Save the changes
4. The app will restart with the new password

### Sharing the Password

Share the password securely with authorized users:
- Use encrypted messaging
- Don't send via email in plain text
- Consider using a password manager to share securely

### Disabling Password Protection

To disable password protection temporarily:
1. Remove or comment out the `[password]` section in Streamlit Cloud secrets
2. The app will show a warning but allow access
3. To fully disable, you can modify `lib/auth.py` to always return `True`

## Security Notes

1. **Password Strength:**
   - Use a strong, unique password (at least 12 characters)
   - Mix uppercase, lowercase, numbers, and symbols
   - Don't reuse passwords from other services

2. **Session Security:**
   - Authentication is stored in the user's browser session
   - Closing the browser tab will require re-authentication
   - Sessions don't persist across different browsers/devices

3. **HTTPS:**
   - Streamlit Cloud automatically uses HTTPS
   - Password is transmitted securely over encrypted connection

4. **Limitations:**
   - This is basic password protection, not enterprise-grade security
   - Anyone with the password can access the app
   - For stronger security, consider OIDC authentication (see DEPLOYMENT_STREAMLIT_OIDC.md)

## Troubleshooting

### Password Not Working

1. **Check Secrets Configuration:**
   - Verify the password is correctly set in Streamlit Cloud secrets
   - Ensure there are no extra spaces or quotes around the password
   - Check that the `[password]` section is properly formatted

2. **Check App Logs:**
   - In Streamlit Cloud, go to **⚙️ Settings** > **Logs**
   - Look for authentication errors

### App Not Asking for Password

- Check that the password is set in secrets
- If no password is configured, the app allows access with a warning
- This is intentional - add a password to secrets to enable protection

### Dependencies Not Installing

- Ensure `requirements.txt` includes all necessary packages
- Check logs for specific package installation errors

## Alternative: OIDC Authentication

If you need stronger authentication (e.g., for enterprise use or user tracking), you can switch to OIDC authentication. See the original `DEPLOYMENT_STREAMLIT.md` for OIDC setup instructions with Microsoft Azure AD or Google.

However, for most use cases, simple password protection is sufficient and much easier to set up.

## Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify secrets are correctly configured
3. Ensure the password section is properly formatted in TOML
4. Review the authentication code in `lib/auth.py`
