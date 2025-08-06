#!/usr/bin/env python3
"""
Enhanced Interview Prep Page - Multi-Tab Interface (Fixed)
=========================================================

Features:
- Tabs for different emails/companies (cleared properly on cache clear)
- Real email sending to authenticated user
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
from shared.google_oauth.dual_gmail_services import get_bot_gmail_service

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

def clear_cache_and_guides():
    """Clear OpenAI cache and completely remove all prep guides from session"""
    try:
        result = subprocess.run([
            sys.executable, "workflows/cache_manager.py", "--clear-openai"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            # Completely clear all session state related to prep guides
            keys_to_remove = []
            for key in st.session_state.keys():
                if any(term in key.lower() for term in ['prep', 'guide', 'edited']):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del st.session_state[key]
            
            st.success("🧹 ✅ Cache cleared! All prep guides removed from display.")
            st.rerun()
        else:
            st.error(f"❌ Failed to clear cache: {result.stderr}")
    except Exception as e:
        st.error(f"❌ Error clearing cache: {str(e)}")

def run_workflow_only():
    """Run the workflow without clearing cache"""
    try:
        st.write("🚀 Running interview prep workflow...")
        result = subprocess.run([
            sys.executable,
            "workflows/interview_prep_workflow.py",
            "--folder", "demo",
            "--max-emails", "5"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            st.success("✅ Workflow completed successfully!")
            return True
        else:
            st.error(f"❌ Workflow failed: {result.stderr}")
            return False
    except Exception as e:
        st.error(f"❌ Error running workflow: {str(e)}")
        return False

def send_single_guide_to_email(company_name: str, content: str):
    """Send a single prep guide via Gmail bot service"""
    try:
        bot_service = get_bot_gmail_service()
        if not bot_service:
            st.error("❌ Bot email not authenticated. Run: python setup_bot_email.py")
            return
        
        user_email = "liveinthemoment780@gmail.com"
        subject = f"Interview Prep Guide - {company_name}"
        
        email_body = f"""Hi!

Here's your personalized interview preparation guide for {company_name}:

{content}

---
Best of luck with your interview!

Sent by Resume AI Assistant"""
        
        # Create and send email
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart()
        message['to'] = user_email
        message['subject'] = subject
        message.attach(MIMEText(email_body, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw_message}
        
        result = bot_service.users().messages().send(userId='me', body=send_message).execute()
        
        if result:
            st.success(f"📧 ✅ {company_name} guide sent to {user_email}!")
        else:
            st.error("❌ Failed to send email")
            
    except Exception as e:
        st.error(f"❌ Email error: {str(e)}")

def send_all_guides_to_email(prep_guides: dict):
    """Send all prep guides in one email"""
    try:
        bot_service = get_bot_gmail_service()
        if not bot_service:
            st.error("❌ Bot email not authenticated. Run: python setup_bot_email.py")
            return
        
        user_email = "liveinthemoment780@gmail.com"
        subject = f"All Interview Prep Guides ({len(prep_guides)} companies)"
        
        combined_content = "Hi!\n\nHere are all your interview preparation guides:\n\n"
        
        for company_name, guide_data in prep_guides.items():
            combined_content += f"## {company_name}\n\n{guide_data['content']}\n\n{'='*50}\n\n"
        
        combined_content += "Best of luck with all your interviews!\n\nSent by Resume AI Assistant"
        
        # Create and send email
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart()
        message['to'] = user_email
        message['subject'] = subject
        message.attach(MIMEText(combined_content, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw_message}
        
        result = bot_service.users().messages().send(userId='me', body=send_message).execute()
        
        if result:
            st.success(f"📧 ✅ All {len(prep_guides)} guides sent to {user_email}!")
        else:
            st.error("❌ Failed to send email")
            
    except Exception as e:
        st.error(f"❌ Email error: {str(e)}")

def render_interview_prep():
    """Main render function with proper cache clearing and email sending"""
    
    # Add CSS styling for tabs and links
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
        padding: 4px;
    }
    
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
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #125584 !important;
        color: white !important;
        border: 2px solid #125584 !important;
        box-shadow: 0 2px 8px rgba(18, 85, 132, 0.3) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #FBA09F !important;
        color: #125584 !important;
        border: 2px solid #FBA09F !important;
    }
    
    .stMarkdown a {
        color: #1f77b4 !important;
        text-decoration: underline !important;
    }
    
    .stMarkdown a:hover {
        color: #0d5aa7 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📚 Interview Prep AI")
    st.markdown("*Generate and manage personalized interview preparation guides*")
    
    # Authentication check
    st.info("📧 Make sure your Gmail is authenticated using `python setup_bot_email.py`")
    
    # Control buttons
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
            clear_cache_and_guides()
    
    with col3:
        if st.button("🔄 Refresh", key="refresh"):
            st.rerun()
    
    # Load prep guides (will be empty if cache was cleared)
    prep_guides = load_all_prep_guides()
    
    if not prep_guides:
        st.info("👆 Click 'Generate Prep Guides' to create personalized guides from your emails")
        
        st.markdown("#### 📖 Example Output:")
        st.code("""## 1. before interview
