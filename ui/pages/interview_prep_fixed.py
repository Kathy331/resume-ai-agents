#!/usr/bin/env python3
"""
Enhanced Interview Prep Page - Multi-Tab Interface
=================================================

Features:
- Tabs for different emails/companies
- Tab names as company names
- Save Changes & Download per tab
- Send 1 to Email / Send All to Email buttons
- Separate Generate and Clear Cache buttons
"""

import streamlit as st
import subprocess
import sys
from pathlib import Path
import glob
import os
from datetime import datetime

# Import Gmail services for email sending
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.google_oauth.dual_gmail_services import get_user_gmail_service, get_bot_gmail_service, check_gmail_authentication

def extract_prep_guide_template(full_content: str) -> str:
    """Extract only the interview prep requirements template from full content"""
    lines = full_content.split('\n')
    
    # Find the start of the prep guide template
    start_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "# interview prep requirements template":
            start_idx = i + 1  # Skip the title line
            break
    
    if start_idx == -1:
        # Try to find just the sections without title
        for i, line in enumerate(lines):
            if line.strip().startswith("## 1. before interview"):
                start_idx = i
                break
    
    if start_idx == -1:
        return "No prep guide template found in the generated content."
    
    # Find the end of the prep guide template (before technical sections)
    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if (line.startswith("====") or 
            line.startswith("RESEARCH CITATIONS") or
            line.startswith("TECHNICAL METADATA") or
            line.startswith("CRITICAL SUCCESS CRITERIA")):
            end_idx = i
            break
    
    # Extract only the template content
    template_lines = lines[start_idx:end_idx]
    
    # Clean up empty lines at the end
    while template_lines and not template_lines[-1].strip():
        template_lines.pop()
    
    return '\n'.join(template_lines)

