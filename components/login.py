"""Login page component"""

import streamlit as st
from supabase_client import authenticate_user, check_supabase_config


@st.cache_data
def _get_login_styles():
    """Get login page CSS styles (cached for performance)"""
    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        /* Force override Streamlit's theme variables for login page */
        :root {
            --login-bg: #FFFFFF;
            --login-text: #FFFFFF;
            --login-text-secondary: #FFFFFF;
        }
        
        /* Override Streamlit's theme text color variable */
        .main {
            --text-color: #FFFFFF !important;
        }
        
        /* Override styles.py - must be more specific than .main h1, etc. */
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
        .main .markdown h1, .main .markdown h2, .main .markdown h3,
        .main .markdown h4, .main .markdown h5, .main .markdown h6,
        .main .markdown p, .main .markdown div, .main .markdown span,
        .main p, .main div, .main span {
            color: #FFFFFF !important;
        }
        
        /* Override global h3 styles specifically for login form */
        .main [data-testid="stForm"] .element-container .markdown h3,
        .main [data-testid="stForm"] .markdown h3,
        section[data-testid="stForm"] .markdown h3,
        section[data-testid="stForm"] .element-container .markdown h3 {
            color: #FFFFFF !important;
        }
        
        .main [data-testid="stForm"] .element-container .markdown p,
        .main [data-testid="stForm"] .markdown p,
        section[data-testid="stForm"] .markdown p,
        section[data-testid="stForm"] .element-container .markdown p {
            color: #FFFFFF !important;
        }
        
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
            color: #FFFFFF !important;
        }
        
        /* Override global styles for login page - use very specific selectors */
        .main .element-container .stTextInput > div > div > input,
        .main [data-testid="stForm"] .stTextInput > div > div > input,
        .stTextInput > div > div > input {
            background-color: #1e293b !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            padding: 0.5rem 0.75rem !important;
        }
        
        .main .element-container .stTextInput label,
        .main [data-testid="stForm"] .stTextInput label,
        .stTextInput label,
        .stTextInput > label {
            color: #FFFFFF !important;
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
            color: #FFFFFF !important;
        }
        
        .login-form-card p {
            color: #FFFFFF !important;
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
            color: #FFFFFF !important;
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
            --text-color: #FFFFFF;
        }
        
        /* Force white text color for all input fields - most specific selectors */
        .main [data-testid="stForm"] .stTextInput > div > div > input[type="text"],
        .main [data-testid="stForm"] .stTextInput > div > div > input[type="email"],
        .main [data-testid="stForm"] .stTextInput > div > div > input[type="password"],
        section[data-testid="stForm"] .stTextInput > div > div > input[type="text"],
        section[data-testid="stForm"] .stTextInput > div > div > input[type="email"],
        section[data-testid="stForm"] .stTextInput > div > div > input[type="password"],
        .main .stTextInput > div > div > input[type="text"],
        .main .stTextInput > div > div > input[type="email"],
        .main .stTextInput > div > div > input[type="password"] {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        
        /* Target placeholder text */
        .main [data-testid="stForm"] .stTextInput input::placeholder,
        section[data-testid="stForm"] .stTextInput input::placeholder,
        .main .stTextInput input::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
            opacity: 0.6 !important;
        }
        
        /* Target all input elements with even more specificity */
        .main [data-testid="stForm"] div[data-baseweb="input"] input,
        section[data-testid="stForm"] div[data-baseweb="input"] input,
        .main div[data-baseweb="input"] input {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        
        /* Style help text */
        .login-form-card [data-testid="stTooltipIcon"] {
            color: #64748b !important;
        }
        
        /* Ensure labels are visible */
        .login-form-card label {
            color: #FFFFFF !important;
        }
        
        /* Additional aggressive overrides for Streamlit's rendered elements */
        div[data-baseweb="input"] input {
            background-color: #1e293b !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        
        /* Target Streamlit's actual input containers */
        section[data-testid="stForm"] .stTextInput input,
        section[data-testid="stForm"] .stTextInput > div > div > input {
            background-color: #1e293b !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: 1px solid #d1d5db !important;
        }
        
        /* Ensure all text in the form card is visible */
        .login-form-card .element-container,
        .login-form-card .element-container * {
            color: inherit;
        }
        
        /* Target Streamlit's baseweb components directly */
        .login-form-card [data-baseweb="input"] {
            background-color: #1e293b !important;
        }
        
        .login-form-card [data-baseweb="input"] input {
            background-color: #1e293b !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
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
            color: #FFFFFF !important;
        }
        
        /* Override any remaining white text in form markdown */
        .main [data-testid="stForm"] .markdown *,
        section[data-testid="stForm"] .markdown * {
            color: #FFFFFF !important;
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
            color: #FFFFFF !important;
        }
        
        /* Override styles.py selectors with higher specificity - must be last */
        html body .main h1,
        html body .main h2,
        html body .main h3,
        html body .main h4,
        html body .main h5,
        html body .main h6,
        html body .main p,
        html body .main div,
        html body .main span,
        html body .main .markdown h1,
        html body .main .markdown h2,
        html body .main .markdown h3,
        html body .main .markdown h4,
        html body .main .markdown h5,
        html body .main .markdown h6,
        html body .main .markdown p,
        html body .main .element-container .markdown h1,
        html body .main .element-container .markdown h2,
        html body .main .element-container .markdown h3,
        html body .main .element-container .markdown h4,
        html body .main .element-container .markdown h5,
        html body .main .element-container .markdown h6,
        html body .main .element-container .markdown p,
        html body .main [data-testid="stForm"] .markdown h1,
        html body .main [data-testid="stForm"] .markdown h2,
        html body .main [data-testid="stForm"] .markdown h3,
        html body .main [data-testid="stForm"] .markdown h4,
        html body .main [data-testid="stForm"] .markdown h5,
        html body .main [data-testid="stForm"] .markdown h6,
        html body .main [data-testid="stForm"] .markdown p {
            color: #FFFFFF !important;
        }
        
        /* Mobile Responsive - Login Page */
        @media (max-width: 768px) {
            .main {
                padding: 0.5rem !important;
            }
            
            .block-container {
                padding: 0.5rem !important;
                max-width: 100% !important;
            }
            
            /* Stack login columns on mobile */
            [data-testid="column"] {
                width: 100% !important;
            }
            
            /* Make login form full width on mobile */
            .login-form-card {
                padding: 1.5rem !important;
            }
            
            /* Touch-friendly buttons */
            .stButton > button {
                min-height: 44px !important;
                font-size: 16px !important;
            }
            
            /* Fix input fields on mobile */
            .stTextInput input {
                font-size: 16px !important; /* Prevents zoom on iOS */
            }
        }
        
        @media (max-width: 480px) {
            .main {
                padding: 0.25rem !important;
            }
            
            .login-form-card {
                padding: 1rem !important;
            }
        }
    </style>
    """


def render_login():
    """Render the login page"""
    # Inject cached styles
    st.markdown(_get_login_styles(), unsafe_allow_html=True)
    
    # Center the login form - responsive columns
    # On mobile, col2 will take full width automatically
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and Title
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>💡</h1>
            <h1 style='color: #FFFFFF; font-weight: 700; margin-bottom: 0.5rem;'>Tycoon Lights</h1>
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
            <div class="signin-header" style='color: #FFFFFF !important;'>
                <h3 style='color: #FFFFFF !important; font-weight: 600 !important; margin-bottom: 0.5rem !important;'>🔐 Sign In</h3>
                <p style='color: #FFFFFF !important; margin-bottom: 1.5rem !important;'>Enter your credentials to access the system</p>
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

