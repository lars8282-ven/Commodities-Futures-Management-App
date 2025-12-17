# Streamlit Cloud Deployment Guide

This guide will help you deploy the Commodities Futures Management App to Streamlit Cloud with email authentication restricted to `@tepuiv.com` addresses.

## Prerequisites

1. GitHub account with the code pushed to a repository
2. Streamlit Cloud account (free tier available)
3. OIDC provider configured (Microsoft Azure AD recommended for @tepuiv.com)
4. Supabase account and credentials

## Step 1: Set Up OIDC Authentication

### Option A: Microsoft Azure AD (Recommended for @tepuiv.com)

1. **Register an App in Azure AD:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to **Azure Active Directory** > **App registrations** > **New registration**
   - Name: "Streamlit Commodities App" (or your preferred name)
   - Supported account types: Accounts in this organizational directory only
   - Redirect URI: 
     - For testing: `http://localhost:8501/oauth2callback`
     - For production: `https://your-app-name.streamlit.app/oauth2callback`

2. **Get Client Credentials:**
   - After registration, go to **Overview** and copy:
     - **Application (client) ID** → `client_id`
     - **Directory (tenant) ID** → Use this in `server_metadata_url`
   - Go to **Certificates & secrets** > **New client secret**
     - Description: "Streamlit App Secret"
     - Copy the **Value** (not the Secret ID) → `client_secret`
     - ⚠️ Save this immediately - it won't be shown again!

3. **Configure API Permissions:**
   - Go to **API permissions**
   - Ensure these are enabled:
     - `openid` (OpenID Connect sign-in)
     - `profile` (View users' basic profile)
     - `email` (View users' email address)
   - These should be granted automatically

### Option B: Google Workspace (Alternative)

If your organization uses Google Workspace:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable **Google+ API**
4. Go to **Credentials** > **Create Credentials** > **OAuth client ID**
5. Application type: **Web application**
6. Authorized redirect URIs:
   - `http://localhost:8501/oauth2callback` (local)
   - `https://your-app-name.streamlit.app/oauth2callback` (production)
7. Copy Client ID and Client Secret

## Step 2: Deploy to Streamlit Cloud

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

   # OIDC Authentication (Microsoft Azure AD example)
   [auth]
   redirect_uri = "https://your-app-name.streamlit.app/oauth2callback"
   cookie_secret = "generate-a-random-32-char-secret-here"

   [auth.microsoft]
   client_id = "your-azure-client-id"
   client_secret = "your-azure-client-secret"
   server_metadata_url = "https://login.microsoftonline.com/YOUR-TENANT-ID/v2.0/.well-known/openid-configuration"
   ```

   **Important:**
   - Replace `YOUR-TENANT-ID` in `server_metadata_url` with your Azure AD tenant ID
   - Generate `cookie_secret` using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - For Google, use the `[auth.google]` section instead (see secrets.toml.example)

4. **Update Redirect URI in OIDC Provider:**
   - After deployment, Streamlit Cloud will provide your app URL
   - Update the redirect URI in your Azure AD/Google app to match:
     - `https://your-actual-app-name.streamlit.app/oauth2callback`

5. **Deploy:**
   - Click **Deploy!**
   - Streamlit will install dependencies and start your app

## Step 3: Verify Authentication

1. **Test Login:**
   - Visit your deployed app URL
   - Click "🔑 Log in"
   - You should be redirected to your OIDC provider (Microsoft/Google)
   - Log in with a `@tepuiv.com` email address

2. **Verify Access Control:**
   - Try logging in with a non-`@tepuiv.com` email
   - You should see an "Access Denied" message
   - Only `@tepuiv.com` emails should be able to access the app

## Troubleshooting

### Authentication Not Working

1. **Check Secrets Configuration:**
   - Ensure all secrets are correctly set in Streamlit Cloud
   - Verify `redirect_uri` matches your actual app URL
   - Confirm `cookie_secret` is a valid random string

2. **Check OIDC Provider Settings:**
   - Verify redirect URI is correctly configured in Azure AD/Google
   - Ensure client ID and secret are correct
   - Check that required scopes (openid, profile, email) are enabled

3. **Check App Logs:**
   - In Streamlit Cloud, go to **⚙️ Settings** > **Logs**
   - Look for authentication errors

### Email Domain Not Verified

- The app automatically checks if the logged-in user's email ends with `@tepuiv.com`
- If you need to change the allowed domain, edit `lib/auth.py` and update `ALLOWED_DOMAIN`

### Dependencies Not Installing

- Ensure `requirements.txt` includes `authlib>=1.3.2`
- Check logs for specific package installation errors

## Security Notes

1. **Never commit secrets:**
   - `.streamlit/secrets.toml` is in `.gitignore`
   - Only use Streamlit Cloud's secrets management for production

2. **Cookie Security:**
   - The `cookie_secret` should be unique and random
   - Don't reuse the same secret across different apps

3. **Domain Restriction:**
   - The app enforces email domain checking server-side
   - Even if someone bypasses client-side checks, server-side verification will block access

## Local Development

For local testing:

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Fill in your actual credentials
3. Use `redirect_uri = "http://localhost:8501/oauth2callback"` for local testing
4. Run: `streamlit run app.py`

## Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify OIDC provider configuration
3. Ensure all secrets are correctly set
4. Review the authentication code in `lib/auth.py`

