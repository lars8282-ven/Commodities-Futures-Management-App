"""
Authentication module for Streamlit app.
Verifies user email domain to restrict access.
"""
import streamlit as st
import re


def verify_email_domain(email: str, allowed_domain: str = "@tepuiv.com") -> bool:
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
    Check if user is authenticated with allowed email domain.
    Uses session state to persist authentication.
    
    Returns:
        True if authenticated, False otherwise
    """
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    
    # Return True if already authenticated
    if st.session_state.authenticated:
        return True
    
    # Show login form
    return False


def show_login_form() -> bool:
    """
    Display login form and handle authentication.
    
    Returns:
        True if user is authenticated, False otherwise
    """
    st.title("🔐 Authentication Required")
    st.markdown("This application is restricted to authorized users.")
    st.info("Please enter your @tepuiv.com email address to continue.")
    
    with st.form("login_form"):
        email = st.text_input(
            "Email Address",
            placeholder="your.name@tepuiv.com",
            type="default"
        )
        
        submit_button = st.form_submit_button("Login", type="primary")
        
        if submit_button:
            if verify_email_domain(email):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.success(f"Authenticated as {email}")
                st.rerun()
            else:
                st.error(f"Access denied. Only @tepuiv.com email addresses are authorized.")
                return False
    
    return False

