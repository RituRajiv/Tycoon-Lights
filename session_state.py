"""Session state management for the Streamlit app"""

import streamlit as st


def initialize_session_state():
    """Initialize session state variables"""
    if 'table_data' not in st.session_state:
        st.session_state.table_data = []
    
    if 'editing_row' not in st.session_state:
        st.session_state.editing_row = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"