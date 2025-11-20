"""Login page component"""

import streamlit as st
from supabase_client import authenticate_user


def render_login():
    """Render the login page"""
    # Add login-specific styles with high specificity
    st.markdown("""
    <style>
        /* Override global styles for login page - use very specific selectors */
        .main .element-container .stTextInput > div > div > input,
        .main [data-testid="stForm"] .stTextInput > div > div > input,
        .stTextInput > div > div > input {
            background-color: #FFFFFF !important;
            color: #262730 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            padding: 0.5rem 0.75rem !important;
        }
        
        .main .element-container .stTextInput label,
        .main [data-testid="stForm"] .stTextInput label,
        .stTextInput label,
        .stTextInput > label {
            color: #262730 !important;
            font-weight: 500 !important;
        }
        
        /* Style form container */
        .main [data-testid="stForm"] {
            background-color: transparent !important;
        }
        
        /* Override global typography for login form card */
        .login-form-card h1,
        .login-form-card h2,
        .login-form-card h3,
        .login-form-card h4,
        .login-form-card h5,
        .login-form-card h6 {
            color: #262730 !important;
        }
        
        .login-form-card p {
            color: #64748b !important;
        }
        
        /* Override global typography for login form */
        .main [data-testid="stForm"] h3,
        .main [data-testid="stForm"] h1,
        .main [data-testid="stForm"] h2,
        .main [data-testid="stForm"] h4,
        .main [data-testid="stForm"] h5,
        .main [data-testid="stForm"] h6,
        .login-form-card [data-testid="stForm"] h3,
        .login-form-card [data-testid="stForm"] h1,
        .login-form-card [data-testid="stForm"] h2 {
            color: #262730 !important;
        }
        
        .main [data-testid="stForm"] p,
        .login-form-card [data-testid="stForm"] p {
            color: #64748b !important;
        }
        
        /* Ensure white card background is visible */
        .login-form-card {
            background: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Override any Streamlit default text colors in form */
        .login-form-card * {
            --text-color: #262730;
        }
        
        /* Style help text */
        .login-form-card [data-testid="stTooltipIcon"] {
            color: #64748b !important;
        }
        
        /* Ensure labels are visible */
        .login-form-card label {
            color: #262730 !important;
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
        
        # Login form card wrapper with unique class
        st.markdown("""
        <div class="login-form-card" style='background: #FFFFFF !important; border-radius: 12px !important; padding: 2rem !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important; margin: 1rem 0 !important;'>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown("""
            <div style='color: #262730 !important;'>
                <h3 style='color: #262730 !important; font-weight: 600 !important; margin-bottom: 0.5rem !important;'>🔐 Sign In</h3>
                <p style='color: #64748b !important; margin-bottom: 1.5rem !important;'>Enter your credentials to access the system</p>
            </div>
            """, unsafe_allow_html=True)
            
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

