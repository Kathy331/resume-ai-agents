# ui/components/dashboard.py
import streamlit as st

def show_dashboard():
    st.title("Resume Interview Prep Agent")
    st.subheader("AI-Powered Interview Preparation Dashboard")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Interviews Analyzed", "24", "12%")
    col2.metric("Questions Generated", "156", "8%")
    col3.metric("Emails Sent", "18", "2%")
    col4.metric("Success Rate", "89%", "3%")
    
    # Recent Activity
    st.markdown("## Recent Activity")
    st.info("New interview detected: Meta Data Scientist - Sarah Johnson")
    st.success("Prep materials generated for Google SWE interview")
    st.warning("Reminder: LinkedIn follow-up due tomorrow")
    
    # Quick Actions
    st.markdown("## Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Fetch New Emails"):
            st.success("Fetching emails...")
    with col2:
        if st.button("Analyze Resume"):
            st.switch_page("pages/2_resume_analyzer.py")
    with col3:
        if st.button("Generate Email"):
            st.switch_page("pages/4_email_generator.py")