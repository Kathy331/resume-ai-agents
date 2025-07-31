"""
email_pipeline.py: 

setup_gmail
   ↓
fetch_emails
   ↓
classify_emails
   ↓
(for Interview_invite)
   ↳ entity_extraction_node
      ↓
   check_existing_interviews_node
      ↓
    if duplicate: → skip_research_node → format_output
    else: → tavily_research_node → format_output


"""