def extract_company_name_from_file(file_path: Path) -> str:
    """Extract company name from the generated file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for company name in metadata section
        lines = content.split('\n')
        for line in lines:
            if line.startswith("Company:"):
                return line.replace("Company:", "").strip()
        
        # Fallback to filename
        return file_path.stem
    except:
        return file_path.stem

def load_all_prep_guides() -> dict:
    """Load all prep guide files and extract clean templates"""
    output_dir = Path("outputs/fullworkflow")
    prep_guides = {}
    
    if output_dir.exists():
        txt_files = list(output_dir.glob("*.txt"))
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                company_name = extract_company_name_from_file(file_path)
                clean_template = extract_prep_guide_template(content)
                
                prep_guides[company_name] = {
                    'content': clean_template,
                    'file_path': str(file_path),
                    'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                }
            except Exception as e:
                st.error(f"Error loading {file_path}: {e}")
    
    return prep_guides

def clear_cache_only():
    """Clear OpenAI cache only and reset prep guides completely"""
    try:
        result = subprocess.run([
            sys.executable, "workflows/cache_manager.py", "--clear-openai"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            # Clear outputs/fullworkflow folder
            output_dir = Path("outputs/fullworkflow")
            if output_dir.exists():
                import shutil
                try:
                    # Remove all files in the directory
                    for file_path in output_dir.glob("*"):
                        if file_path.is_file():
                            file_path.unlink()
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                    st.info("🗂️ Cleared outputs/fullworkflow folder")
                except Exception as e:
                    st.warning(f"⚠️ Could not clear outputs folder: {str(e)}")
            
            # Clear ALL session state related to prep guides
            keys_to_clear = []
            for key in list(st.session_state.keys()):
                if any(term in key.lower() for term in ['prep', 'guide', 'edited']):
                    keys_to_clear.append(key)
            
            for key in keys_to_clear:
                del st.session_state[key]
            
            # Also remove any cached file references
            if hasattr(st.session_state, 'cached_prep_guides'):
                del st.session_state.cached_prep_guides
            
            st.success("🧹 ✅ Cache cleared successfully! All prep guides and output files removed.")
            st.rerun()  # Force complete refresh
        else:
            st.error(f"❌ Failed to clear cache: {result.stderr}")
    except Exception as e:
        st.error(f"❌ Error clearing cache: {str(e)}")

def run_workflow_only():
    """Run the workflow without clearing cache - show terminal logs in real-time"""
    try:
        st.write("🚀 Running interview prep workflow...")
        
        # Run workflow with real-time terminal output (not captured)
        result = subprocess.run([
            sys.executable,
            "workflows/interview_prep_workflow.py",
            "--folder", "demo",
            "--max-emails", "5"  # Process multiple emails
        ], cwd=Path.cwd())  # Remove capture_output=True to show logs in terminal
        
        if result.returncode == 0:
            st.success("✅ Workflow completed successfully!")
            return True
        else:
            st.error(f"❌ Workflow failed with return code: {result.returncode}")
            return False
    except Exception as e:
        st.error(f"❌ Error running workflow: {str(e)}")
        return False

def send_prep_guide_to_email(company_name: str, content: str):
    """Send a single prep guide to email using bot service with professional styling"""
    try:
        # Use bot service which has send permissions
        bot_service = get_bot_gmail_service()
        if not bot_service:
            st.error("❌ Bot email service not authenticated. Please run `python setup_bot_email.py` and choose option 2.")
            return
        
        # Send to the authenticated user's email
        user_email = "liveinthemoment780@gmail.com"
        
        # Create styled HTML email content
        subject = f"🎯 Interview Prep Guide - {company_name}"
        
        # Convert markdown links to HTML in content
        import re
        html_content = content.replace('\n', '<br>')
        # Convert [text](url) to <a href="url">text</a>
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        html_content = re.sub(link_pattern, r'<a href="\2" style="color: #1f77b4; text-decoration: underline;">\1</a>', html_content)
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Prep Guide</title>
</head>
<body style="margin: 0; padding: 10px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 95%; width: 100%; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #DDF1F6, #125584); padding: 30px; text-align: center; border: 3px solid #125584;">
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                🎯 Interview Prep Guide
            </h1>
            <h2 style="color: white; margin: 10px 0 0 0; font-size: 20px; font-weight: 500; opacity: 0.9;">
                Company: {company_name}
            </h2>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px; line-height: 1.6; color: #333;">
            <div style="font-size: 16px;">
                {html_content}
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
            <p style="margin: 0; color: #6c757d; font-size: 14px;">
                Generated by <strong>Interview Prep AI</strong> • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
            <p style="margin: 10px 0 0 0; color: #6c757d; font-size: 12px;">
                Best of luck with your interview! 🚀
            </p>
        </div>
        
    </div>
</body>
</html>
        """
        
        # Create message using bot service
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart('alternative')
        message['to'] = user_email
        message['subject'] = subject
        
        # Create both plain text and HTML versions
        text_content = f"""🎯 Interview Prep Guide - {company_name}

{content}

---
Generated by Interview Prep AI • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Best of luck with your interview!"""
        
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send email using bot service
        send_message = bot_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        st.success(f"📧 ✅ {company_name} prep guide sent to {user_email}!")
        
    except Exception as e:
        st.error(f"❌ Error sending email: {str(e)}")
        st.info("💡 Make sure bot email is authenticated with send permissions: python setup_bot_email.py (option 2)")

def send_all_prep_guides_to_email(prep_guides: dict):
    """Send all prep guides to email using bot service with professional styling"""
    try:
        # Use bot service which has send permissions
        bot_service = get_bot_gmail_service()
        if not bot_service:
            st.error("❌ Bot email service not authenticated. Please run `python setup_bot_email.py` and choose option 2.")
            return
        
        # Send to the authenticated user's email
        user_email = "liveinthemoment780@gmail.com"
        
        # Create styled HTML email content for all guides
        subject = f"🎯 All Interview Prep Guides ({len(prep_guides)} companies)"
        
        # Build HTML content for all companies
        companies_html = ""
        companies_text = ""
        
        for i, (company_name, guide_data) in enumerate(prep_guides.items()):
            # Convert markdown links to HTML
            import re
            html_content = guide_data['content'].replace('\n', '<br>')
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            html_content = re.sub(link_pattern, r'<a href="\2" style="color: #1f77b4; text-decoration: underline;">\1</a>', html_content)
            
            companies_html += f"""
            <div style="margin-bottom: 40px; border-bottom: 2px solid #e9ecef; padding-bottom: 30px;">
                <h2 style="color: #125584; font-size: 24px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #DDF1F6;">
                    🏢 {company_name}
                </h2>
                <div style="font-size: 16px; line-height: 1.6;">
                    {html_content}
                </div>
            </div>
            """
            
            companies_text += f"""
🏢 {company_name}
{'='*50}

{guide_data['content']}

{'='*50}

"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Interview Prep Guides</title>
</head>
<body style="margin: 0; padding: 10px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 95%; width: 100%; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #DDF1F6, #125584); padding: 30px; text-align: center; border: 3px solid #125584;">
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                🎯 Interview Prep Guides
            </h1>
            <h2 style="color: white; margin: 10px 0 0 0; font-size: 18px; font-weight: 500; opacity: 0.9;">
                {len(prep_guides)} Companies Included
            </h2>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px; color: #333;">
            {companies_html}
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
            <p style="margin: 0; color: #6c757d; font-size: 14px;">
                Generated by <strong>Interview Prep AI</strong> • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
            <p style="margin: 10px 0 0 0; color: #6c757d; font-size: 12px;">
                Best of luck with all your interviews! 🚀
            </p>
        </div>
        
    </div>
</body>
</html>
        """
        
        # Create message using bot service
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart('alternative')
        message['to'] = user_email
        message['subject'] = subject
        
        # Create both plain text and HTML versions
        text_content = f"""🎯 All Interview Prep Guides ({len(prep_guides)} companies)

{companies_text}

Generated by Interview Prep AI • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Best of luck with all your interviews!"""
        
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send email using bot service
        send_message = bot_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        st.success(f"📧 ✅ All {len(prep_guides)} prep guides sent to {user_email}!")
        
    except Exception as e:
        st.error(f"❌ Error sending all guides: {str(e)}")
        st.info("💡 Make sure bot email is authenticated with send permissions: python setup_bot_email.py (option 2)")

