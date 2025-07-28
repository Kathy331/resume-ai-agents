import streamlit as st
from datetime import datetime

def render_sidebar():
    """Render the main sidebar with navigation and status"""
    
    with st.sidebar:
        # App header
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 1.5rem;">
            <h1 style="color: #3b82f6; margin: 0; font-size: 1.5rem;">🎯 Interview AI</h1>
            <p style="color: #6b7280; margin: 0; font-size: 0.8rem;">Intelligent Prep Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Status Overview
        st.markdown("### 📊 System Status")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.get('pipeline_status', {}).get('email_active', False):
                st.markdown('<span class="status-success">📧 Email Active</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-warning">📧 Email Inactive</span>', unsafe_allow_html=True)
        
        with col2:
            if st.session_state.get('pipeline_status', {}).get('resume_processed', False):
                st.markdown('<span class="status-success">📄 Resume Ready</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-warning">📄 No Resume</span>', unsafe_allow_html=True)
        
        # Cache status
        cache_size = st.session_state.get('pipeline_status', {}).get('research_cache_size', 0)
        st.metric("🧠 Research Cache", f"{cache_size} entries")
        
        st.markdown("---")
        
        # Main Navigation
        st.markdown("### 🧭 Navigation")
        
        # Navigation options
        nav_options = [
            ("🏠 Dashboard", "Dashboard"),
            ("📧 Email Pipeline", "Email Pipeline"),
            ("📄 Resume Pipeline", "Resume Pipeline"),
            ("🔬 Research Engine", "Research Engine"),
            ("❓ Question Generation", "Question Generation"),
            ("⚙️ Settings", "Settings")
        ]
        
        selected_page = st.radio(
            "Choose a section:",
            options=[option[1] for option in nav_options],
            format_func=lambda x: next(option[0] for option in nav_options if option[1] == x),
            key="navigation_radio"
        )
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Sync Gmail", use_container_width=True):
                st.session_state['trigger_email_sync'] = True
                st.success("Syncing emails...")
        
        with col2:
            if st.button("🧹 Clear Cache", use_container_width=True):
                st.session_state['trigger_cache_clear'] = True
                st.success("Cache cleared!")
        
        # Manual trigger for interview prep
        if st.button("🎯 Run Interview Prep", use_container_width=True, type="primary"):
            st.session_state['trigger_interview_prep'] = True
            st.success("Starting interview prep...")
        
        st.markdown("---")
        
        # Pipeline Health
        st.markdown("### 🏥 Pipeline Health")
        
        # Email pipeline status
        email_status = "🟢 Active" if st.session_state.get('email_pipeline_active') else "🔴 Inactive"
        st.markdown(f"**Email Pipeline:** {email_status}")
        
        # Resume pipeline status
        resume_status = "🟢 Ready" if st.session_state.get('resume_pipeline_ready') else "🟡 Pending"
        st.markdown(f"**Resume Pipeline:** {resume_status}")
        
        # Research engine status
        research_status = "🟢 Online" if st.session_state.get('research_engine_online') else "🔴 Offline"
        st.markdown(f"**Research Engine:** {research_status}")
        
        st.markdown("---")
        
        # Recent Activity Preview
        st.markdown("### 📈 Recent Activity")
        
        recent_activities = st.session_state.get('recent_activities', [
            {"type": "email", "message": "Processed interview email", "time": "2 hours ago"},
            {"type": "research", "message": "Researched Google Inc.", "time": "4 hours ago"},
            {"type": "questions", "message": "Generated 15 questions", "time": "6 hours ago"}
        ])
        
        for activity in recent_activities[:3]:  # Show only last 3
            icon = {"email": "📧", "research": "🔬", "questions": "❓", "resume": "📄"}.get(activity["type"], "📝")
            st.markdown(f"""
            <div class="activity-item">
                <small><strong>{icon} {activity['message']}</strong></small><br>
                <small style="color: #6b7280;">{activity['time']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Footer info
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; color: #6b7280; font-size: 0.7rem;">
            <p>Last updated: {}</p>
            <p>Version 1.0.0-beta</p>
        </div>
        """.format(datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)
    
    return selected_page