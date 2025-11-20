"""Custom CSS styles for the Streamlit app"""

def get_custom_styles():
    """Returns custom CSS as HTML string"""
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
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
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
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
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