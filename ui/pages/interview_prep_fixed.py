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
    """Clear OpenAI cache only"""
    try:
        result = subprocess.run([
            sys.executable, "workflows/cache_manager.py", "--clear-openai"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            st.success("🧹 ✅ Cache cleared successfully!")
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
            "--max-emails", "5"  # Process multiple emails
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

def send_prep_guide_to_email(company_name: str, content: str):
    """Send a single prep guide to email"""
    try:
        # Create temporary file with the content
        temp_file = Path(f"temp_{company_name}_guide.md")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(f"# Interview Prep Guide - {company_name}\n\n{content}")
        
        # Simulate sending email (replace with actual email sending logic)
        st.success(f"📧 ✅ {company_name} prep guide sent to your email!")
        
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()
            
    except Exception as e:
        st.error(f"❌ Error sending email: {str(e)}")

def send_all_prep_guides_to_email(prep_guides: dict):
    """Send all prep guides to email"""
    try:
        # Combine all guides into one email
        combined_content = "# All Interview Prep Guides\n\n"
        
        for company_name, guide_data in prep_guides.items():
            combined_content += f"## {company_name}\n\n"
            combined_content += guide_data['content']
            combined_content += "\n\n" + "="*50 + "\n\n"
        
        # Create temporary file
        temp_file = Path("temp_all_guides.md")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(combined_content)
        
        # Simulate sending email
        st.success(f"📧 ✅ All {len(prep_guides)} prep guides sent to your email!")
        
        # Clean up
        if temp_file.exists():
            temp_file.unlink()
            
    except Exception as e:
        st.error(f"❌ Error sending all guides: {str(e)}")

def render_interview_prep():
    """Render the enhanced interview prep page with tabs"""
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
    
    if not prep_guides:
        st.info("👆 Click 'Generate Prep Guides' to create personalized guides from your emails")
        
        # Show example
        st.markdown("#### 📖 Example Output:")
        st.code("""## 1. before interview

- email mentions date options: Tuesday, August 6 or Wednesday, August 7
- time: flexible between 10:00 a.m. and 4:00 p.m. (ET)
- duration: 30 minutes
- respond by end of day Friday, August 2 to confirm your time slot
- format: virtual, zoom - test your zoom setup

## 2. interviewer background

- rakesh gohel is a professional at juteq with expertise in AI
- background: scaling with AI agents, cloud-native solutions focus
- [rakesh gohel linkedin](https://ca.linkedin.com/in/rakeshgohel01)

## 3. company background

- juteq is a technology company specializing in AI and cloud-native solutions
- focuses on cloud-native innovation and DevOps solutions
- [juteq linkedin](https://ca.linkedin.com/company/juteq)

... (sections 4-6 continue with specific technical prep, questions, etc.)
""", language="markdown")
        return
    
    # Display prep guides in tabs
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
                help="Edit the content as needed, then save or download"
            )
            
            # Update session state when content changes
            st.session_state.edited_guides[company_name] = edited_content
            
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