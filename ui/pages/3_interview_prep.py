# ui/pages/3_interview_prep.py
import streamlit as st
from components.sidebar import show_sidebar

def show_interview_prep():
    st.title("Interview Preparation")
    st.subheader("AI-Powered Question Generation")
    
    # Interview details
    col1, col2 = st.columns(2)
    with col1:
        interviewer = st.text_input("Interviewer Name", "Sarah Johnson")
        company = st.text_input("Company", "Meta")
    with col2:
        role = st.text_input("Role", "Data Scientist")
        date = st.date_input("Interview Date")
    
    if st.button("Generate Prep Materials", type="primary"):
        with st.spinner("AI analyzing and generating prep..."):
            # Technical Questions
            st.subheader("Technical Questions")
            questions = [
                "Explain the bias-variance tradeoff in machine learning",
                "How would you handle missing data in a dataset?",
                "Describe the difference between supervised and unsupervised learning"
            ]
            for i, q in enumerate(questions, 1):
                st.markdown(f"{i}. {q}")
            
            # Behavioral Questions
            st.subheader("Behavioral Questions")
            behavioral = [
                "Tell me about a time you had to work with difficult stakeholders",
                "Describe a situation where you had to make a decision with incomplete information"
            ]
            for i, q in enumerate(behavioral, 1):
                st.markdown(f"{i}. {q}")
            
            st.success("Prep materials generated successfully!")
            st.button("Send to Email", type="secondary")

show_sidebar()
show_interview_prep()