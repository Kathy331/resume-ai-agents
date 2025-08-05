"""
 TODO: This may not be needed
"""

# from typing import Dict 
# import pymupdf
# import docx
# import fitz
# import re

# def extract_text(file: bytes, file_type: str) -> str:
#     """
#     Extracts raw text from a resume file. 
#     Supported types: 'pdf', 'docx', and 'txt'.
#     """
#     # Handles 'pdf'
#     if file_type == "pdf":
#         doc = fitz.open(stream=file, filetype="pdf")
#         return "\n".join([page.get_text() for page in doc])
    
#     # Handles 'docx'
#     elif file_type == "docx":
#         document = docx.Document(file)
#         return "\n".join([para.text for para in document.paragraphs])
    
#     # Handles 'txt'
#     elif file_type == "text":
#         return file.decode("utf-8")
    
#     # Handles other types
#     else: 
#         raise ValueError("Unsupported file type: {file_type}")

# def parse_sections(text:str) -> Dict[str, str]:
#     """
#     Naively split resume text into sections like Education, Experience, etc.
#     This can be refined later with ML or regex rules.
#     """
#     sections = {}
#     lines = text.splitlines()
#     current_section = "General"
#     buffer = []

#     section_keywords = {
#         "education": ["education", "university", "degree"],
#         "experience": ["experience", "work", "employment"],
#         "projects": ["projects", "portfolio"],
#         "skills": ["skills", "technologies", "tools"],
#         "certifications": ["certification", "license"]
#     }

#     def match_section(line):
#         """
#         TODO: Fill in
#         """
#         lower = line.lower()
#         for name, keywords in section_keywords.items():
#             if any(k in lower for k in keywords):
#                 return name.capitalize
#         return None
    
#     for line in lines:
#         new_section = match_section(line)
#         if new_section:
#             sections[current_section] = "\n".join(buffer).strip()
#             current_section = new_section
#             buffer = []
#         else:
#             buffer.append
#     sections[current_section] = "\n".join(buffer).strip()
#     return sections