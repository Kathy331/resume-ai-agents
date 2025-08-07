import streamlit as st
import tempfile
import pandas as pd
from datetime import datetime
from agents.resume_analyzer.agent import ResumeAnalyzerAgent
from agents.base_agent import AgentInput
import asyncio
import json


def render_resume_pipeline():
    """Render the resume processing pipeline page"""
    
    st.title("📄 Resume Processing Pipeline")
    st.markdown("Upload, process, and manage your resume data for personalized interview prep")
    
    # Resume Upload Section
    st.markdown("### 📤 Resume Upload")
    
    upload_col1, upload_col2 = st.columns([2, 1])
    
    with upload_col1:
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT. Max size: 10MB"
        )
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            # File info
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.1f} KB",
                "File type": uploaded_file.type
            }
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                file_path = tmp_file.name
            # Set up Agent
            analyzer = ResumeAnalyzerAgent(config={})
            input_data = AgentInput(data={"file_path": file_path})

            if st.button("Analyze Resume"):
                with st.spinner("Processing resume..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(analyzer.execute(input_data))

                    if result.success:
                        st.success("Analysis Complete!")
                        # Store raw data in session state
                        st.session_state["resume_analysis_result"] = result.data

                        # TODO: delete later... Optionally display for debugging
                        st.json(result.data) 
                    else:
                        st.error(f"Error: {result.errors}")
                    
                    st.success("✅ Resume processed successfully!")
                    st.session_state['resume_processed'] = True
                    st.session_state['resume_data'] = {
                        "filename": uploaded_file.name,
                        "processed_at": datetime.now().isoformat()
                    }

    with upload_col2:
        st.markdown("**📋 Processing Steps**")
        
        steps = [
            {"step": "File Upload", "status": "✅" if uploaded_file else "⏳", "desc": "Upload resume file"},
            {"step": "Text Extraction", "status": "⏳", "desc": "Extract text from document"},
            {"step": "NER Processing", "status": "⏳", "desc": "Identify entities"},
            {"step": "Structure Analysis", "status": "⏳", "desc": "Parse sections"},
            {"step": "Memory Storage", "status": "⏳", "desc": "Store in knowledge base"}
        ]
        
        for step in steps:
            st.markdown(f"{step['status']} **{step['step']}**")
            st.markdown(f"<small>{step['desc']}</small>", unsafe_allow_html=True)
            st.markdown("")
    
    st.markdown("---")
    
    # Resume Analysis Results
    if st.session_state.get('resume_processed', False):
        st.markdown("### 🧠 Resume Analysis Results")
        
        # Tabs for different analysis views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🛠️ Skills", "💼 Experience", "🎓 Education"])

        analysis_data = st.session_state.get("resume_analysis_result", {})
        
        with tab1:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)

            chunks = analysis_data.get("chunks", [])
            
            with col1:
                st.metric("📝 Total Sections", len(analysis_data.get("chunks", [])))
            with col2:
                keywords = analysis_data.get("extracted_keywords", "")
                st.metric("🛠️ Skills Found", len([k.strip() for k in keywords.split(",") if k.strip()]))
            with col3:
                experience_count = sum(len(chunk.get("experience", [])) for chunk in chunks)
                st.metric("💼 Work Experience", experience_count)
            with col4:
                education_count = sum(len(chunk.get("education", [])) for chunk in chunks)
                st.metric("🎓 Education", education_count)
            
            # Resume quality score
            st.markdown("#### 🎯 Resume Quality Analysis")
            
            # TODO: Dont need this
            quality_metrics = {
                "Overall Score": 85,
                "Clarity": 90,
                "Completeness": 80,
                "ATS Compatibility": 88,
                "Keyword Density": 75
            }
            
            for metric, score in quality_metrics.items():
                st.progress(score / 100, text=f"{metric}: {score}/100")
        
        with tab2:
            st.markdown("#### 🛠️ Extracted Skills")
            
            for i, chunk in enumerate(chunks):
                st.markdown(f"**Resume Chunk {i + 1} - {chunk.get('name', 'Unnamed')}**")
                
                skills = chunk.get("skills", [])
                if skills and isinstance(skills[0], dict):  # Categorized
                    for category_block in skills:
                        category = category_block.get("category", "General")
                        skills_list = category_block.get("skills", [])
                        st.markdown(f"- **{category}**: {', '.join(skills_list)}")
                elif skills:  # Flat skill list
                    st.markdown(", ".join(skills))
                else:
                    st.markdown("_No skills found._")
        
        with tab3:
            st.markdown("#### 💼 Work Experience Timeline")
            
            for i, chunk in enumerate(chunks):
                for exp in chunk.get("experience", []):
                    st.markdown(f"""
                    <div style="
                        padding: 1rem;
                        margin-bottom: 1rem;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        background-color: white;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <div>
                                <strong style="font-size: 1.1rem;">{exp.get('title', 'Unknown Role')}</strong><br>
                                <span style="color: #3b82f6; font-weight: 500;">{exp.get('company', '')}</span>
                            </div>
                            <span style="color: #6b7280; font-size: 0.9rem;">{exp.get('dates') or f"{exp.get('start_date', '')} – {exp.get('end_date', '')}"}</span>
                        </div>
                        
                        <p style="margin: 0.5rem 0; color: #4b5563;">{exp.get('description', '')}</p>
                        
                        <div style="margin: 0.5rem 0;">
                            <strong>Key Responsibilities:</strong>
                            <ul style="margin: 0.25rem 0;">
                                {''.join([f'<li>{resp}</li>' for resp in exp.get('responsibilities', [])])}
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown("#### 🎓 Education Background")
            
            for i, chunk in enumerate(chunks):
                for edu in chunk.get("education", []):
                    st.markdown(f"""
                    <div style="
                        padding: 1rem;
                        margin-bottom: 1rem;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        background-color: white;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <div>
                                <strong style="font-size: 1.1rem;">{edu.get('degree', 'Degree')}</strong><br>
                                <span style="color: #3b82f6; font-weight: 500;">{edu.get('institution', 'Institution')}</span>
                            </div>
                            <div style="text-align: right; color: #6b7280; font-size: 0.9rem;">
                                <div>{edu.get('graduation_date', '')}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        st.info("📤 Upload and process a resume to see analysis results")
    
    st.markdown("---")
    
    # Behavioral Interview Prep Generation
    if st.session_state.get('resume_processed', False):
        st.markdown("### 🎭 Behavioral Interview Preparation")
        
        st.markdown("""
        Generate personalized STAR framework answers based on your resume experience.
        """)
        
        # Common behavioral questions
        behavioral_questions = [
            "Tell me about a time you had to overcome a significant challenge",
            "Describe a situation where you had to work with a difficult team member",
            "Give an example of when you had to learn something new quickly",
            "Tell me about a time you made a mistake and how you handled it",
            "Describe your greatest professional achievement",
            "Tell me about a time you had to meet a tight deadline",
            "Give an example of when you showed leadership",
            "Describe a time you had to adapt to change"
        ]
        
        selected_question = st.selectbox("Select a behavioral question:", behavioral_questions)
        
        if st.button("🎯 Generate STAR Answer", type="primary"):
            with st.spinner("Generating personalized answer..."):
                # Mock STAR answer generation
                st.markdown("#### 📝 Generated STAR Answer")
                
                star_answer = {
                    "Situation": "At Tech Corp, our main product API was experiencing 300% increased load during peak hours, causing frequent timeouts and affecting 50,000+ users daily.",
                    
                    "Task": "As the Senior Software Engineer, I was tasked with identifying the bottleneck and implementing a solution within 2 weeks to prevent customer churn during our busy season.",
                    
                    "Action": "I conducted a comprehensive performance analysis using monitoring tools, identified database queries as the primary bottleneck, implemented database indexing and query optimization, introduced Redis caching for frequently accessed data, and set up automated monitoring alerts.",
                    
                    "Result": "Reduced API response time by 75% (from 2.5s to 0.6s average), eliminated timeout errors completely, improved system reliability to 99.9% uptime, and saved the company an estimated $200K in potential lost revenue."
                }
                
                for component, content in star_answer.items():
                    st.markdown(f"""
                    <div style="
                        padding: 0.75rem;
                        margin-bottom: 0.5rem;
                        border-left: 4px solid #10b981;
                        background-color: #f0fdf4;
                        border-radius: 0 5px 5px 0;
                    ">
                        <strong style="color: #059669;">{component}:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Self-reflection and improvement
                st.markdown("#### 🔍 Answer Analysis & Suggestions")
                
                feedback = {
                    "Strengths": [
                        "Specific metrics and quantifiable results",
                        "Clear problem-solution narrative",
                        "Demonstrates technical and leadership skills"
                    ],
                    "Improvements": [
                        "Add more detail about stakeholder communication",
                        "Mention lessons learned for future situations",
                        "Include team collaboration aspects"
                    ],
                    "Score": "8.5/10"
                }
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    st.markdown("**✅ Strengths**")
                    for strength in feedback["Strengths"]:
                        st.markdown(f"• {strength}")
                
                with col2:
                    st.markdown("**💡 Improvements**")
                    for improvement in feedback["Improvements"]:
                        st.markdown(f"• {improvement}")
                
                with col3:
                    st.markdown("**📊 Overall Score**")
                    st.markdown(f"### {feedback['Score']}")
                    st.progress(0.85)
    
    st.markdown("---")
    
    # Resume Memory Management
    st.markdown("### 🧠 Resume Memory Management")
    
    memory_col1, memory_col2 = st.columns(2)
    
    with memory_col1:
        st.markdown("**📚 Stored Information**")
        
        if st.session_state.get('resume_processed', False):
            memory_stats = {
                "Skills": 23,
                "Work Experiences": 4,
                "Projects": 6,
                "Achievements": 12,
                "Education": 2,
                "Certifications": 3
            }
            
            for category, count in memory_stats.items():
                st.markdown(f"**{category}:** {count} entries")
        else:
            st.info("No resume data in memory. Process a resume first.")
    
    with memory_col2:
        st.markdown("**⚙️ Memory Actions**")
        
        if st.button("🔄 Refresh Memory", use_container_width=True):
            st.success("Memory refreshed!")
        
        if st.button("📥 Export Memory", use_container_width=True):
            st.info("Exporting resume memory to JSON...")
        
        if st.button("🗑️ Clear Memory", use_container_width=True):
            st.warning("Resume memory cleared!")
            st.session_state['resume_processed'] = False
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #6b7280; font-size: 0.8rem;">
        Resume pipeline last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
        Memory usage: 45MB | 
        Processing accuracy: 94.2%
    </div>
    """, unsafe_allow_html=True)