- email mentions date options: Tuesday, August 6 or Wednesday, August 7
- time: flexible between 10:00 a.m. and 4:00 p.m. (ET)

## 2. interviewer background
- rakesh gohel is a professional at juteq with expertise in AI
- [rakesh gohel linkedin](https://ca.linkedin.com/in/rakeshgohel01)

## 3. company background
- juteq is a technology company specializing in AI and cloud-native solutions
- [juteq linkedin](https://ca.linkedin.com/company/juteq)

... (sections 4-6 continue with specific technical prep, questions, etc.)
""", language="markdown")
        return
    
    # Display prep guides in tabs
    st.markdown("### 📋 Interview Prep Guides")
    
    company_names = list(prep_guides.keys())
    tabs = st.tabs([f"🏢 {name}" for name in company_names])
    
    # Initialize session state for edited content
    if 'edited_guides' not in st.session_state:
        st.session_state.edited_guides = {}
    
    for i, (company_name, guide_data) in enumerate(prep_guides.items()):
        with tabs[i]:
            st.markdown(f"#### {company_name}")
            st.caption(f"Last updated: {guide_data['last_modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Initialize edited content
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
            
            # Update session state
            st.session_state.edited_guides[company_name] = edited_content
            
            # Show link preview
            if "[" in edited_content and "](" in edited_content:
                st.markdown("##### 🔗 Link Preview:")
                import re
                preview_content = edited_content
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                preview_content = re.sub(link_pattern, r'<a href="\2" target="_blank">\1</a>', preview_content)
                
                preview_lines = preview_content.split('\n')[:10]
                for line in preview_lines:
                    if '<a href=' in line:
                        st.markdown(line, unsafe_allow_html=True)
                        break
            
            # Action buttons
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
                if st.button("📧 Send to Email", key=f"send_{company_name}"):
                    send_single_guide_to_email(company_name, edited_content)
            
            with col4:
                st.caption(f"📁 {Path(guide_data['file_path']).name}")
    
    # Global actions
    if prep_guides:
        st.markdown("### 🌐 Global Actions")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📧 Send All to Email", key="send_all"):
                guides_to_send = {}
                for company_name in prep_guides.keys():
                    guides_to_send[company_name] = {
                        'content': st.session_state.edited_guides.get(company_name, prep_guides[company_name]['content'])
                    }
                send_all_guides_to_email(guides_to_send)
        
        with col2:
            st.metric("Total Guides", len(prep_guides))
        
        with col3:
            st.info("💡 Use tabs above to edit individual guides, or send all at once")

if __name__ == "__main__":
    render_interview_prep()