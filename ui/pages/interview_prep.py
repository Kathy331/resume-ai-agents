import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tempfile

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import workflow components
try:
    from workflows.interview_prep_workflow import InterviewPrepWorkflow
    from shared.google_oauth.dual_gmail_services import get_user_gmail_service, get_bot_gmail_service, check_gmail_authentication
    from shared.google_oauth.google_apis_start import create_service
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = str(e)

def send_email_with_bot_service(service, recipient_email, subject, html_body):
    """Send email using the bot Gmail service"""
    try:
        message = MIMEMultipart('alternative')
        message['to'] = recipient_email
        message['subject'] = subject
        
        # Create HTML part
        html_part = MIMEText(html_body, 'html')
        message.attach(html_part)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send email
        send_message = service.users().messages().send(
            userId='me', 
            body={'raw': raw_message}
        ).execute()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    /* Light theme override */
    .stApp {
        background-color: #DFEDEF !important;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #DFEDEF;
    }
    
    /* Custom input sections */
    .input-section {
        background-color: #DDF1F6;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border: 2px solid #125584;
    }
    
    /* Status cards */
    .status-card {
        background-color: #DDF1F6;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #125584;
        margin: 10px 0;
        font-family: 'Arial', sans-serif;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #125584 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #0d4163 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(18, 85, 132, 0.3) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #DDF1F6;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #125584;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FBA09F !important;
        color: #125584 !important;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background-color: white !important;
        border: 2px solid #125584 !important;
        border-radius: 8px !important;
        color: #125584 !important;
    }
    
    /* Success/info messages */
    .stSuccess {
        background-color: #d4edda !important;
        border-color: #c3e6cb !important;
        color: #155724 !important;
    }
    
    .stInfo {
        background-color: #DDF1F6 !important;
        border-color: #125584 !important;
        color: #125584 !important;
    }
    
    /* Prep guide content styling */
    .prep-guide-content {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #125584;
        margin: 10px 0;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
    }
    
    /* Scrollable content */
    .scrollable-content {
        max-height: 500px;
        overflow-y: auto;
        padding: 15px;
        background-color: white;
        border: 2px solid #125584;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'interview_folder' not in st.session_state:
        st.session_state.interview_folder = ""
    if 'folder_locked' not in st.session_state:
        st.session_state.folder_locked = False
    if 'prep_guides' not in st.session_state:
        st.session_state.prep_guides = {}
    if 'email_tabs' not in st.session_state:
        st.session_state.email_tabs = []
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""

def generate_prep_guide():
    """Generate prep guide using the workflow"""
    if not IMPORTS_AVAILABLE:
        st.error(f"Cannot import required modules: {IMPORT_ERROR}")
        return
        
    try:
        with st.spinner("🔄 Generating interview prep guides..."):
            # Initialize workflow
            workflow = InterviewPrepWorkflow()
            
            # Run workflow with folder parameter
            folder = st.session_state.interview_folder if st.session_state.interview_folder else None
            results = workflow.run_workflow(folder=folder)
            
            if results and results.get('success') and results.get('individual_results'):
                # Extract prep guides from individual results
                prep_guides = {}
                for result in results['individual_results']:
                    if result.get('prep_guide_generated') and result.get('company_keyword'):
                        company = result['company_keyword']
                        # Get prep guide content from pipeline results
                        prep_guide_pipeline_result = result.get('pipeline_results', {}).get('prep_guide_pipeline', {})
                        prep_guide_content = prep_guide_pipeline_result.get('prep_guide_content', '')
                        
                        if prep_guide_content:
                            prep_guides[company] = {
                                'content': prep_guide_content,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'company_keyword': company,
                                'email_subject': result.get('subject', ''),
                                'citations': prep_guide_pipeline_result.get('citations_used', 0)
                            }
                
                if prep_guides:
                    st.session_state.prep_guides = prep_guides
                    st.success(f"✅ Generated {len(prep_guides)} prep guides!")
                    st.rerun()
                else:
                    st.warning("⚠️ No prep guides were generated. The emails might not be interview invitations.")
            else:
                st.warning("⚠️ Workflow completed but no results were returned. Please check your email folder.")
                
    except Exception as e:
        st.error(f"❌ Error generating prep guides: {str(e)}")

def render_interview_prep():
    """Main function to render the interview prep page"""
    apply_custom_css()
    initialize_session_state()
    
    st.title("🎯 Interview Prep AI")
    st.markdown("Generate personalized interview preparation guides from your emails")
    
    # Folder Input Section
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📁 Email Folder Configuration")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        if not st.session_state.folder_locked:
            folder_input = st.text_input(
                "Email Folder Name",
                value=st.session_state.interview_folder,
                placeholder="Enter folder name (leave empty to use INTERVIEW_FOLDER from .env)",
                disabled=st.session_state.folder_locked,
                key="folder_input"
            )
            st.session_state.interview_folder = folder_input
        else:
            st.text_input(
                "Email Folder Name", 
                value=st.session_state.interview_folder, 
                disabled=True,
                key="folder_display"
            )
    
    with col2:
        if not st.session_state.folder_locked:
            if st.button("🔒 Lock Folder", key="lock_folder"):
                st.session_state.folder_locked = True
                st.rerun()
        else:
            if st.button("✏️ Edit Folder", key="edit_folder"):
                st.session_state.folder_locked = False
                st.rerun()
    
    with col3:
        if st.button("🚀 Generate Prep Guide", key="generate_prep"):
            if st.session_state.folder_locked or not st.session_state.interview_folder:
                generate_prep_guide()
            else:
                st.warning("Please lock the folder first or leave empty to use default settings")
    
    # Display current configuration
    current_folder = st.session_state.interview_folder if st.session_state.interview_folder else os.getenv('INTERVIEW_FOLDER', 'INBOX')
    st.markdown(f"""
    <div class="status-card">
        <strong>Current Configuration:</strong><br>
        📁 Folder: <code>{current_folder}</code><br>
        🔒 Status: {'Locked' if st.session_state.folder_locked else 'Unlocked'}
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # User Email Input Section
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📧 Your Email Configuration")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_email = st.text_input(
            "Your Email Address",
            value=st.session_state.user_email,
            placeholder="Enter your email address for receiving prep guides",
            key="user_email_input"
        )
        st.session_state.user_email = user_email
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("📤 Send All Prep Guides", key="send_all_guides"):
            if st.session_state.user_email and st.session_state.prep_guides:
                send_all_prep_guides(st.session_state.user_email)
            elif not st.session_state.user_email:
                st.warning("Please enter your email address first")
            else:
                st.warning("No prep guides available to send")
    
    # Display current email configuration
    if st.session_state.user_email:
        # Get authentication status from dual Gmail services
        auth_status = check_gmail_authentication()
        
        user_email = auth_status.get('user_email', 'Not authenticated')
        bot_email = auth_status.get('bot_email', 'Not authenticated')
        
        # Status check
        user_status = '✅ Connected' if auth_status['user_authenticated'] else '❌ Not connected'
        bot_status = '✅ Ready to send' if auth_status['bot_authenticated'] else '❌ Not authenticated'
            
        st.markdown(f"""
        <div class="status-card">
            <strong>Email Configuration:</strong><br>
            📧 Your Email: <code>{user_email}</code> {user_status}<br>
            🤖 Sender Account: <code>{bot_email}</code> {bot_status}<br>
            📡 Status: {bot_status}
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    

    
    # Display Prep Guides Interface
    display_prep_guides_interface()

def display_prep_guides_interface():
    """Display the main prep guides interface with editable tabs and editing"""
    st.markdown("---")
    st.markdown("### 📋 Interview Prep Guides")
    
    if not st.session_state.prep_guides:
        st.info("📭 No prep guides generated yet. Click 'Generate Prep Guide' first.")
        return
    
    # Initialize editable tab names in session state
    if 'tab_names' not in st.session_state:
        st.session_state.tab_names = {company: company for company in st.session_state.prep_guides.keys()}
    
    # Add any new companies to tab names
    for company in st.session_state.prep_guides.keys():
        if company not in st.session_state.tab_names:
            st.session_state.tab_names[company] = company
    
    # Tab name editing section
    st.markdown("#### ✏️ Edit Tab Names")
    companies = list(st.session_state.prep_guides.keys())
    
    for i, company in enumerate(companies):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_name = st.text_input(
                f"Tab name for {company}:",
                value=st.session_state.tab_names.get(company, company),
                key=f"tab_name_{company}"
            )
            st.session_state.tab_names[company] = new_name
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Reset", key=f"reset_tab_{company}"):
                st.session_state.tab_names[company] = company
                st.rerun()
    
    # Create tabs with editable names
    tab_display_names = [st.session_state.tab_names.get(company, company) for company in companies]
    tabs = st.tabs([f"🏢 {name}" for name in tab_display_names])
    
    for i, (company, tab) in enumerate(zip(companies, tabs)):
        with tab:
            display_single_prep_guide(company)

def display_single_prep_guide(company: str):
    """Display interface for a single prep guide with editing capabilities"""
    prep_guide = st.session_state.prep_guides[company]
    content_key = f"prep_content_{company}"
    edit_key = f"edit_mode_{company}"
    
    # Initialize content in session state if not exists
    if content_key not in st.session_state:
        st.session_state[content_key] = prep_guide.get('content', '')
    
    # Initialize edit mode if not exists
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False
    
    # Company header with stats
    st.markdown(f"""
    <div style="background-color: #DDF1F6; padding: 10px; border-radius: 8px; border: 1px solid #125584; margin: 10px 0;">
        <strong>🏢 Company:</strong> <code>{company}</code> |
        <strong>📊 Length:</strong> {len(st.session_state[content_key])} chars |
        <strong>📝 Words:</strong> {len(st.session_state[content_key].split())} |
        <strong>🔧 Mode:</strong> {'Edit' if st.session_state[edit_key] else 'View'}
    </div>
    """, unsafe_allow_html=True)
    
    # Control buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button(f"✏️ {'Exit Edit' if st.session_state[edit_key] else 'Edit'}", key=f"edit_{company}"):
            st.session_state[edit_key] = not st.session_state[edit_key]
            st.rerun()
    
    with col2:
        if st.button(f"💾 Save", key=f"save_{company}"):
            st.session_state.prep_guides[company]['content'] = st.session_state[content_key]
            st.success(f"✅ Saved changes for {company}")
    
    with col3:
        if st.button(f"🔄 Reset", key=f"reset_{company}"):
            st.session_state[content_key] = prep_guide.get('content', '')
            st.rerun()
    
    with col4:
        if st.button(f"📤 Send", key=f"send_{company}"):
            if st.session_state.user_email:
                send_single_prep_guide(company, st.session_state.user_email)
            else:
                st.warning("Please set your email address first")
    
    # Content display/editing
    if st.session_state[edit_key]:
        # Edit mode
        st.session_state[content_key] = st.text_area(
            f"Edit {company} Prep Guide:",
            value=st.session_state[content_key],
            height=400,
            key=f"textarea_{company}"
        )
    else:
        # View mode with scrollable content
        st.markdown(f"""
        <div style="
            max-height: 500px; 
            overflow-y: auto; 
            padding: 15px; 
            background-color: white; 
            border: 2px solid #125584; 
            border-radius: 8px; 
            margin: 10px 0;
            white-space: pre-wrap;
            font-family: 'Helvetica', sans-serif;
            line-height: 1.6;
        ">
{st.session_state[content_key]}
        </div>
        """, unsafe_allow_html=True)

def send_single_prep_guide(company: str, recipient_email: str):
    """Send a single prep guide via email using bot service"""
    try:
        # Check bot authentication status
        auth_status = check_gmail_authentication()
        if not auth_status['bot_authenticated']:
            st.error("❌ Bot email not authenticated. Contact admin to set up bot account.")
            return
        
        # Get bot service
        bot_service = get_bot_gmail_service()
        if not bot_service:
            st.error("❌ Failed to get bot Gmail service")
            return
        
        # Get bot email for display
        bot_email = auth_status.get('bot_email', 'Bot Account')
        st.info(f"📧 Sending from bot account: {bot_email}")
        
        prep_content = st.session_state.prep_guides[company]['content']
        subject = f"🎯 Interview Prep Guide for {company}"
        
        # Create HTML email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background-color: #DDF1F6; padding: 20px; border-radius: 10px; border: 2px solid #125584;">
                <h1 style="color: #125584;">🎯 Interview Prep Guide</h1>
                <h2 style="color: #125584;">Company: {company}</h2>
                <hr style="border: 1px solid #125584;">
                <div style="background-color: white; padding: 15px; border-radius: 8px; white-space: pre-wrap;">
{prep_content}
                </div>
                <hr style="border: 1px solid #125584;">
                <p style="text-align: center; color: #125584; font-style: italic;">
                    Generated by Interview Prep AI • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </p>
            </div>
        </body>
        </html>
        """
        
        # Send email using bot service
        result = send_email_with_bot_service(bot_service, recipient_email, subject, html_body)
        
        if result:
            st.success(f"✅ Prep guide for {company} sent to {recipient_email}")
        else:
            st.error("❌ Failed to send email")
            
    except Exception as e:
        st.error(f"❌ Error sending email: {str(e)}")

def send_all_prep_guides(recipient_email: str):
    """Send all prep guides in a single email using bot Gmail service"""
    try:
        # Check bot authentication status
        auth_status = check_gmail_authentication()
        if not auth_status['bot_authenticated']:
            st.error("❌ Bot email not authenticated. Contact admin to set up bot account.")
            return
        
        # Get bot service
        bot_service = get_bot_gmail_service()
        if not bot_service:
            st.error("❌ Failed to get bot Gmail service")
            return
        
        # Get bot email for display
        bot_email = auth_status.get('bot_email', 'Bot Account')
        st.info(f"📧 Sending from bot account: {bot_email}")
        
        companies = list(st.session_state.prep_guides.keys())
        subject = f"🎯 Interview Prep Guides - {len(companies)} Companies"
        
        # Create combined HTML content
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background-color: #DDF1F6; padding: 20px; border-radius: 10px; border: 2px solid #125584;">
                <h1 style="color: #125584;">🎯 Interview Prep Guides</h1>
                <p style="color: #125584;"><strong>Companies:</strong> {', '.join(companies)}</p>
                <p style="color: #125584;"><strong>Sent from:</strong> {bot_email}</p>
                <hr style="border: 1px solid #125584;">
        """
        
        for company in companies:
            prep_content = st.session_state.prep_guides[company]['content']
            html_body += f"""
                <div style="background-color: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h2 style="color: #125584; border-bottom: 2px solid #125584; padding-bottom: 10px;">
                        🏢 {company}
                    </h2>
                    <div style="white-space: pre-wrap;">
{prep_content}
                    </div>
                </div>
            """
        
        html_body += f"""
                <hr style="border: 1px solid #125584;">
                <p style="text-align: center; color: #125584; font-style: italic;">
                    Generated by Interview Prep AI • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
                    Sent via Bot Gmail Service
                </p>
            </div>
        </body>
        </html>
        """
        
        # Send email using bot service
        result = send_email_with_bot_service(bot_service, recipient_email, subject, html_body)
        
        if result:
            st.success(f"✅ All prep guides for {len(companies)} companies sent to {recipient_email}")
            st.success(f"📧 Email sent from: {bot_email}")
        else:
            st.error("❌ Failed to send email")
            
    except Exception as e:
        st.error(f"❌ Error sending all prep guides: {str(e)}")
        
        # Suggest solution
        with st.expander("🔧 Troubleshooting"):
            st.write("**Possible solutions:**")
            st.write("1. Check that Gmail API is enabled in Google Cloud Console")
            st.write("2. Verify that the credentials file exists and is valid")
            st.write("3. Try re-authenticating by deleting token files and running again")
            st.write("4. Ensure you have the correct scopes enabled")
            st.code("rm token_files/token_gmail_v1.json", language="bash")

if __name__ == "__main__":
    render_interview_prep()
