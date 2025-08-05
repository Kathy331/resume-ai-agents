STRUCTURED_SUMMARY_PROMPT = """
You are an intelligent resume parser. Extract structured information from the following resume text.
Return the output in this JSON format:
{{
  "name": "",
  "email": "",
  "phone": "",
  "summary": "",
  "education": [],
  "experience": [],
  "skills": []
}}

Resume Text:
{text}

Respond ONLY with a valid JSON object.
"""