# Main Streamlit application

import streamlit as st
from styles import get_custom_styles
from session_state import initialize_session_state
from components.navigation import render_navigation
from components.driver_form import render_driver_form
from components.table_display import render_table
from components.pdf_upload import render_pdf_upload
from components.login import render_login
from supabase_client import fetch_particulars, fetch_brands, authenticate_user

# Page configuration - optimized for mobile
st.set_page_config(
    page_title="Tycoon Lights",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)
# Optimize for mobile - reduce initial render complexity
if 'mobile_optimized' not in st.session_state:
    st.session_state.mobile_optimized = True

# Apply custom styles
st.markdown(get_custom_styles(), unsafe_allow_html=True)

# JavaScript injection for hiding rerun button - optimized for mobile
import streamlit.components.v1 as components

hide_rerun_html = """
<script>
(function() {
    'use strict';
    let executed = false;
    const MAX_RETRIES = 3;
    let retryCount = 0;
    
    function hideRerun() {
        if (executed && retryCount >= MAX_RETRIES) return;
        
        try {
            const toolbar = document.querySelector('[data-testid="stToolbar"]');
            if (toolbar) {
                toolbar.style.display = 'none';
                toolbar.remove();
            }
            
            const header = document.querySelector('header[data-testid="stHeader"]');
            if (header) {
                header.style.display = 'none';
            }
            
            const headerButtons = document.querySelectorAll('header button');
            headerButtons.forEach(btn => btn.remove());
            
            executed = true;
        } catch (e) {
            retryCount++;
            if (retryCount < MAX_RETRIES) {
                setTimeout(hideRerun, 200);
            }
        }
    }
    
    // Run once after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hideRerun, { once: true });
    } else {
        setTimeout(hideRerun, 50);
    }
})();
</script>
"""
components.html(hide_rerun_html, height=0)

# Initialize session state
initialize_session_state()

# Check auth status
is_logged_in = st.session_state.get('supabase_user') is not None
current_page = st.session_state.get('current_page', 'Home')

# Render navigation
render_navigation()

# Handle page navigation
if current_page == "Login":
    render_login()
    st.stop()
elif current_page == "Upload PDF":
    # Check authentication
    if not is_logged_in:
        st.warning("🔐 **Authentication Required:** Please log in to access the upload page.")
        with st.expander("🔑 Sign In", expanded=True):
            email = st.text_input("Email", key="auth_email_upload")
            password = st.text_input("Password", type="password", key="auth_password_upload")
            
            col_auth1, col_auth2 = st.columns([1, 1])
            with col_auth1:
                if st.button("Sign In", type="primary", use_container_width=True, key="signin_upload"):
                    if email and password:
                        success, message = authenticate_user(email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter both email and password")
        st.stop()
    render_pdf_upload()
    st.stop()
else:
    # Home page
    # Fetch particulars (cached) - optimized for mobile
    try:
        # Only show spinner if data is not cached (first load)
        db_particulars = fetch_particulars()
        if not db_particulars:
            st.error("❌ No particulars found in database. Please contact your administrator.")
            st.stop()
        particular = st.selectbox(
            "📦 Select Particular", 
            db_particulars, 
            index=0,
            help="Choose the type of component you want to configure"
        )
    except ValueError as e:
        # Configuration errors (missing env vars, invalid URL format)
        st.error(f"❌ Configuration Error: {e}")
        st.info("""
        **To fix this issue:**
        
        **For Local Development:**
        1. Create a `.env` file in the project root
        2. Add your Supabase credentials:
        ```
        SUPABASE_URL=https://ldatmittxoudwpcgdcbc.supabase.co
        SUPABASE_KEY=your-anon-key
        ```
        
        **For Streamlit Cloud:**
        1. Go to your app's Settings (⋮ menu → Settings)
        2. Navigate to "Secrets" tab
        3. Add your Supabase credentials in TOML format
        """)
        st.stop()
    except ConnectionError as e:
        # DNS/Network errors
        st.error(f"❌ Connection Error: {e}")
        st.info("💡 **Tip:** Check your internet connection and verify your Supabase URL is correct.")
        st.stop()
    except Exception as e:
        # Other errors
        error_msg = str(e)
        if "Name or service not known" in error_msg or "[Errno -2]" in error_msg:
            st.error(f"❌ DNS Resolution Error: Cannot resolve Supabase hostname")
            st.info("""
            **This usually means:**
            1. Your SUPABASE_URL might be incorrect
            2. Your internet connection is down
            3. The Supabase project might be paused or deleted
            
            **To fix:**
            - Verify your SUPABASE_URL in `.env` file (local) or Streamlit Secrets (cloud)
            - Check your internet connection
            - Verify your Supabase project is active
            """)
        else:
            st.error(f"❌ Error fetching particulars: {e}")
            st.info("💡 **Tip:** Check your internet connection and try refreshing the page.")
        st.stop()

    # Fetch brands (cached) - optimized for mobile
    try:
        db_brands = fetch_brands()
        if not db_brands:
            st.error("❌ No brands found in database. Please contact your administrator.")
            st.stop()
        
        # Brand and location columns
        col_brand, col_location = st.columns(2)
        
        with col_brand:
            brand_name = st.selectbox(
                "🏷️ Brand Name", 
                db_brands, 
                index=0,
                help="Select the brand for your configuration"
            )
        
        with col_location:
            location_type = st.selectbox(
                "📍 Location Type", 
                ["indoor", "outdoor", "both"], 
                index=0,
                help="Select the location type for your configuration"
            )
    except ValueError as e:
        # Configuration errors (missing env vars, invalid URL format)
        st.error(f"❌ Configuration Error: {e}")
        st.info("""
        **To fix this issue:**
        
        **For Local Development:**
        1. Create a `.env` file in the project root
        2. Add your Supabase credentials:
        ```
        SUPABASE_URL=https://ldatmittxoudwpcgdcbc.supabase.co
        SUPABASE_KEY=your-anon-key
        ```
        
        **For Streamlit Cloud:**
        1. Go to your app's Settings (⋮ menu → Settings)
        2. Navigate to "Secrets" tab
        3. Add your Supabase credentials in TOML format
        """)
        st.stop()
    except ConnectionError as e:
        # DNS/Network errors
        st.error(f"❌ Connection Error: {e}")
        st.info("💡 **Tip:** Check your internet connection and verify your Supabase URL is correct.")
        st.stop()
    except Exception as e:
        # Other errors
        error_msg = str(e)
        if "Name or service not known" in error_msg or "[Errno -2]" in error_msg:
            st.error(f"❌ DNS Resolution Error: Cannot resolve Supabase hostname")
            st.info("""
            **This usually means:**
            1. Your SUPABASE_URL might be incorrect
            2. Your internet connection is down
            3. The Supabase project might be paused or deleted
            
            **To fix:**
            - Verify your SUPABASE_URL in `.env` file (local) or Streamlit Secrets (cloud)
            - Check your internet connection
            - Verify your Supabase project is active
            """)
        else:
            st.error(f"❌ Error fetching brands: {e}")
            st.info("💡 **Tip:** Check your internet connection and try refreshing the page.")
        st.stop()

    if particular == "Drivers":
        render_driver_form(brand_name, location_type)
    elif particular == "LED strips":
        st.info("🚧 **LED Strips Functionality**\n\nThis feature is coming soon. Stay tuned!")

    render_table()
