import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

def render_email_pipeline():
    """Render the email pipeline management page"""
    
    st.title("📧 Email Pipeline Management")
    st.markdown("Monitor and control your email processing pipeline")
    
    # Pipeline Control Panel
    st.markdown("### 🎛️ Pipeline Control")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pipeline_active = st.session_state.get('email_pipeline_active', False)
        if st.button("🟢 Start Pipeline" if not pipeline_active else "🔴 Stop Pipeline", 
                    use_container_width=True,
                    type="primary" if not pipeline_active else "secondary"):
            st.session_state['email_pipeline_active'] = not pipeline_active
            status = "started" if not pipeline_active else "stopped"
            st.success(f"Email pipeline {status}!")
    
    with col2:
        if st.button("🔄 Manual Sync", use_container_width=True):
            st.info("Manually syncing Gmail...")
            st.session_state['manual_sync_triggered'] = True
    
    with col3:
        if st.button("🧹 Clear Queue", use_container_width=True):
            st.warning("Email queue cleared!")
            st.session_state['email_queue_cleared'] = True
    
    with col4:
        if st.button("📊 Export Logs", use_container_width=True):
            st.info("Exporting pipeline logs...")
    
    st.markdown("---")
    
    # Pipeline Status Overview
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 📈 Pipeline Performance")
        
        # Pipeline stages with metrics
        stages = [
            {"name": "Gmail Fetch", "status": "Active", "processed": 245, "success_rate": 99.2, "avg_time": "1.2s"},
            {"name": "Email Classification", "status": "Active", "processed": 245, "success_rate": 96.7, "avg_time": "0.8s"},
            {"name": "Entity Extraction", "status": "Active", "processed": 67, "success_rate": 94.1, "avg_time": "1.5s"},
            {"name": "Research Engine", "status": "Active", "processed": 67, "success_rate": 91.0, "avg_time": "12.3s"},
            {"name": "Question Generation", "status": "Active", "processed": 67, "success_rate": 97.8, "avg_time": "3.2s"},
            {"name": "Email Delivery", "status": "Active", "processed": 67, "success_rate": 100.0, "avg_time": "0.5s"},
        ]
        
        df_stages = pd.DataFrame(stages)
        
        # Display pipeline stages
        for _, stage in df_stages.iterrows():
            status_color = "#10b981" if stage['status'] == "Active" else "#ef4444"
            
            st.markdown(f"""
            <div style="
                padding: 1rem;
                margin-bottom: 0.5rem;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{stage['name']}</strong>
                        <span style="color: {status_color}; margin-left: 0.5rem;">● {stage['status']}</span>
                    </div>
                    <div style="text-align: right; font-size: 0.9rem;">
                        <div>📊 {stage['processed']} processed</div>
                        <div>✅ {stage['success_rate']}% success</div>
                        <div>⏱️ {stage['avg_time']} avg</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent Email Processing Log
        st.markdown("### 📋 Recent Email Processing")
        
        # Mock email processing data
        email_data = [
            {
                "timestamp": "2024-01-15 14:30:22",
                "sender": "recruiter@google.com",
                "subject": "Interview Invitation - Software Engineer",
                "classification": "Interview Invite",
                "status": "✅ Processed",
                "prep_sent": "Yes"
            },
            {
                "timestamp": "2024-01-15 13:45:18",
                "sender": "hr@microsoft.com",
                "subject": "Technical Interview Schedule",
                "classification": "Interview Invite",
                "status": "✅ Processed",
                "prep_sent": "Yes"
            },
            {
                "timestamp": "2024-01-15 12:22:10",
                "sender": "friend@personal.com",
                "subject": "Weekend plans?",
                "classification": "Personal",
                "status": "🔄 Analyzed",
                "prep_sent": "No"
            },
            {
                "timestamp": "2024-01-15 11:15:33",
                "sender": "noreply@linkedin.com",
                "subject": "New job recommendations",
                "classification": "Promotional",
                "status": "⏭️ Skipped",
                "prep_sent": "No"
            },
            {
                "timestamp": "2024-01-15 10:48:27",
                "sender": "careers@amazon.com",
                "subject": "Final round interview details",
                "classification": "Interview Invite",
                "status": "⚠️ Error",
                "prep_sent": "Retry"
            }
        ]
        
        df_emails = pd.DataFrame(email_data)
        
        # Display email log with styling
        for _, email in df_emails.iterrows():
            status_colors = {
                "✅ Processed": "#10b981",
                "🔄 Analyzed": "#3b82f6",
                "⏭️ Skipped": "#6b7280",
                "⚠️ Error": "#ef4444"
            }
            
            classification_colors = {
                "Interview Invite": "#8b5cf6",
                "Personal": "#06b6d4",
                "Promotional": "#f59e0b"
            }
            
            status_color = status_colors.get(email['status'], "#6b7280")
            class_color = classification_colors.get(email['classification'], "#6b7280")
            
            st.markdown(f"""
            <div style="
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                border-left: 4px solid {status_color};
                background-color: #f8fafc;
                border-radius: 0 5px 5px 0;
            ">
                <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 0.5rem;">
                    <div style="flex: 1;">
                        <strong>{email['subject']}</strong><br>
                        <small>From: {email['sender']}</small><br>
                        <span style="
                            background-color: {class_color};
                            color: white;
                            padding: 0.2rem 0.5rem;
                            border-radius: 10px;
                            font-size: 0.7rem;
                        ">{email['classification']}</span>
                    </div>
                    <div style="text-align: right; font-size: 0.8rem;">
                        <div>{email['status']}</div>
                        <div>📤 Prep: {email['prep_sent']}</div>
                        <small>{email['timestamp']}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        # Pipeline Statistics
        st.markdown("### 📊 Statistics")
        
        # Key metrics
        st.metric("📧 Emails Processed Today", "23", delta="5 more than yesterday")
        st.metric("🎯 Interview Emails Found", "4", delta="2 new")
        st.metric("⚡ Avg Processing Time", "2.8s", delta="-0.3s faster")
        st.metric("✅ Success Rate", "96.7%", delta="1.2% improvement")
        
        st.markdown("---")
        
        # Gmail Connection Status
        st.markdown("### 🔗 Gmail Connection")
        
        connection_status = st.session_state