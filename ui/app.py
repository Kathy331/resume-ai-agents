import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import page modules
from pages import dashboard, email_pipeline, resume_pipeline, research_engine, question_generation, settings
from components import sidebar, stats_cards, activity_feed

# Configure page
st.set_page_config(
    page_title="Interview Prep AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        padding: 1rem 0;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .status-success {
        color: #10b981;
    }
    
    .status-warning {
        color: #f59e0b;
    }
    
    .status-error {
        color: #ef4444;
    }
    
    .sidebar-section {
        margin-bottom: 2rem;
    }
    
    .activity-item {
        padding: 0.75rem;
        border-left: 3px solid #3b82f6;
        background-color: #f8fafc;
        margin-bottom: 0.5rem;
        border-radius: 0 5px 5px 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    if 'pipeline_status' not in st.session_state:
        st.session_state.pipeline_status = {
            'email_active': False,
            'resume_processed': False,
            'research_cache_size': 0,
            'last_sync': None
        }
    
    # Render sidebar
    selected_page = sidebar.render_sidebar()
    st.session_state.current_page = selected_page
    
    # Main content area
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    
    # Page routing
    if selected_page == "Dashboard":
        dashboard.render_dashboard()
    elif selected_page == "Email Pipeline":
        email_pipeline.render_email_pipeline()
    elif selected_page == "Resume Pipeline":
        resume_pipeline.render_resume_pipeline()
    elif selected_page == "Research Engine":
        research_engine.render_research_engine()
    elif selected_page == "Question Generation":
        question_generation.render_question_generation()
    elif selected_page == "Settings":
        settings.render_settings()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()