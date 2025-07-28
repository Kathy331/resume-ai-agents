# ui/pages/4_email_generator.py
import streamlit as st
from components.sidebar import show_sidebar

def show_email_generator():
    st.title("Email Generator")
    st.subheader("Smart Email Writer")
    
    email_types = ["Thank You Note", "Follow-up", "Reschedule Request", "Networking"]
    selected_type = st.selectbox("Email Type", email_types)
    
    # Context from vector store
    context_available = st.checkbox("Use personal tone context", value=True)
    
    if st.button("Generate Email", type="primary"):
        with st.spinner("Crafting personalized email..."):
            st.subheader("Generated Email")
            email_content = """Dear Sarah,

Thank you for the opportunity to interview for the Data Scientist position at Meta. I enjoyed learning more about the team's work on AI-driven recommendation systems and am excited about the possibility of contributing to such innovative projects.

I look forward to our discussion and hope we can find a time that works for both of our schedules.

Best regards,
John"""
            st.text_area("", email_content, height=200)
            col1, col2 = st.columns(2)
            with col1:
                st.button("Send via Gmail")
            with col2:
                st.button("Regenerate")

show_sidebar()
show_email_generator()