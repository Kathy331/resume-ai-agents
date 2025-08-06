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

#streamlit run ui/testui/app.py
# Set page config
st.set_page_config(
    page_title="Resume AI Assistant",
    page_icon="🐙",
    layout="wide"
)

# Custom CSS with your specified color scheme and authentication UI
st.markdown("""
<style>
    :root {
        --primary: #DDF1F6;
        --secondary: #DFEDEF;
        --accent: #FBA09F;
        --text: #125584;
        --light: #e0e0e0;
        --dark: #121212;
        --gray: #b0bec5;
        --border-radius: 8px;
        --shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* Override Streamlit's default theme */
    .stApp {
        background-color: #DFEDEF !important;
        color: #125584 !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #DFEDEF !important;
        color: #125584 !important;
        padding-top: 1rem !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #DDF1F6 !important;
    }
    
    /* Sidebar content */
    section[data-testid="stSidebar"] div {
        color: #125584 !important;
    }
    
    /* Override Streamlit's text colors */
    .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: #125584 !important;
    }
    
    /* Override input field backgrounds */
    .stTextInput > div > div > input {
        background-color: #DDF1F6 !important;
        color: #125584 !important;
        border: 2px solid #125584 !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #DDF1F6 !important;
        color: #125584 !important;
        border: 2px solid #125584 !important;
    }
    
    .stSelectbox > div > div > div {
        background-color: #DDF1F6 !important;
        color: #125584 !important;
    }

    body {
        background-color: var(--secondary) !important;
        color: var(--text) !important;
    }

    * {
        box-sizing: border-box;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .header {
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: var(--text);
        padding: 1rem 2rem;
        box-shadow: var(--shadow);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 0;
        margin-bottom: 1.5rem;
    }

    .logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .logo-icon {
        font-size: 2rem;
    }

    .logo-text {
        font-size: 1.5rem;
        font-weight: 600;
    }

    .section-title {
        font-size: 1.2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--text);
        color: var(--text);
    }

    .step-card {
        background: var(--primary);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border-left: 4px solid var(--text);
        margin-bottom: 1rem;
        color: var(--text);
    }

    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.8rem;
    }

    .step-icon {
        font-size: 1.5rem;
        color: var(--text);
    }

    .step-title {
        font-weight: 600;
        font-size: 1.1rem;
    }

    .step-description {
        color: var(--text);
        margin-bottom: 1rem;
        opacity: 0.8;
    }

    .upload-area {
        border: 2px dashed var(--text);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        background: var(--primary);
        color: var(--text);
        margin-bottom: 1.5rem;
    }

    .upload-icon {
        font-size: 3rem;
        color: var(--text);
        margin-bottom: 1rem;
    }

    .btn {
        background: var(--text);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: var(--border-radius);
        font-weight: 600;
        transition: background 0.3s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
    }

    .btn:hover {
        background: var(--accent);
        color: var(--text);
    }

    .btn-secondary {
        background: var(--accent);
        color: var(--text);
    }

    .btn-secondary:hover {
        background: var(--text);
        color: white;
    }

    .btn-accent {
        background: var(--accent);
        color: var(--text);
    }

    .btn-accent:hover {
        background: var(--text);
        color: white;
    }

    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .status-active {
        background-color: #4caf50;
    }

    .status-pending {
        background-color: #ffc107;
    }

    .status-inactive {
        background-color: #9e9e9e;
    }

    .progress-bar {
        height: 8px;
        background: #424242;
        border-radius: 4px;
        margin: 1.5rem 0;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: var(--accent);
        width: 65%;
    }

    .stat-card {
        background: var(--primary);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        text-align: center;
        color: var(--text);
        border: 1px solid var(--text);
        transition: transform 0.2s;
    }

    .stat-card:hover {
        transform: translateY(-5px);
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text);
        margin: 0.5rem 0;
    }

    .stat-label {
        color: var(--text);
        opacity: 0.8;
    }

    .input-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: var(--text);
    }

    .input-group input, 
    .input-group textarea {
        width: 100%;
        padding: 0.8rem;
        border: 1px solid var(--text);
        background: var(--primary);
        color: var(--text);
        border-radius: var(--border-radius);
        font-size: 1rem;
    }

    .input-group textarea {
        min-height: 120px;
        resize: vertical;
    }

    .actions {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }

    .stButton>button {
        width: auto;
        background-color: var(--text) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stButton>button:hover {
        background-color: var(--accent) !important;
        color: var(--text) !important;
    }
    
    /* Ensure all button text is white and readable */
    .stButton>button span {
        color: white !important;
    }
    
    .stButton>button:hover span {
        color: white !important;
    }
    
    /* Navigation buttons specific styling */
    .stButton>button[kind="primary"] {
        background-color: #125584 !important;
        color: white !important;
        border: 2px solid #125584 !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        background-color: #FBA09F !important;
        color: white !important;
        border: 2px solid #FBA09F !important;
    }
    
    /* Force white text on all buttons */
    button[data-testid="baseButton-primary"] {
        background-color: #125584 !important;
        color: white !important;
    }
    
    button[data-testid="baseButton-primary"]:hover {
        background-color: #FBA09F !important;
        color: white !important;
    }
    
    /* Override any text color inheritance in buttons */
    .stButton p, .stButton div, .stButton span {
        color: white !important;
    }
    
    /* File upload button */
    .stFileUploader button {
        background-color: #125584 !important;
        color: white !important;
        border: 2px solid #125584 !important;
    }
    
    .stFileUploader button:hover {
        background-color: #FBA09F !important;
        color: white !important;
    }
    
    /* Checkbox and radio button labels */
    .stCheckbox label, .stRadio label {
        color: #125584 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #DDF1F6 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #DDF1F6 !important;
        color: #125584 !important;
        border: 1px solid #125584 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #125584 !important;
        color: white !important;
    }

    /* Fix metric cards */
    .css-1xarl3l {
        background-color: #DDF1F6 !important;
        color: #125584 !important;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background-color: #DDF1F6 !important;
        color: #125584 !important;
        border: 2px dashed #125584 !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #DDF1F6 !important;
        color: #125584 !important;
    }
    
    .stError {
        background-color: #FBA09F !important;
        color: #125584 !important;
    }
    
    .stWarning {
        background-color: #FBA09F !important;
        color: #125584 !important;
    }
    
    .stInfo {
        background-color: #DDF1F6 !important;
        color: #125584 !important;
    }
    
    /* Override any remaining dark backgrounds */
    [data-testid="stAppViewContainer"] {
        background-color: #DFEDEF !important;
    }
    
    [data-testid="stHeader"] {
        background-color: #DFEDEF !important;
    }
    
    [data-testid="stToolbar"] {
        background-color: #DFEDEF !important;
    }
    
    /* Spinner and loading elements */
    .stSpinner > div {
        border-color: #125584 !important;
    }

    .nav-button {
        background: var(--text);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: var(--border-radius);
        margin: 0.2rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }

    .nav-button:hover {
        background: var(--accent);
        color: var(--text);
    }

    .nav-button.active {
        background: var(--accent);
        color: var(--text);
    }
    
    /* Authentication status styling */
    .auth-status {
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius);
        margin: 0.5rem 0;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .auth-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .auth-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    
    .auth-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    
    .auth-bar {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        padding: 1rem;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #125584 !important;
    }
    
    /* Radio buttons in sidebar */
    [data-testid="stSidebar"] .stRadio label {
        color: #125584 !important;
    }
    
    /* Selected radio button */
    [data-testid="stSidebar"] .stRadio div[aria-selected="true"] {
        background-color: #125584 !important;
    }
</style>

""", unsafe_allow_html=True)

