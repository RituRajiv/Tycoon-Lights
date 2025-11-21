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

# Page configuration
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

# Apply custom styles
st.markdown(get_custom_styles(), unsafe_allow_html=True)

# JavaScript injection for hiding rerun button
import streamlit.components.v1 as components

hide_rerun_html = """
<script>
(function() {
    let isRunning = false;
    let lastRunTime = 0;
    const DEBOUNCE_MS = 500; // Debounce to prevent excessive calls
    
    function hideRerun() {
        // Prevent concurrent executions
        const now = Date.now();
        if (isRunning || (now - lastRunTime) < DEBOUNCE_MS) {
            return;
        }
        
        isRunning = true;
        lastRunTime = now;
        
        try {
            // Hide toolbar
            const toolbar = document.querySelector('[data-testid="stToolbar"]');
            if (toolbar && toolbar.isConnected) {
                toolbar.style.display = 'none';
                toolbar.style.visibility = 'hidden';
                toolbar.remove();
            }
            
            // Hide header
            const header = document.querySelector('header[data-testid="stHeader"]');
            if (header && header.isConnected) {
                header.style.display = 'none';
            }
            
            // Hide header/toolbar buttons
            const headerButtons = document.querySelectorAll('header button, [data-testid="stToolbar"] button');
            headerButtons.forEach(btn => {
                if (btn.isConnected) {
                    btn.style.display = 'none';
                    btn.remove();
                }
            });
        } catch (e) {
            // Silently fail
        } finally {
            isRunning = false;
        }
    }
    
    // Run immediately
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hideRerun);
    } else {
        hideRerun();
    }
    
    // Run after delay
    setTimeout(hideRerun, 100);
    
    // Watch for toolbar/header additions
    let observerTimeout;
    const observer = new MutationObserver(function(mutations) {
        clearTimeout(observerTimeout);
        observerTimeout = setTimeout(() => {
            const hasToolbar = document.querySelector('[data-testid="stToolbar"]');
            const hasHeader = document.querySelector('header[data-testid="stHeader"]');
            if (hasToolbar || hasHeader) {
                hideRerun();
            }
        }, 200);
    });
    
    // Observe direct children only
    if (document.body) {
        observer.observe(document.body, { 
            childList: true, 
            subtree: false
        });
    }
    
    // Clean up on unload
    window.addEventListener('beforeunload', () => {
        observer.disconnect();
    });
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
    # Fetch particulars (cached)
    try:
        with st.spinner("Loading..."):
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
    except Exception as e:
        st.error(f"❌ Error fetching particulars: {e}")
        st.info("💡 **Tip:** Check your internet connection and try refreshing the page.")
        st.stop()

    # Fetch brands (cached)
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
    except Exception as e:
        st.error(f"❌ Error fetching brands: {e}")
        st.info("💡 **Tip:** Check your internet connection and try refreshing the page.")
        st.stop()

    if particular == "Drivers":
        render_driver_form(brand_name, location_type)
    elif particular == "LED strips":
        st.info("🚧 **LED Strips Functionality**\n\nThis feature is coming soon. Stay tuned!")

    render_table()
