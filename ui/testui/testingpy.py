import streamlit as st
#streamlit run ui/test/testingpy.py
# Set page config
st.set_page_config(
    page_title="Job Application Workflow UI",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary: #64b5f6;
        --secondary: #81c784;
        --accent: #ba68c8;
        --light: #e0e0e0;
        --dark: #121212;
        --gray: #b0bec5;
        --border-radius: 8px;
        --shadow: 0 2px 10px rgba(0,0,0,0.5);
    }

    body {
        background-color: var(--dark);
        color: var(--light);
    }

    * {
        box-sizing: border-box;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .header {
        background: linear-gradient(135deg, var(--primary), #42a5f5);
        color: white;
        padding: 1rem 2rem;
        box-shadow: var(--shadow);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 0;
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
        border-bottom: 2px solid var(--primary);
        color: var(--primary);
    }

    .step-card {
        background: #1e1e1e;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border-left: 4px solid var(--primary);
        margin-bottom: 1rem;
        color: var(--light);
    }

    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.8rem;
    }

    .step-icon {
        font-size: 1.5rem;
        color: var(--primary);
    }

    .step-title {
        font-weight: 600;
        font-size: 1.1rem;
    }

    .step-description {
        color: var(--gray);
        margin-bottom: 1rem;
    }

    .upload-area {
        border: 2px dashed var(--gray);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        background: #1f1f1f;
        color: var(--gray);
        margin-bottom: 1.5rem;
    }

    .upload-icon {
        font-size: 3rem;
        color: var(--gray);
        margin-bottom: 1rem;
    }

    .btn {
        background: var(--primary);
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
        background: #2196f3;
    }

    .btn-secondary {
        background: var(--secondary);
    }

    .btn-secondary:hover {
        background: #66bb6a;
    }

    .btn-accent {
        background: var(--accent);
    }

    .btn-accent:hover {
        background: #ab47bc;
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
        background: var(--secondary);
        width: 65%;
    }

    .stat-card {
        background: #1c1c1c;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        text-align: center;
        color: var(--light);
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        margin: 0.5rem 0;
    }

    .stat-label {
        color: var(--gray);
    }

    .input-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: var(--light);
    }

    .input-group input, 
    .input-group textarea {
        width: 100%;
        padding: 0.8rem;
        border: 1px solid #444;
        background: #222;
        color: var(--light);
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
    }
</style>

""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <div class="logo">
        <div class="logo-icon">🎯</div>
        <div class="logo-text">JobFlow AI</div>
    </div>
    <div>
        <button class="btn">User Profile</button>
    </div>
</div>
""", unsafe_allow_html=True)

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
            st.experimental_rerun()
    
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