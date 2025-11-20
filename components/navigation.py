"""Navigation bar component"""

import streamlit as st


def render_navigation():
    """Render navigation bar with menu items - only shown when logged in"""
    # Check authentication - navigation should only be rendered when logged in
    is_logged_in = st.session_state.get('supabase_user') is not None
    if not is_logged_in:
        return  # Don't render navigation if not logged in
    
    current_page = st.session_state.get('current_page', 'Home')
    
    # Get user email for display
    user_email = None
    if st.session_state.get('supabase_user'):
        user_email = getattr(st.session_state.supabase_user, 'email', 'User')
    
    # Responsive navigation columns - stack on mobile
    nav_cols = st.columns([2, 1, 1, 1, 1.5], gap="small")
    
    with nav_cols[0]:
        st.markdown("""
        <div style='display: flex; align-items: center; gap: 0.5rem;'>
            <span style='font-size: 1.5rem;'>💡</span>
            <h3 style='margin: 0; color: #f1f5f9; font-weight: 700;'>Tycoon Lights</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with nav_cols[1]:
        button_type = "primary" if current_page == "Home" else "secondary"
        if st.button("🏠 Home", use_container_width=True, key="nav_home", type=button_type):
            st.session_state.current_page = "Home"
            st.rerun()
    
    with nav_cols[2]:
        button_type = "primary" if current_page == "Upload PDF" else "secondary"
        if st.button("📄 Upload", use_container_width=True, key="nav_upload", type=button_type):
            st.session_state.current_page = "Upload PDF"
            st.rerun()
    
    with nav_cols[3]:
        if st.button("🔄 Rerun", use_container_width=True, key="nav_rerun", help="Refresh the page", type="secondary"):
            st.rerun()
    
    with nav_cols[4]:
        col_user, col_logout = st.columns([2, 1])
        with col_user:
            if user_email:
                st.markdown(f"""
                <div style='display: flex; align-items: center; height: 100%; padding: 0.5rem 0;'>
                    <small style='color: #cbd5e1; font-size: 0.75rem;'>👤 {user_email.split("@")[0]}</small>
                </div>
                """, unsafe_allow_html=True)
        with col_logout:
            if st.button("Logout", use_container_width=True, key="nav_logout", help="Logout", type="secondary"):
                from components.login import logout_user
                logout_user()
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

