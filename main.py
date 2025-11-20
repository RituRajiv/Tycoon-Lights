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
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Apply custom styles
st.markdown(get_custom_styles(), unsafe_allow_html=True)

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
    # Fetch particulars from database
    try:
        with st.spinner("🔄 Loading particulars..."):
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
        st.stop()

    # Fetch brand names from database
    try:
        with st.spinner("🔄 Loading brands..."):
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
        st.stop()

    if particular == "Drivers":
        render_driver_form(brand_name)
    elif particular == "LED strips":
        st.info("🚧 **LED Strips Functionality**\n\nThis feature is coming soon. Stay tuned!")

    render_table()
