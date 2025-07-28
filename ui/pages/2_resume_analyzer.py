# ui/pages/2_resume_analyzer.py
import streamlit as st
from components.sidebar import show_sidebar

def show_resume_analyzer():
    st.title("Resume Analyzer")
    st.subheader("Multi-Modal Resume Intelligence")
    
    uploaded_file = st.file_uploader("Upload your resume (PDF/DOC)", 
                                    type=['pdf', 'doc', 'docx'])
    
    if uploaded_file:
        st.success("Resume uploaded successfully!")
        
        # Analysis sections
        with st.expander("Extracted Information", expanded=True):
            st.write("**Name:** John Doe")
            st.write("**Experience:** 5 years in Software Engineering")
            st.write("**Skills:** Python, React, Docker, AWS")
        
        with st.expander("Job Description Alignment"):
            jd_text = st.text_area("Paste Job Description", height=150)
            if st.button("Analyze Match"):
                st.progress(85)
                st.success("85% match with Software Engineer role")
                st.info("Tip: Highlight your AWS certification more prominently")
        
        with st.expander("Skills Analysis"):
            st.bar_chart({"Technical": 85, "Leadership": 78, "Communication": 92})

show_sidebar()
show_resume_analyzer()