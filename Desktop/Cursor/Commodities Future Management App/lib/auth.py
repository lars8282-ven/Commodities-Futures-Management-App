"""
Simple password authentication module for Streamlit app.
Uses a password stored in secrets or config for basic access control.
"""
import streamlit as st


def check_authentication() -> bool:
    """
    Check if user has entered the correct password.
    
    Password is stored in:
    - Streamlit Cloud: secrets (st.secrets.get("password", {}).get("password"))
    - Local: config.toml [password] section or secrets.toml
    
    Returns:
        True if authenticated, False otherwise
    """
    # Get password from secrets or config
    try:
        # Try to get password from secrets first (Streamlit Cloud)
        required_password = st.secrets.get("password", {}).get("password")
        # If not in secrets, try config (local development)
        if not required_password:
            # For local development, you can also set it directly here temporarily
            # But better to use secrets.toml
            required_password = None
    except Exception:
        required_password = None
    
    # If no password is configured, allow access (optional - you may want to require it)
    if not required_password:
        st.warning("⚠️ No password configured. Please set a password in secrets.toml or Streamlit Cloud secrets.")
        st.info("For now, allowing access. Configure password protection by adding `[password] password = 'your-password'` to secrets.")
        return True  # Allow access if no password configured
    
    # Check if user is already authenticated in this session
    if st.session_state.get("authenticated", False):
        return True
    
    # Show password input form
    st.title("🔐 Password Required")
    st.markdown("This application is password protected.")
    
    with st.form("password_form"):
        password_input = st.text_input(
            "Enter Password",
            type="password",
            placeholder="Enter the application password"
        )
        submit_button = st.form_submit_button("Submit", type="primary")
        
        if submit_button:
            if password_input == required_password:
                st.session_state.authenticated = True
                st.success("✅ Access granted!")
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")
                return False
    
    return False
