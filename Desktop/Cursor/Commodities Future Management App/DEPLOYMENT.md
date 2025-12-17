# Deployment Guide - Streamlit Community Cloud

This guide explains how to deploy the CME Futures Scraper app to Streamlit Community Cloud with email authentication.

## Prerequisites

1. GitHub account
2. Code pushed to a GitHub repository
3. Streamlit Community Cloud account (free at https://share.streamlit.io)

## Step 1: Push Code to GitHub

If your code isn't already on GitHub:

1. Create a new repository on GitHub
2. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

## Step 2: Deploy to Streamlit Community Cloud

1. **Sign in to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select your GitHub repository
   - Select the branch (usually `main` or `master`)
   - Set Main file path to: `app.py`

3. **Configure App**
   - App URL: Choose a subdomain (e.g., `your-app-name`)
   - Python version: Select Python 3.10 or higher

## Step 3: Set Up Secrets

Streamlit Cloud uses secrets to store sensitive information like API keys.

1. In your app's settings, click "Secrets"
2. Add the following secrets in TOML format:

```toml
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
```

3. Click "Save"

## Step 4: Authentication

The app uses email domain verification to restrict access to @tepuiv.com email addresses.

### How It Works

- Users must enter their email address when accessing the app
- Only emails ending with `@tepuiv.com` are authorized
- Authentication is stored in session state (per browser session)

### For Production (Optional - More Secure)

For a more secure authentication system, consider using:

1. **Streamlit's Built-in OIDC Authentication** (requires OIDC provider setup)
   - Configure Google Workspace or Microsoft Azure AD
   - Use `st.login()` and `st.user` features
   - See Streamlit docs for OIDC setup

2. **Custom OAuth Integration**
   - Integrate with your organization's SSO
   - More complex but more secure

## Step 5: Verify Deployment

1. Access your app at: `https://your-app-name.streamlit.app`
2. You should see the login form
3. Enter a @tepuiv.com email address
4. After authentication, the app should load normally

## Environment Variables

The app uses the following environment variables (set via Streamlit Secrets):

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key

## Troubleshooting

### App won't start
- Check that `app.py` is the correct main file
- Verify all dependencies are in `requirements.txt`
- Check Streamlit Cloud logs for errors

### Authentication not working
- Ensure `lib/auth.py` is included in your repository
- Check that the email domain check is working correctly

### Database connection errors
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set correctly in secrets
- Check that your Supabase project is accessible
- Ensure your Supabase API key has proper permissions

### Selenium/ChromeDriver issues
- Streamlit Cloud may have limitations with Selenium
- Consider using headless mode (already enabled)
- Check Cloud logs for ChromeDriver errors

## Security Notes

1. **Email Verification Limitations**
   - Current implementation is client-side verification
   - For production, consider server-side validation
   - Session-based auth resets on browser close

2. **API Keys**
   - Never commit secrets to GitHub
   - Always use Streamlit Secrets for sensitive data
   - Use service role keys only in secure environments

3. **Rate Limiting**
   - Consider adding rate limiting for scraping operations
   - Monitor usage to prevent abuse

## Updating the App

To update your deployed app:

1. Push changes to your GitHub repository
2. Streamlit Cloud automatically detects changes
3. The app will redeploy (may take 1-2 minutes)

Or manually trigger a redeploy:
1. Go to your app settings
2. Click "Reboot app"

## Support

For issues specific to:
- **Streamlit Cloud**: Check https://docs.streamlit.io/streamlit-community-cloud
- **App functionality**: Check the app logs in Streamlit Cloud dashboard

