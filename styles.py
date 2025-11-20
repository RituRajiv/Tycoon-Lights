"""Custom CSS styles for the Streamlit app"""

import streamlit as st

@st.cache_data
def get_custom_styles():
    """Returns custom CSS as HTML string (cached for performance)"""
    return """
<style>
    /* Hide Streamlit header */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Main background */
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        min-height: 100vh;
    }
    
    /* Typography - will be overridden by login form styles */
    .main h1,
    .main h2,
    .main h3,
    .main h4,
    .main h5,
    .main h6 {
        color: #f1f5f9 !important;
    }
    
    /* Navigation Bar */
    .nav-container {
        background: #1e293b;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
    }
    
    /* Form Elements - Dark theme for main app */
    .stSelectbox > div > div > select {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
    /* Login form inputs will be styled separately in login.py */
    
    /* Table Container */
    .table-container {
        background: #1e293b;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        overflow-x: auto;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
    }
</style>
"""