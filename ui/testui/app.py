import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Add ui directory to path for relative imports
ui_root = Path(__file__).parent.parent
sys.path.append(str(ui_root))

# Import the interview prep page and authentication
from pages.interview_prep import render_interview_prep
from shared.google_oauth.dual_gmail_services import check_gmail_authentication

# Set page config
st.set_page_config(
    page_title="Resume AI Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with better design and animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #DDF1F6;
        --secondary: #DFEDEF;
        --accent: #FBA09F;
        --text: #125584;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --border-radius: 12px;
        --shadow: 0 4px 20px rgba(18, 85, 132, 0.08);
        --shadow-hover: 0 8px 25px rgba(18, 85, 132, 0.15);
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #DFEDEF 0%, #DDF1F6 100%);
        color: var(--text);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1544g2n {
        background: linear-gradient(180deg, #DDF1F6 0%, #DFEDEF 100%);
        border-right: 1px solid rgba(18, 85, 132, 0.1);
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Override Streamlit's default colors */
    .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: var(--text);
    }
    
    /* Enhanced header */
    .app-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .app-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23125584' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
        pointer-events: none;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text);
        margin: 0;
        position: relative;
        z-index: 1;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        color: var(--text);
        opacity: 0.8;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced cards */
    .feature-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid rgba(18, 85, 132, 0.1);
        transition: var(--transition);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent), var(--primary));
    }
    
    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.8rem;
    }
    
    .card-description {
        color: var(--text);
        opacity: 0.8;
        line-height: 1.6;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .status-success {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.1);
        color: var(--warning);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.1);
        color: var(--error);
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--text) 0%, var(--accent) 100%);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-hover);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: white;
        border: 2px solid rgba(18, 85, 132, 0.1);
        border-radius: var(--border-radius);
        color: var(--text);
        transition: var(--transition);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(251, 160, 159, 0.1);
    }
    
    /* File uploader */
    .upload-zone {
        border: 2px dashed rgba(18, 85, 132, 0.3);
        border-radius: var(--border-radius);
        padding: 3rem 2rem;
        text-align: center;
        background: linear-gradient(135deg, white 0%, var(--primary) 100%);
        transition: var(--transition);
        margin: 1rem 0;
    }
    
    .upload-zone:hover {
        border-color: var(--accent);
        background: linear-gradient(135deg, var(--primary) 0%, white 100%);
    }
    
    .upload-icon {
        font-size: 3rem;
        color: var(--text);
        margin-bottom: 1rem;
        opacity: 0.7;
    }
    
    /* Progress indicators */
    .progress-container {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 8px;
        background: rgba(18, 85, 132, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--accent), var(--primary));
        transition: width 0.3s ease;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow);
        border: 1px solid rgba(18, 85, 132, 0.1);
        transition: var(--transition);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: var(--text);
        opacity: 0.7;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar navigation */
    .nav-item {
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: var(--border-radius);
        transition: var(--transition);
        cursor: pointer;
        border: 1px solid transparent;
    }
    
    .nav-item:hover {
        background: rgba(18, 85, 132, 0.05);
        border-color: rgba(18, 85, 132, 0.1);
    }
    
    .nav-item.active {
        background: var(--accent);
        color: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def show_authentication_status():
    """Enhanced authentication status display"""
    auth_status = check_gmail_authentication()
    
    st.markdown("### 🔐 Authentication Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if auth_status['user_authenticated']:
            st.markdown(f"""
            <div class="status-badge status-success">
                📧 User Email: ✅ {auth_status['user_email'] or 'Connected'}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge status-warning">
                📧 User Email: ⚠️ Not Connected
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if auth_status['bot_authenticated']:
            st.markdown(f"""
            <div class="status-badge status-success">
                🤖 Bot Email: ✅ {auth_status['bot_email'] or 'Connected'}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge status-error">
                🤖 Bot Email: ❌ Not Connected
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Status", type="primary"):
        st.rerun()

def show_workflow_steps():
    """Display workflow progress in sidebar"""
    st.markdown("### 📋 Workflow Progress")
    
    steps = [
        {"icon": "📄", "title": "Resume Upload", "progress": 100},
        {"icon": "🔍", "title": "Resume Analysis", "progress": 100},
        {"icon": "📋", "title": "Job Description", "progress": 85},
        {"icon": "🎯", "title": "Job Matching", "progress": 75},
        {"icon": "📧", "title": "Email Drafting", "progress": 60},
        {"icon": "🚀", "title": "Send & Track", "progress": 0}
    ]
    
    for i, step in enumerate(steps):
        status = "✅" if step["progress"] == 100 else "🔄" if step["progress"] > 0 else "⏳"
        
        st.markdown(f"""
        <div style="margin: 0.5rem 0; padding: 0.75rem; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">{step['icon']}</span>
                <strong style="color: #125584;">{step['title']}</strong>
                <span style="margin-left: auto; font-size: 0.9rem;">{status}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {step['progress']}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_workflow_page():
    """Main workflow page content"""
    
    # Header
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">📄 Job Application Workflow</h1>
        <p class="app-subtitle">Streamline your job search with AI-powered automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">12</div>
            <div class="metric-label">Applications Sent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">3</div>
            <div class="metric-label">Responses Received</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">78%</div>
            <div class="metric-label">Match Average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">1</div>
            <div class="metric-label">Upcoming Interviews</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content sections
    col_main1, col_main2 = st.columns([2, 1])
    
    with col_main1:
        # Email draft section
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">📧</div>
            <h3 class="card-title">Email Draft Review</h3>
            <p class="card-description">Review and customize your personalized outreach email</p>
        </div>
        """, unsafe_allow_html=True)
        
        subject = st.text_input("📝 Subject Line", "Exploring Software Engineering Opportunities at Tech Innovations Inc.")
        
        email_content = st.text_area("✉️ Email Content", 
"""Dear Sarah Johnson,

I hope this email finds you well. I came across your profile while researching Tech Innovations Inc. and was impressed by your work on sustainable cloud solutions. As a software engineer with 5 years of experience in cloud technologies and environmental sustainability, I believe my skills align perfectly with your team's mission.

In my previous role at GreenTech Solutions, I successfully:
• Reduced server energy consumption by 30% through infrastructure optimization
• Led a team of 4 developers in implementing carbon-tracking systems
• Architected scalable solutions handling 10M+ daily transactions

I'm particularly excited about Tech Innovations' commitment to carbon-neutral operations and would love to contribute to your sustainability initiatives. Your recent blog post about renewable energy integration in cloud infrastructure really resonated with my passion for green technology.

Would you be available for a brief conversation next week to discuss how my experience can support your team's goals?

Best regards,
Alex Morgan
Senior Software Engineer
alex.morgan@email.com | (555) 123-4567""", height=400)
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("💾 Save Draft", type="secondary"):
                st.success("✅ Draft saved successfully!")
        
        with col_btn2:
            if st.button("🚀 Send Email", type="primary"):
                st.success("🎉 Email sent successfully! Tracking initiated.")
                st.balloons()
        
        with col_btn3:
            if st.button("🔄 Generate New Version"):
                st.info("🤖 Generating alternative version...")
    
    with col_main2:
        # Quick stats and recent activity
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">📊</div>
            <h3 class="card-title">Recent Activity</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
            <strong>🎯 Tech Corp</strong><br>
            <small style="color: #666;">Applied 2 hours ago</small>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
            <strong>💬 StartupXYZ</strong><br>
            <small style="color: #666;">Response received</small>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
            <strong>📅 InnovateLab</strong><br>
            <small style="color: #666;">Interview scheduled</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Job description upload section
    st.markdown("""
    <div class="feature-card">
        <div class="card-icon">📋</div>
        <h3 class="card-title">Add New Job Opportunity</h3>
        <p class="card-description">Upload job descriptions or paste URLs to analyze and prepare applications</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📁 Upload File", "🔗 Job URL"])
    
    with tab1:
        st.markdown("""
        <div class="upload-zone">
            <div class="upload-icon">📄</div>
            <h4>Upload Job Description</h4>
            <p>Drag & drop or click to upload</p>
            <small>Supported: PDF, DOCX, TXT</small>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
    
    with tab2:
        job_url = st.text_input("🔗 Job Posting URL", placeholder="https://company.com/careers/job-123")
        
        if st.button("🔍 Analyze Job Posting"):
            if job_url:
                st.success("✅ Job posting analyzed successfully!")
                st.info("🤖 AI is now matching your profile with job requirements...")
            else:
                st.warning("⚠️ Please enter a valid job URL")

def render_interview_prep_page():
    """Interview prep page wrapper"""
    
    # Header
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">📚 Interview Prep AI</h1>
        <p class="app-subtitle">AI-powered interview preparation and practice</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check authentication
    auth_status = check_gmail_authentication()
    if not auth_status['user_authenticated']:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">🔗</div>
            <h3 class="card-title">Connect Your Email</h3>
            <p class="card-description">To access interview preparation features, please connect your Gmail account:</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **📋 Setup Instructions:**
        
        1. Open terminal in VS Code
        2. Run: `python setup_bot_email.py`
        3. Choose option 1 (User Authentication)
        4. Follow browser authentication process
        5. Click "Refresh Status" in the sidebar
        
        **🔒 Privacy & Security:**
        - Your email is used only for reading interview invitations
        - All data remains secure and private
        - The bot sends emails separately from a dedicated account
        """)
    else:
        # Render the actual interview prep page
        render_interview_prep()

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    # Navigation menu
    page = st.radio(
        "Choose a page:",
        ["🎯 Job Application Workflow", "📚 Interview Prep AI"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Authentication status in sidebar
    show_authentication_status()
    
    st.divider()
    
    # Workflow steps (only show on workflow page)
    if "Workflow" in page:
        show_workflow_steps()
    
    st.divider()
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("📊 View Analytics", use_container_width=True):
        st.info("📈 Analytics dashboard coming soon!")
    
    if st.button("⚙️ Settings", use_container_width=True):
        st.info("🛠️ Settings panel coming soon!")
    
    if st.button("❓ Help & Support", use_container_width=True):
        st.info("📚 Help documentation coming soon!")

# Main content based on navigation
if "Interview Prep" in page:
    render_interview_prep_page()
else:
    render_workflow_page()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; opacity: 0.7;">
    <small>© 2024 Resume AI Assistant | Built with ❤️ and Streamlit</small>
</div>
""", unsafe_allow_html=True)