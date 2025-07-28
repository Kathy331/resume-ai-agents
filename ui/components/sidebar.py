# ui/components/sidebar.py
import streamlit as st

def show_sidebar():
    with st.sidebar:
        st.title("Resume Interview Prep Agent")
        
        # Navigation - FIXED: Use buttons instead of page_link
        st.markdown("## Navigation")
        if st.button("🏠 Dashboard"):
            # Stay on current page or show info
            st.info("You are on the Dashboard page")
        
        if st.button("📄 Resume Analyzer"):
            st.switch_page("../pages/2_resume_analyzer.py")
            
        if st.button("🎯 Interview Prep"):
            st.switch_page("pages/3_interview_prep.py")
            
        if st.button("📧 Email Generator"):
            st.switch_page("pages/4_email_generator.py")
            
        if st.button("📚 History"):
            st.switch_page("pages/5_history.py")
        
        # Quick Actions
        st.markdown("## Quick Actions")
        if st.button("📥 Fetch Gmail"):
            st.success("Fetching emails...")
        
        if st.button("🔄 Refresh Data"):
            st.success("Data refreshed!")
        
        # Settings
        st.markdown("## Settings")
        auto_prep = st.checkbox("Auto-generate prep", value=True)
        email_notif = st.checkbox("Email notifications", value=True)
        confidence = st.slider("Confidence threshold", 0, 100, 80)
        
        # Store settings in session state
        st.session_state.auto_prep = auto_prep
        st.session_state.email_notif = email_notif
        st.session_state.confidence_threshold = confidence