# ui/pages/5_history.py
import streamlit as st
from components.sidebar import show_sidebar
import pandas as pd

def show_history():
    st.title("History")
    st.subheader("Interview History and Analytics")
    
    # Timeline view
    st.markdown("## Recent Interviews")
    
    # Sample data
    history_data = [
        {"Date": "2024-01-15", "Company": "Google", "Role": "SWE", "Status": "Prepared"},
        {"Date": "2024-01-10", "Company": "Meta", "Role": "Data Scientist", "Status": "Completed"},
        {"Date": "2024-01-05", "Company": "Amazon", "Role": "ML Engineer", "Status": "Scheduled"},
        {"Date": "2023-12-20", "Company": "Microsoft", "Role": "Software Engineer", "Status": "Completed"}
    ]
    
    for item in history_data:
        status_color = "🟢" if item["Status"] == "Completed" else "🟡" if item["Status"] == "Prepared" else "🔵"
        st.markdown(f"{status_color} **{item['Date']}** - {item['Company']} ({item['Role']}) - {item['Status']}")
    
    # Performance Analytics
    st.markdown("## Preparation Analytics")
    
    # Sample analytics data
    analytics_data = {
        "Metric": ["Questions Answered", "Confidence Score", "Prep Time (min)", "Interviews"],
        "Value": [156, 89, 245, 24],
        "Trend": ["↗️ 12%", "↗️ 8%", "↘️ 5%", "↗️ 15%"]
    }
    
    df = pd.DataFrame(analytics_data)
    st.dataframe(df, use_container_width=True)
    
    # Charts
    st.markdown("## Progress Over Time")
    chart_data = pd.DataFrame({
        'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'Questions': [45, 67, 89, 123],
        'Confidence': [75, 82, 88, 91]
    })
    
    st.line_chart(chart_data.set_index('Week'))

show_sidebar()
show_history()