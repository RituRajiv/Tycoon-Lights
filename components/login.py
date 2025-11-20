"""Login page component"""

import streamlit as st
from supabase_client import authenticate_user


def render_login():
    """Render the login page"""
    # Add login-specific styles
    st.markdown("""
    <style>
        /* Ensure text inputs are visible on login page */
        .stTextInput > div > div > input {
            background-color: #FFFFFF !important;
            color: #262730 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
        }
        
        .stTextInput label {
            color: #262730 !important;
            font-weight: 500 !important;
        }
        
        /* Style form elements */
        div[data-testid="stForm"] {
            background-color: transparent !important;
        }
        
        /* Ensure Streamlit markdown text is visible in form */
        div[data-testid="stForm"] h3,
        div[data-testid="stForm"] h1,
        div[data-testid="stForm"] h2 {
            color: #262730 !important;
        }
        
        div[data-testid="stForm"] p {
            color: #64748b !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and Title
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>💡</h1>
            <h1 style='color: #f1f5f9; font-weight: 700; margin-bottom: 0.5rem;'>Tycoon Lights</h1>
            <p style='color: #cbd5e1; font-size: 1rem;'>Driver Selection & Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if already logged in
        if st.session_state.get('supabase_user'):
            user_email = getattr(st.session_state.supabase_user, 'email', 'User')
            st.success(f"✅ You are already logged in as: **{user_email}**")
            if st.button("Logout", type="secondary", use_container_width=True):
                logout_user()
                st.rerun()
            return
        
        # Login form card wrapper
        st.markdown("""
        <div style='background: #FFFFFF; border-radius: 12px; padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); margin: 1rem 0;'>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<h3 style="color: #262730; font-weight: 600; margin-bottom: 0.5rem;">🔐 Sign In</h3>', unsafe_allow_html=True)
            st.markdown('<p style="color: #64748b; margin-bottom: 1.5rem;">Enter your credentials to access the system</p>', unsafe_allow_html=True)
            
            email = st.text_input(
                "📧 Email Address", 
                placeholder="your.email@example.com",
                help="Enter your registered email address"
            )
            
            password = st.text_input(
                "🔒 Password", 
                type="password", 
                placeholder="Enter your password",
                help="Enter your password"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submit_button = st.form_submit_button(
                "🚀 Login", 
                type="primary", 
                use_container_width=True
            )
            
            if submit_button:
                if email and password:
                    with st.spinner("🔄 Authenticating..."):
                        success, message = authenticate_user(email, password)
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.session_state.current_page = "Home"
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please enter both email and password")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem; color: #64748b; font-size: 0.875rem;'>
            <p>Need help? Contact your administrator</p>
        </div>
        """, unsafe_allow_html=True)


def logout_user():
    """Logout the current user"""
    st.session_state.pop('supabase_user', None)
    st.session_state.pop('supabase_session', None)
    st.session_state.current_page = "Login"
    st.success("✅ Logged out successfully")