def show_authentication_status():
    """Show authentication status at the top of the page"""
    auth_status = check_gmail_authentication()
    
    st.markdown('<div class="auth-bar">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if auth_status['user_authenticated']:
            st.markdown(f"""
            <div class="auth-status auth-success">
                📧 <strong>User Email:</strong> ✅ {auth_status['user_email'] or 'Connected'}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="auth-status auth-warning">
                📧 <strong>User Email:</strong> ⚠️ Not Connected
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if auth_status['bot_authenticated']:
            st.markdown(f"""
            <div class="auth-status auth-success">
                🤖 <strong>Bot Email:</strong> ✅ {auth_status['bot_email'] or 'Connected'}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="auth-status auth-error">
                🤖 <strong>Bot Email:</strong> ❌ Not Connected
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🔄 Refresh", key="refresh_auth"):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_user_authentication_instructions():
    """Show user authentication instructions in expander"""
    with st.expander("🔗 Connect Your Email", expanded=True):
        st.markdown("""
        **📋 To Connect Your Gmail Account:**
        
        1. Open terminal in VS Code
        2. Run: `python setup_bot_email.py`
        3. Choose option 1 (User Authentication)
        4. Follow browser authentication
        5. Click "Refresh" button above
        
        **🔒 This allows the AI to:**
        - Read your Gmail for interview invitations
        - Analyze email content for prep guides
        - Keep your data secure and private
        
        **ℹ️ Your email is used only for reading. The bot sends emails separately.**
        """)

# Header
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("ui/images/inky2.png", width=60)

with col_title:
    st.markdown("""
    <div class="logo-text" style="font-size:1.8rem;font-weight:600;margin-top:0.4rem;color:#125584;">
        Resume AI Assistant
    </div>
    """, unsafe_allow_html=True)

# Authentication status bar
show_authentication_status()

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'workflow'

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Choose a page:",
        ["🎯 Job Application Workflow", "📚 Interview Prep AI"],
        key="navigation"
    )
    
    if page == "📚 Interview Prep AI":
        st.session_state.current_page = 'interview_prep'
    else:
        st.session_state.current_page = 'workflow'

# Page routing
if st.session_state.current_page == 'interview_prep':
    # Show authentication instructions if user not connected
    auth_status = check_gmail_authentication()
    if not auth_status['user_authenticated']:
        show_user_authentication_instructions()
    
    # Display Interview Prep page
    render_interview_prep()
else:
    # Display workflow content
    # Main layout
    col1, col2 = st.columns([1, 3])

    # Sidebar content
    with col1:
        # Workflow steps
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">Workflow Navigation</h2>', unsafe_allow_html=True)
        
        steps = [
            {"icon": "⭐", "title": "Resume Upload", "desc": "Upload your resume for processing", "status": "active"},
            {"icon": "🔍", "title": "Resume Analysis", "desc": "Extracting skills and experience", "status": "active"},
            {"icon": "📋", "title": "Job Description", "desc": "Input target job information", "status": "active"},
            {"icon": "🎯", "title": "Job Matching", "desc": "Comparing your profile with job", "status": "active"},
            {"icon": "📧", "title": "Email Drafting", "desc": "Creating personalized outreach", "status": "pending"}
        ]
        
        for step in steps:
            status_class = f"status-{step['status']}"
            st.markdown(f"""
            <div class="step-card">
                <div class="step-header">
                    <div class="step-icon">{step['icon']}</div>
                    <div class="step-title">{step['title']}</div>
                </div>
                <p>{step['desc']}</p>
                <span class="status-indicator {status_class}"></span> 
                {step['status'].title()}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
        
        # System status
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">System Status</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">87%</div>
            <div class="stat-label">Workflow Progress</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        """, unsafe_allow_html=True)
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">4</div>
                <div class="stat-label">Emails Drafted</div>
            </div>
            """, unsafe_allow_html=True)
        with col_stat2:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">2</div>
                <div class="stat-label">Interviews Scheduled</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)    
        
    # Main content
    with col2:
        # Dashboard stats
        st.markdown('<div class="dashboard-stats">', unsafe_allow_html=True)
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">12</div>
                <div class="stat-label">Applications Sent</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div class="stat-label">Responses Received</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat3:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">78%</div>
                <div class="stat-label">Match Average</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat4:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">1</div>
                <div class="stat-label">Upcoming Interviews</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Email draft review
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">Job Application Workflow</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-icon">📧</div>
                <div class="step-title">Email Draft Review</div>
            </div>
            <p class="step-description">Review and edit the generated email before sending</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Email form
        subject = st.text_input("Subject Line", "Exploring Opportunities at Tech Innovations Inc.")
        
        email_content = st.text_area("Email Content", 
"""Dear Sarah Johnson,

I came across your profile while researching Tech Innovations Inc. and was impressed by your work on sustainable cloud solutions. As a software engineer with 5 years of experience in cloud technologies and environmental sustainability, I believe my skills align well with your team's focus on green technology.

In my previous role at GreenTech Solutions, I reduced server energy consumption by 30% through infrastructure optimization. I'm particularly excited about Tech Innovations' commitment to carbon-neutral operations and would love to contribute to your sustainability initiatives.

I would appreciate the opportunity to discuss how my experience can support your team's goals. Are you available for a brief conversation next week?

Best regards,
Alex Morgan
Software Engineer""", height=300)
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("Save Draft", key="save"):
                st.success("Draft saved successfully!")
        
        with col_btn2:
            if st.button("Send Email", key="send"):
                st.success("Email sent successfully! The workflow will proceed to scheduling follow-ups.")
        
        with col_btn3:
            if st.button("Generate New Version", key="regenerate"):
                new_email = """Dear Sarah,

I hope this email finds you well. I'm reaching out regarding potential opportunities at Tech Innovations Inc. After reviewing your company's impressive work in sustainable technology, I believe my experience in cloud infrastructure and environmental solutions could be valuable to your team.

In my current role as Senior Software Engineer at GreenTech, I've led projects that reduced our carbon footprint by 35% through server optimization and renewable energy adoption. I'm particularly drawn to Tech Innovations' Green Cloud Initiative and would be excited to contribute to similar projects.

Would you be available for a brief discussion next week?

Best regards,
Alex Morgan"""
                st.session_state.email_content = new_email
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Job description upload
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">Upload New Job Description</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">📋</div>
            <h3>Upload Job Description</h3>
            <p>Drag & drop or click to upload a job posting</p>
            <p>Supported formats: PDF, DOCX, TXT</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
        if uploaded_file:
            st.success(f"File {uploaded_file.name} uploaded successfully!")
        
        job_url = st.text_input("Or Enter Job Posting URL", placeholder="https://...")
        
        if st.button("Process Job Description"):
            if uploaded_file or job_url:
                st.success("Job description processed successfully!")
            else:
                st.warning("Please upload a file or enter a job URL")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Add import for HTML formatter at the top
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import HTML formatter
try:
    from shared.html_formatter import generate_juteq_clean_content, generate_dandilyonn_clean_content
    print("✅ HTML formatter imported successfully")
except ImportError as e:
    print(f"❌ Failed to import HTML formatter: {e}")
    # Fallback - define inline
    def generate_juteq_clean_content():
        return """## 1. before interview

- email mentions date options: Tuesday, August 6 or Wednesday, August 7
- time: flexible between 10:00 a.m. and 4:00 p.m. (ET)
- duration: 30 minutes
- respond by end of day Friday, August 2 to confirm your time slot
- format: virtual, zoom - test your zoom setup and ensure stable internet connection
- prepare to discuss your background and interests in AI and cloud technologies

## 2. interviewer background

- rakesh gohel is a professional at juteq with expertise in AI and cloud technologies
- background: scaling with AI agents, cloud-native solutions focus
- mentioned interest in AI and cloud technologies in interview invitation
- [rakesh gohel linkedin](https://ca.linkedin.com/in/rakeshgohel01)

## 3. company background

- juteq is a technology company specializing in AI and cloud-native solutions
- active in AI trends and innovation as evidenced by recent LinkedIn posts
- focuses on cloud-native innovation and DevOps solutions
- hiring for internship positions in AI and cloud technologies
- [juteq linkedin](https://ca.linkedin.com/company/juteq)

## 4. technical preparations

- role: juteq internship program
- prep areas:
  - review fundamental concepts in AI and cloud technologies (as mentioned in email)
  - familiarize yourself with cloud-native solutions and DevOps practices
  - prepare examples of any AI or cloud projects you've worked on
  - be ready to discuss your interests in AI and cloud technologies

## 5. questions to ask

- to interviewer:
  - what drew you to focus on AI and cloud technologies at juteq?
  - how do you see juteq's approach to scaling with AI agents evolving?

- to company:
  - what are the most exciting projects juteq is working on currently?
  - what does success look like for an intern in this program?
  - how does juteq support intern learning and development?

## 6. common questions

- "tell me about a time when you worked with AI or cloud technologies."
- "how would you approach learning about a new AI technology or cloud platform?"
- "describe your interest in AI and cloud technologies mentioned in your application."
- "describe a time when you had to learn something quickly."
- "how do you handle feedback and constructive criticism?\""""
    
    def generate_dandilyonn_clean_content():
        return """## 1. before interview

- email mentions interview scheduling details and time slots
- format: virtual meeting setup recommended
- prepare to discuss your background and interests in education and technology
- review the SEEDS internship program mission and values

## 2. interviewer background

- archana chaudhary is the founder of dandilyonn seeds with 25+ years of engineering leadership
- background: adobe experience, stanford education, engineering leadership
- focus on women in tech, mobile app development, non-profit work
- [archana chaudhary linkedin](https://www.linkedin.com/in/jainarchana/)

## 3. company background

- dandilyonn seeds is a non-profit organization focused on education and environmental awareness
- founded in 2018 with focus on educating female computer science students
- SEEDS internship program for skill development and mentorship
- mission: empowering women in technology through education and hands-on experience
- [dandilyonn linkedin](https://www.linkedin.com/company/dandilyonn)

## 4. technical preparations

- role: dandilyonn seeds internship program
- prep areas:
  - review concepts in computer science education and non-profit work
  - research environmental awareness and sustainability initiatives
  - prepare examples of leadership, volunteering, or educational experience
  - familiarize yourself with the SEEDS internship program mission

## 5. questions to ask

- to interviewer:
  - what inspired you to start dandilyonn seeds and focus on education?
  - how do you balance engineering leadership with non-profit mission?

- to company:
  - what exciting initiatives is dandilyonn seeds pursuing?
  - what does success look like for an intern in this program?
  - how does dandilyonn seeds support intern learning and development?

## 6. common questions

- "tell me about a time when you demonstrated leadership or initiative."
- "how do you see technology being used to address social or environmental issues?"
- "what draws you to educational or non-profit work?"
- "describe your experience with mentoring or helping others learn."
- "describe a time when you had to learn something quickly."
- "how do you handle feedback and constructive criticism?\""""

def display_prep_guides():
    """Display editable interview prep guides"""
    st.header("📋 Interview Prep Guides")
    
    # Company selection
    company_options = ["Select Company", "JUTEQ", "Dandilyonn SEEDS"]
    selected_company = st.selectbox("Choose a company:", company_options)
    
    if selected_company == "JUTEQ":
        st.markdown("### 🚀 JUTEQ Interview Prep Guide")
        st.markdown("*AI & Cloud Technologies Internship*")
        
        # Get clean content
        content = generate_juteq_clean_content()
        
        # Create editable text area
        edited_content = st.text_area(
            "Edit your prep guide:",
            value=content,
            height=600,
            key="juteq_editor"
        )
        
        # Save button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("� Save Changes", key="save_juteq"):
                # Save to user storage
                save_user_guide("JUTEQ", edited_content)
                st.success("✅ Guide saved successfully!")
        
        with col2:
            # Download button
            st.download_button(
                label="📥 Download",
                data=edited_content,
                file_name="JUTEQ_prep_guide.md",
                mime="text/markdown"
            )
        
    elif selected_company == "Dandilyonn SEEDS":
        st.markdown("### 🌱 Dandilyonn SEEDS Interview Prep Guide")
        st.markdown("*Education & Environmental Awareness Internship*")
        
        # Get clean content
        content = generate_dandilyonn_clean_content()
        
        # Create editable text area
        edited_content = st.text_area(
            "Edit your prep guide:",
            value=content,
            height=600,
            key="dandilyonn_editor"
        )
        
        # Save button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("� Save Changes", key="save_dandilyonn"):
                # Save to user storage
                save_user_guide("Dandilyonn", edited_content)
                st.success("✅ Guide saved successfully!")
        
        with col2:
            # Download button
            st.download_button(
                label="📥 Download",
                data=edited_content,
                file_name="Dandilyonn_prep_guide.md",
                mime="text/markdown"
            )
    
    elif selected_company == "Select Company":
        st.info("👆 Please select a company to view and edit the interview prep guide")
        
        # Show preview of both companies
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚀 JUTEQ Preview")
            st.markdown("- AI & Cloud Technologies")
            st.markdown("- Interviewer: Rakesh Gohel")
            st.markdown("- 30-minute virtual interview")
            
        with col2:
            st.markdown("#### 🌱 Dandilyonn SEEDS Preview")
            st.markdown("- Education & Environmental Focus")
            st.markdown("- Interviewer: Archana Chaudhary")
            st.markdown("- Non-profit internship program")

def save_user_guide(company: str, content: str):
    """Save user-edited guide to storage"""
    import os
    from pathlib import Path
    
    # Create user storage directory
    storage_dir = Path("user_storage")
    storage_dir.mkdir(exist_ok=True)
    
    # Save file
    filename = f"{company}_edited_guide.md"
    file_path = storage_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Saved user guide: {file_path}")

def load_user_guide(company: str) -> str:
    """Load user-edited guide from storage"""
    from pathlib import Path
    
    storage_dir = Path("user_storage")
    filename = f"{company}_edited_guide.md"
    file_path = storage_dir / filename
    
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Return default content if no saved version
    if company == "JUTEQ":
        return generate_juteq_clean_content()
    else:
        return generate_dandilyonn_clean_content()

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Interview Prep Assistant",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 Interview Prep Assistant")
    st.markdown("*Edit and customize your interview preparation guides*")
    
    # Display the editable prep guides
    display_prep_guides()

if __name__ == "__main__":
    main()