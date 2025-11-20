"""Login page component"""

import streamlit as st
from supabase_client import authenticate_user, check_supabase_config


def render_login():
    """Render the login page"""
    # Inject styles multiple times to ensure they override Streamlit defaults
    # Add login-specific styles with high specificity
    st.markdown("""
    <style>
        /* Force override Streamlit's theme variables for login page */
        :root {
            --login-bg: #FFFFFF;
            --login-text: #000000;
            --login-text-secondary: #000000;
        }
        
        /* Override global h3 styles specifically for login form */
        .main [data-testid="stForm"] .element-container .markdown h3,
        .main [data-testid="stForm"] .markdown h3,
        section[data-testid="stForm"] .markdown h3,
        section[data-testid="stForm"] .element-container .markdown h3 {
            color: #000000 !important;
        }
        
        .main [data-testid="stForm"] .element-container .markdown p,
        .main [data-testid="stForm"] .markdown p,
        section[data-testid="stForm"] .markdown p,
        section[data-testid="stForm"] .element-container .markdown p {
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        /* Force black color for all headings and text in login form */
        .main [data-testid="stForm"] h3,
        .main [data-testid="stForm"] h1,
        .main [data-testid="stForm"] h2,
        .main [data-testid="stForm"] h4,
        .main [data-testid="stForm"] h5,
        .main [data-testid="stForm"] h6,
        .main [data-testid="stForm"] p,
        .main [data-testid="stForm"] div,
        .main [data-testid="stForm"] span,
        .main [data-testid="stForm"] * {
            color: #000000 !important;
        }
        
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
            color: #000000 !important;
        }
        
        .login-form-card p {
            color: #000000 !important;
        }
        
        /* Override global typography for login form - more specific selectors */
        section[data-testid="stForm"] h3,
        section[data-testid="stForm"] h1,
        section[data-testid="stForm"] h2,
        section[data-testid="stForm"] h4,
        section[data-testid="stForm"] h5,
        section[data-testid="stForm"] h6,
        section[data-testid="stForm"] p,
        section[data-testid="stForm"] div,
        .main section[data-testid="stForm"] h3,
        .main section[data-testid="stForm"] h1,
        .main section[data-testid="stForm"] h2,
        .main section[data-testid="stForm"] p,
        .main section[data-testid="stForm"] div,
        .login-form-card [data-testid="stForm"] h3,
        .login-form-card [data-testid="stForm"] h1,
        .login-form-card [data-testid="stForm"] h2,
        .login-form-card [data-testid="stForm"] p {
            color: #000000 !important;
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
        
        /* Additional aggressive overrides for Streamlit's rendered elements */
        div[data-baseweb="input"] input {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
        
        /* Target Streamlit's actual input containers */
        section[data-testid="stForm"] .stTextInput input,
        section[data-testid="stForm"] .stTextInput > div > div > input {
            background-color: #FFFFFF !important;
            color: #262730 !important;
            border: 1px solid #d1d5db !important;
        }
        
        /* Ensure all text in the form card is visible */
        .login-form-card .element-container,
        .login-form-card .element-container * {
            color: inherit;
        }
        
        /* Target Streamlit's baseweb components directly */
        .login-form-card [data-baseweb="input"] {
            background-color: #FFFFFF !important;
        }
        
        .login-form-card [data-baseweb="input"] input {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
        
        /* Most specific override for markdown content in forms */
        .main section[data-testid="stForm"] .element-container .markdown h3,
        .main section[data-testid="stForm"] .element-container .markdown p,
        .main section[data-testid="stForm"] .markdown h3,
        .main section[data-testid="stForm"] .markdown p,
        section[data-testid="stForm"] .element-container .markdown h3,
        section[data-testid="stForm"] .element-container .markdown p,
        section[data-testid="stForm"] .markdown h3,
        section[data-testid="stForm"] .markdown p {
            color: #000000 !important;
        }
        
        /* Override any remaining white text in form markdown */
        .main [data-testid="stForm"] .markdown *,
        section[data-testid="stForm"] .markdown * {
            color: #000000 !important;
        }
        
        /* Target signin-header class specifically */
        .signin-header,
        .signin-header h3,
        .signin-header p,
        .signin-header *,
        .main .signin-header,
        .main .signin-header h3,
        .main .signin-header p,
        .main .signin-header *,
        section[data-testid="stForm"] .signin-header,
        section[data-testid="stForm"] .signin-header h3,
        section[data-testid="stForm"] .signin-header p,
        section[data-testid="stForm"] .signin-header * {
            color: #000000 !important;
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
            <h1 style='color: #000000; font-weight: 700; margin-bottom: 0.5rem;'>Tycoon Lights</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Check Supabase configuration
        is_configured, config_error = check_supabase_config()
        if not is_configured:
            st.error(f"⚠️ **Configuration Error:** {config_error}")
            st.info("""
            **For Streamlit Cloud Deployment:**
            1. Go to your app's Settings (⋮ menu → Settings)
            2. Navigate to the "Secrets" tab
            3. Add your Supabase credentials in TOML format:
            
            ```toml
            SUPABASE_URL = "your-supabase-project-url"
            SUPABASE_KEY = "your-supabase-anon-key"
            SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"
            ```
            
            **For Local Development:**
            Create a `.env` file in the project root with:
            ```
            SUPABASE_URL=your-supabase-project-url
            SUPABASE_KEY=your-supabase-anon-key
            SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
            ```
            """)
            st.stop()
        
        # Check if already logged in
        if st.session_state.get('supabase_user'):
            user_email = getattr(st.session_state.supabase_user, 'email', 'User')
            st.success(f"✅ You are already logged in as: **{user_email}**")
            if st.button("Logout", type="secondary", use_container_width=True):
                logout_user()
                st.rerun()
            return
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown("""
            <style>
                /* Force black color for Sign In heading and text - highest specificity */
                .signin-header h3,
                .signin-header p,
                .signin-header *,
                .main .signin-header h3,
                .main .signin-header p,
                section[data-testid="stForm"] .signin-header h3,
                section[data-testid="stForm"] .signin-header p {
                    color: #000000 !important;
                }
            </style>
            <div class="signin-header" style='color: #000000 !important;'>
                <h3 style='color: #000000 !important; font-weight: 600 !important; margin-bottom: 0.5rem !important;'>🔐 Sign In</h3>
                <p style='color: #000000 !important; margin-bottom: 1.5rem !important;'>Enter your credentials to access the system</p>
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