def render_interview_prep():
    """Render the enhanced interview prep page with tabs"""
    
    # Add custom CSS for rounded tabs with proper styling and hyperlinks
    st.markdown("""
    <style>
    /* Tab container styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
        padding: 4px;
    }
    
    /* Individual tab styling */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 8px 20px !important;
        border-radius: 12px !important;
        background-color: #DDF1F6 !important;
        color: #125584 !important;
        border: 2px solid #125584 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        margin: 0 4px !important;
        min-width: auto !important;
        white-space: nowrap !important;
    }
    
    /* Active/selected tab styling */
    .stTabs [aria-selected="true"] {
        background-color: #125584 !important;
        color: white !important;
        border: 2px solid #125584 !important;
        box-shadow: 0 2px 8px rgba(18, 85, 132, 0.3) !important;
    }
    
    /* Hover effect for inactive tabs */
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #FBA09F !important;
        color: #125584 !important;
        border: 2px solid #FBA09F !important;
    }
    
    /* Tab content area */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 20px 0 !important;
        background-color: transparent !important;
    }
    
    /* Ensure text inside tabs is properly styled */
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] div {
        color: inherit !important;
        font-weight: inherit !important;
    }
    
    /* Remove any underlines from tab text */
    .stTabs [data-baseweb="tab"] {
        text-decoration: none !important;
    }
    
    /* Active tab text color override */
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div {
        color: white !important;
    }
    
    /* Fix hyperlinks in text areas to be visible */
    .stTextArea textarea {
        line-height: 1.6 !important;
    }
    
    /* Style for hyperlinks in markdown display */
    .stMarkdown a {
        color: #1f77b4 !important;
        text-decoration: underline !important;
    }
    
    .stMarkdown a:hover {
        color: #0d5aa7 !important;
        text-decoration: underline !important;
    }
    
    /* Style hyperlinks in any content */
    a {
        color: #1f77b4 !important;
        text-decoration: underline !important;
    }
    
    a:hover {
        color: #0d5aa7 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📚 Interview Prep AI")
    st.markdown("*Generate and manage personalized interview preparation guides*")
    
    # Authentication check
    st.info("📧 Make sure your Gmail is authenticated using `python setup_bot_email.py`")
    
    # Control buttons section
    st.markdown("### 🎛️ Controls")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎯 Generate Prep Guides", key="generate_prep", type="primary"):
            with st.spinner("Generating interview prep guides..."):
                success = run_workflow_only()
                if success:
                    st.rerun()
    
    with col2:
        if st.button("🧹 Clear Cache", key="clear_cache"):
            clear_cache_only()
    
    with col3:
        if st.button("🔄 Refresh", key="refresh"):
            st.rerun()
    
    # Load all prep guides
    prep_guides = load_all_prep_guides()
    
    # Force clear display if cache was just cleared (check session state)
    if 'cache_just_cleared' in st.session_state:
        prep_guides = {}  # Override to show empty state
        del st.session_state['cache_just_cleared']
    
    # Check if session state has edited guides but no files exist (after cache clear)
    if 'edited_guides' in st.session_state and not prep_guides:
        # Clear session state if no files exist
        del st.session_state.edited_guides
    
    if not prep_guides:
        # Show clean state before generation
        st.markdown("### 🎯 Ready to Generate Interview Prep Guides")
        
        st.markdown("""
        <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 10px; border: 2px dashed #125584; margin: 20px 0;">
            <h3 style="color: #125584; margin-bottom: 20px;">📚 No Interview Prep Guides Available</h3>
            <p style="color: #6c757d; font-size: 16px; margin-bottom: 30px;">Click the button above to generate personalized prep guides from your emails</p>
            <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #125584; text-align: left; max-width: 500px; margin: 0 auto;">
                <strong style="color: #125584;">What you'll get:</strong>
                <ul style="color: #333; margin-top: 10px;">
                    <li>📅 Interview scheduling details</li>
                    <li>👤 Interviewer background research</li>
                    <li>🏢 Company information and insights</li>
                    <li>💼 Technical preparation requirements</li>
                    <li>❓ Potential interview questions</li>
                    <li>📝 Key talking points and tips</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return    # Display prep guides in tabs
    st.markdown("### 📋 Interview Prep Guides")
    
    # Create tabs with company names
    company_names = list(prep_guides.keys())
    tabs = st.tabs([f"🏢 {name}" for name in company_names])
    
    # Initialize session state for edited content
    if 'edited_guides' not in st.session_state:
        st.session_state.edited_guides = {}
    
    for i, (company_name, guide_data) in enumerate(prep_guides.items()):
        with tabs[i]:
            st.markdown(f"#### {company_name}")
            st.caption(f"Last updated: {guide_data['last_modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Initialize edited content for this company if not exists
            if company_name not in st.session_state.edited_guides:
                st.session_state.edited_guides[company_name] = guide_data['content']
            
            # Editable text area
            edited_content = st.text_area(
                "Interview Prep Requirements Template:",
                value=st.session_state.edited_guides[company_name],
                height=500,
                key=f"prep_guide_{company_name}",
                help="Edit the content as needed. Links will be clickable when downloaded."
            )
            
            # Update session state when content changes
            st.session_state.edited_guides[company_name] = edited_content
            
            # Show preview with clickable links
            if "[" in edited_content and "](" in edited_content:
                st.markdown("##### 🔗 Link Preview:")
                # Convert markdown links to HTML for preview
                import re
                preview_content = edited_content
                # Convert [text](url) to clickable links
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                preview_content = re.sub(link_pattern, r'<a href="\2" target="_blank">\1</a>', preview_content)
                
                # Show first few lines with links
                preview_lines = preview_content.split('\n')[:10]
                for line in preview_lines:
                    if '<a href=' in line:
                        st.markdown(line, unsafe_allow_html=True)
                        break
            
            # Action buttons for this tab
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                if st.button("💾 Save Changes", key=f"save_{company_name}"):
                    st.session_state.edited_guides[company_name] = edited_content
                    st.success("✅ Changes saved!")
            
            with col2:
                st.download_button(
                    label="📥 Download",
                    data=edited_content,
                    file_name=f"{company_name}_prep_guide.md",
                    mime="text/markdown",
                    key=f"download_{company_name}"
                )
            
            with col3:
                if st.button("� Send to Email", key=f"send_{company_name}"):
                    send_prep_guide_to_email(company_name, edited_content)
            
            with col4:
                # Show file info
                st.caption(f"📁 {Path(guide_data['file_path']).name}")
    
    # Global action buttons
    if prep_guides:
        st.markdown("### 🌐 Global Actions")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📧 Send All to Email", key="send_all"):
                # Use edited content from session state
                guides_to_send = {}
                for company_name in prep_guides.keys():
                    guides_to_send[company_name] = {
                        'content': st.session_state.edited_guides.get(company_name, prep_guides[company_name]['content'])
                    }
                send_all_prep_guides_to_email(guides_to_send)
        
        with col2:
            # Show summary stats
            st.metric("Total Guides", len(prep_guides))
        
        with col3:
            st.info("💡 Use tabs above to edit individual guides, or send all at once")

if __name__ == "__main__":
    render_interview_prep()