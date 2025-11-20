# Main Streamlit application

import streamlit as st
from styles import get_custom_styles
from session_state import initialize_session_state
from components.navigation import render_navigation
from components.driver_form import render_driver_form
from components.table_display import render_table
from components.pdf_upload import render_pdf_upload
from components.login import render_login
from supabase_client import fetch_particulars, fetch_brands

# Page configuration for mobile and desktop
st.set_page_config(
    page_title="Tycoon Lights",
    page_icon="💡",
    layout="wide",  # Streamlit handles mobile responsiveness automatically
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Apply custom styles
st.markdown(get_custom_styles(), unsafe_allow_html=True)

# Use components API for more reliable JavaScript injection
import streamlit.components.v1 as components

hide_rerun_html = """
<script>
(function() {
    let isRunning = false;
    let lastRunTime = 0;
    const DEBOUNCE_MS = 500; // Debounce to prevent excessive calls
    
    function hideRerun() {
        // Prevent concurrent executions and debounce
        const now = Date.now();
        if (isRunning || (now - lastRunTime) < DEBOUNCE_MS) {
            return;
        }
        
        isRunning = true;
        lastRunTime = now;
        
        try {
            // Hide entire toolbar (most efficient - single operation)
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
            
            // Only check buttons in header/toolbar area (more efficient)
            const headerButtons = document.querySelectorAll('header button, [data-testid="stToolbar"] button');
            headerButtons.forEach(btn => {
                if (btn.isConnected) {
                    btn.style.display = 'none';
                    btn.remove();
                }
            });
        } catch (e) {
            // Silently fail to prevent console errors
        } finally {
            isRunning = false;
        }
    }
    
    // Run once immediately
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hideRerun);
    } else {
        hideRerun();
    }
    
    // Run once after a short delay
    setTimeout(hideRerun, 100);
    
    // Use a more efficient MutationObserver - only watch for toolbar/header additions
    let observerTimeout;
    const observer = new MutationObserver(function(mutations) {
        // Debounce observer callbacks
        clearTimeout(observerTimeout);
        observerTimeout = setTimeout(() => {
            // Only check if toolbar or header was added
            const hasToolbar = document.querySelector('[data-testid="stToolbar"]');
            const hasHeader = document.querySelector('header[data-testid="stHeader"]');
            if (hasToolbar || hasHeader) {
                hideRerun();
            }
        }, 200);
    });
    
    // Only observe direct children of body, not entire subtree (much more efficient)
    if (document.body) {
        observer.observe(document.body, { 
            childList: true, 
            subtree: false  // Changed from true - only watch direct children
        });
    }
    
    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        observer.disconnect();
    });
})();
</script>
"""
components.html(hide_rerun_html, height=0)

# Initialize session state
initialize_session_state()

# Check authentication status
is_logged_in = st.session_state.get('supabase_user') is not None
current_page = st.session_state.get('current_page', 'Home')

# If not logged in, only allow access to login page
if not is_logged_in:
    if current_page != "Login":
        st.session_state.current_page = "Login"
        st.rerun()
    # Render login page without navigation
    render_login()
    st.stop()

# User is logged in - render navigation bar
render_navigation()

# Handle page navigation (only accessible when logged in)
if current_page == "Login":
    # If logged in and on login page, redirect to home
    st.session_state.current_page = "Home"
    st.rerun()
elif current_page == "Upload PDF":
    render_pdf_upload()
    st.stop()
else:
    # Home page - Main functionality
    # Fetch particulars from database (cached)
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

    # Fetch brand names from database (cached)
    try:
        db_brands = fetch_brands()
        if not db_brands:
            st.error("❌ No brands found in database. Please contact your administrator.")
            st.stop()
        brand_name = st.selectbox(
            "🏷️ Brand Name", 
            db_brands, 
            index=0,
            help="Select the brand for your configuration"
        )
    except Exception as e:
        st.error(f"❌ Error fetching brands: {e}")
        st.info("💡 **Tip:** Check your internet connection and try refreshing the page.")
        st.stop()

    if particular == "Drivers":
        render_driver_form(brand_name)
    elif particular == "LED strips":
        st.info("🚧 **LED Strips Functionality**\n\nThis feature is coming soon. Stay tuned!")

    render_table()
