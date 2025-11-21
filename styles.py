"""Custom CSS styles for the Streamlit app"""

import streamlit as st

@st.cache_data
def get_custom_styles():
    """Returns custom CSS as HTML string (cached for performance)"""
    return """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta http-equiv="Permissions-Policy" content="accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), clipboard-write=(), document-domain=(), encrypted-media=(), gyroscope=(), layout-animations=(), legacy-image-formats=(), magnetometer=(), midi=(), oversized-images=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), sync-xhr=(), usb=(), vr=(), wake-lock=(), xr-spatial-tracking=()">
<script>
(function() {
    'use strict';
    
    // Suppress Feature Policy warnings (deprecated API)
    const originalWarn = console.warn;
    console.warn = function(...args) {
        const message = args.join(' ');
        if (message.includes('Feature Policy: Skipping unsupported feature name')) {
            return; // Suppress Feature Policy warnings
        }
        if (message.includes('Some cookies are misusing the recommended "SameSite" attribute')) {
            return; // Suppress SameSite cookie warnings
        }
        if (message.includes('preloaded with link preload was not used')) {
            return; // Suppress preload warnings
        }
        if (message.includes('iframe which has both allow-scripts and allow-same-origin')) {
            return; // Suppress iframe sandbox warnings
        }
        originalWarn.apply(console, args);
    };
    
    // Suppress WebSocket onclose errors (non-critical)
    const originalError = console.error;
    console.error = function(...args) {
        const message = args.join(' ');
        if (message.includes('WebSocket') && message.includes('onclose')) {
            return; // Suppress WebSocket onclose errors
        }
        originalError.apply(console, args);
    };
    
    // Handle WebSocket errors gracefully
    window.addEventListener('error', function(e) {
        if (e.message && e.message.includes('WebSocket')) {
            e.preventDefault();
            return false;
        }
    }, true);
    
    // Suppress unhandled promise rejections from WebSocket
    window.addEventListener('unhandledrejection', function(e) {
        if (e.reason && typeof e.reason === 'string' && e.reason.includes('WebSocket')) {
            e.preventDefault();
            return false;
        }
    });
})();
</script>
<style>
    /* Hide Streamlit header */
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    
    /* Hide rerun button and toolbar - comprehensive selectors */
    button[title="Rerun"],
    button[kind="header"][title="Rerun"],
    [data-testid="stToolbar"] button[title="Rerun"],
    .stToolbar button[title="Rerun"],
    header button[title="Rerun"],
    button[aria-label*="Rerun"],
    button[aria-label*="rerun"],
    button[title*="Rerun" i],
    button[title*="Rerun"],
    [data-testid="stToolbar"] > div > button:first-child,
    [data-testid="stToolbar"] button:first-of-type,
    [data-testid="stToolbar"] button,
    button svg + span,
    [data-testid="stToolbar"],
    /* Hide all buttons in header area */
    header button,
    header [role="button"],
    /* Hide toolbar container */
    [data-testid="stToolbar"],
    [data-testid="stToolbar"] *,
    /* Hide any element with rerun in class or id */
    [class*="rerun" i],
    [id*="rerun" i],
    /* Hide top-right corner buttons */
    .stApp > header,
    .stApp > header * {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }
    
    /* Prevent horizontal scroll on mobile */
    html, body {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    
    /* Main background */
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        min-height: 100vh;
        width: 100% !important;
        max-width: 100% !important;
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
            padding: 0.5rem !important;
        }
        
        /* Ensure all containers fit mobile */
        .block-container {
            padding: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Fix column layouts on mobile */
        [data-testid="column"] {
            width: 100% !important;
            padding: 0.25rem !important;
        }
        
        /* Make buttons touch-friendly */
        .stButton > button {
            min-height: 44px !important;
            font-size: 16px !important;
        }
        
        /* Fix selectboxes on mobile */
        .stSelectbox {
            width: 100% !important;
        }
        
        /* Prevent text overflow */
        * {
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }
        
        /* Fix table scrolling */
        .table-container {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
    }
    
    /* Extra small devices */
    @media (max-width: 480px) {
        .main {
            padding: 0.25rem !important;
        }
        
        .block-container {
            padding: 0.5rem !important;
        }
    }
</style>
"""