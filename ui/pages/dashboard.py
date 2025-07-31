import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random

def render_dashboard():
    """Render the main dashboard page"""
    
    st.title("🎯 Interview Prep AI Dashboard")
    st.markdown("Welcome to your intelligent interview preparation assistant!")
    
    # Key Metrics Row
    st.markdown("### 📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📧 Total Interviews",
            value="12",
            delta="3 this week",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="✅ Completed Preps",
            value="9",
            delta="75% success rate",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="🔬 Companies Researched",
            value="8",
            delta="2 new this week",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="❓ Questions Generated",
            value="156",
            delta="24 today",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # Main content in two columns
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Pipeline Status Overview
        st.markdown("### 🔄 Pipeline Status")
        
        # Create pipeline status chart
        pipeline_data = {
            'Pipeline': ['Email Classification', 'Entity Extraction', 'Company Research', 'Question Generation', 'Prep Summary'],
            'Status': ['Active', 'Active', 'Active', 'Active', 'Active'],
            'Last Run': ['2 min ago', '2 min ago', '5 min ago', '3 min ago', '1 min ago'],
            'Success Rate': [98, 95, 92, 97, 99]
        }
        
        df_pipeline = pd.DataFrame(pipeline_data)
        
        # Display as styled dataframe
        st.dataframe(
            df_pipeline,
            use_container_width=True,
            hide_index=True
        )
        
        # Interview Preparation Timeline
        st.markdown("### 📅 Recent Interview Preparations")
        
        # Mock interview data
        interview_data = {
            'Company': ['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple'],
            'Role': ['Software Engineer', 'Product Manager', 'Data Scientist', 'Frontend Dev', 'iOS Developer'],
            'Date': ['2024-01-15', '2024-01-12', '2024-01-10', '2024-01-08', '2024-01-05'],
            'Status': ['Completed', 'Completed', 'In Progress', 'Completed', 'Completed'],
            'Questions Generated': [23, 18, 15, 21, 19]
        }
        
        df_interviews = pd.DataFrame(interview_data)
        df_interviews['Date'] = pd.to_datetime(df_interviews['Date'])
        
        # Create timeline visualization
        fig_timeline = px.scatter(
            df_interviews,
            x='Date',
            y='Company',
            size='Questions Generated',
            color='Status',
            title="Interview Preparation Timeline",
            color_discrete_map={
                'Completed': '#10b981',
                'In Progress': '#f59e0b',
                'Pending': '#ef4444'
            }
        )
        
        fig_timeline.update_layout(
            height=400,
            showlegend=True,
            xaxis_title="Date",
            yaxis_title="Company"
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Performance Analytics
        st.markdown("### 📈 Performance Analytics")
        
        tab1, tab2, tab3 = st.tabs(["Success Rates", "Question Quality", "Research Depth"])
        
        with tab1:
            # Success rate over time
            dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
            success_rates = [random.randint(85, 98) for _ in dates]
            
            fig_success = px.line(
                x=dates,
                y=success_rates,
                title="Interview Prep Success Rate Over Time",
                labels={'x': 'Date', 'y': 'Success Rate (%)'}
            )
            fig_success.update_traces(line_color='#3b82f6')
            st.plotly_chart(fig_success, use_container_width=True)
        
        with tab2:
            # Question quality metrics
            quality_data = {
                'Question Type': ['Company-Specific', 'Role-Specific', 'Behavioral', 'Technical', 'General'],
                'Average Quality Score': [4.7, 4.5, 4.8, 4.3, 4.6],
                'Questions Generated': [45, 67, 89, 34, 78]
            }
            
            fig_quality = px.bar(
                quality_data,
                x='Question Type',
                y='Average Quality Score',
                title="Question Quality by Type",
                color='Average Quality Score',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_quality, use_container_width=True)
        
        with tab3:
            # Research depth metrics
            research_data = {
                'Research Type': ['Company Info', 'Interviewer Background', 'Role Analysis', 'Industry Trends'],
                'Data Points Collected': [156, 89, 134, 67],
                'Accuracy Score': [94, 87, 91, 89]
            }
            
            fig_research = px.scatter(
                research_data,
                x='Data Points Collected',
                y='Accuracy Score',
                size='Data Points Collected',
                color='Research Type',
                title="Research Quality vs. Depth"
            )
            st.plotly_chart(fig_research, use_container_width=True)
    
    with col_right:
        # Live Activity Feed
        st.markdown("### 🔴 Live Activity")
        
        # Real-time activity simulation
        if 'activity_feed' not in st.session_state:
            st.session_state.activity_feed = [
                {"time": "2 min ago", "type": "email", "message": "New interview email from Google", "status": "success"},
                {"time": "5 min ago", "type": "research", "message": "Completed company research for Microsoft", "status": "success"},
                {"time": "8 min ago", "type": "questions", "message": "Generated 23 questions for Amazon interview", "status": "success"},
                {"time": "12 min ago", "type": "prep", "message": "Sent prep summary to user", "status": "success"},
                {"time": "15 min ago", "type": "error", "message": "Tavily API rate limit reached", "status": "error"},
            ]
        
        # Activity feed container
        activity_container = st.container()
        
        with activity_container:
            for activity in st.session_state.activity_feed:
                status_color = {
                    "success": "#10b981",
                    "warning": "#f59e0b",
                    "error": "#ef4444"
                }.get(activity["status"], "#6b7280")
                
                type_icon = {
                    "email": "📧",
                    "research": "🔬",
                    "questions": "❓",
                    "prep": "📝",
                    "error": "⚠️"
                }.get(activity["type"], "📝")
                
                st.markdown(f"""
                <div style="
                    padding: 0.75rem;
                    margin-bottom: 0.5rem;
                    border-left: 3px solid {status_color};
                    background-color: #f8fafc;
                    border-radius: 0 5px 5px 0;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
                        <span style="margin-right: 0.5rem;">{type_icon}</span>
                        <strong style="color: #1f2937;">{activity['message']}</strong>
                    </div>
                    <small style="color: #6b7280;">{activity['time']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Refresh activity feed
        if st.button("🔄 Refresh Activity", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📋 Quick Stats")
        
        # System health indicators
        st.markdown("""
        **🏥 System Health**
        - API Status: 🟢 All systems operational
        - Cache Hit Rate: 87%
        - Avg Response Time: 2.3s
        - Memory Usage: 234MB / 1GB
        """)
        
        st.markdown("---")
        
        # Upcoming Interviews
        st.markdown("### 📅 Upcoming Interviews")
        
        upcoming = [
            {"company": "Tesla", "date": "Tomorrow", "time": "2:00 PM", "prep_status": "Ready"},
            {"company": "Netflix", "date": "Jan 20", "time": "10:30 AM", "prep_status": "In Progress"},
            {"company": "Uber", "date": "Jan 22", "time": "3:00 PM", "prep_status": "Pending"}
        ]
        
        for interview in upcoming:
            status_color = {
                "Ready": "#10b981",
                "In Progress": "#f59e0b",
                "Pending": "#ef4444"
            }.get(interview["prep_status"], "#6b7280")
            
            st.markdown(f"""
            <div style="
                padding: 0.5rem;
                margin-bottom: 0.5rem;
                border: 1px solid #e5e7eb;
                border-radius: 5px;
                background-color: white;
            ">
                <strong>{interview['company']}</strong><br>
                <small>📅 {interview['date']} • ⏰ {interview['time']}</small><br>
                <small style="color: {status_color};">● {interview['prep_status']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔍 Manual Research", use_container_width=True):
            st.info("Opening research interface...")
        
        if st.button("📝 Generate Questions", use_container_width=True):
            st.info("Opening question generator...")
        
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Opening detailed analytics...")
    
    # Footer with system info
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #6b7280; font-size: 0.8rem;">
        Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
        System uptime: 2d 14h 23m | 
        Version: 1.0.0-beta
    </div>
    """, unsafe_allow_html=True)