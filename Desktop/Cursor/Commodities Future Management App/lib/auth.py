"""
Authentication module for Streamlit app.
Uses Streamlit's built-in OIDC authentication with email domain verification.
Restricts access to @tepuiv.com email addresses.
"""
import streamlit as st


ALLOWED_DOMAIN = "@tepuiv.com"


def verify_email_domain(email: str, allowed_domain: str = ALLOWED_DOMAIN) -> bool:
    """
    Verify email belongs to allowed domain.
    
    Args:
        email: Email address to verify
        allowed_domain: Required domain (default: "@tepuiv.com")
        
    Returns:
        True if email ends with allowed domain, False otherwise
    """
    if not email:
        return False
    
    email = email.strip().lower()
    allowed_domain = allowed_domain.lower()
    
    # Simple validation: check if email ends with allowed domain
    return email.endswith(allowed_domain) and "@" in email


def check_authentication() -> bool:
    """
    Check if user is authenticated with allowed email domain using Streamlit OIDC.
    
    This function:
    1. Checks if user is logged in via Streamlit's built-in OIDC (st.user)
    2. Verifies the email domain is @tepuiv.com
    3. Shows login button if not authenticated
    4. Shows error if logged in with wrong domain
    
    Returns:
        True if authenticated with correct domain, False otherwise
    """
    # Check if user is logged in via Streamlit OIDC
    if not st.user.is_logged_in:
        # User is not logged in - show login button
        st.title("🔐 Authentication Required")
        st.markdown("This application is restricted to authorized users.")
        st.info(f"Please log in with your {ALLOWED_DOMAIN} email address to continue.")
        
        # Try to detect if OIDC is configured
        try:
            # Show login button - this will redirect to OIDC provider
            if st.button("🔑 Log in", type="primary"):
                st.login()  # Redirects to OIDC provider
            return False
        except Exception as e:
            # If OIDC is not configured, show helpful error
            st.error("⚠️ Authentication is not configured properly.")
            st.warning(
                "To enable authentication, you need to configure OIDC in `.streamlit/secrets.toml`. "
                "See the deployment guide for setup instructions."
            )
            st.code(
                """
# Example configuration for Microsoft/Azure AD:
[auth]
redirect_uri = "https://your-app-url.streamlit.app/oauth2callback"
cookie_secret = "your-random-secret-here"

[auth.microsoft]
client_id = "your-client-id"
client_secret = "your-client-secret"
server_metadata_url = "https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration"
                """,
                language="toml"
            )
            return False
    
    # User is logged in - check email domain
    user_email = st.user.get("email") or st.user.get("preferred_username") or ""
    
    if not user_email:
        st.error("⚠️ Unable to retrieve email from authentication provider.")
        st.info("Please contact your administrator if this issue persists.")
        if st.button("🔓 Log out"):
            st.logout()
        return False
    
    # Verify email domain
    if not verify_email_domain(user_email, ALLOWED_DOMAIN):
        st.error(f"❌ Access Denied")
        st.warning(
            f"Your email address ({user_email}) is not authorized to access this application. "
            f"Only {ALLOWED_DOMAIN} email addresses are permitted."
        )
        if st.button("🔓 Log out"):
            st.logout()
        return False
    
    # User is authenticated with correct domain
    return True


def show_login_form() -> bool:
    """
    Deprecated: This function is kept for backwards compatibility.
    Use check_authentication() instead, which handles OIDC authentication.
    
    Returns:
        True if user is authenticated, False otherwise
    """
    return check_authentication()
