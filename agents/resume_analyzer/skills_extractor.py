
"""
TODO: this may not be needed
"""
# import re
# from typing import Dict, List

# def extract_skills(text:str) -> Dict[str, List[str]]:
#     """
#     Extract technical and soft skills from text using keyword lists.
#     This is a rule-based version—you can later replace with ML/NLP models.
#     """
#     technical_keywords = [
#         "python", "javascript", "sql", "react", "node", "java", "aws", "docker",
#         "kubernetes", "git", "linux", "c++", "typescript"
#     ]

#     soft_keywords = [
#         "leadership", "communication", "teamwork", "problem solving",
#         "adaptability", "time management", "creativity"
#     ]

#     text_lower = text.lower()
#     tech_skills = [
#         {"skill": skill, "proficiency": "Unknown", "years": None, "frequency": text_lower.count(skill)}
#         for skill in technical_keywords if skill in text_lower
#     ]

#     soft_skills = [
#         {"skill": skill.capitalize(), "evidence": "", "context": ""}
#         for skill in soft_keywords if skill in text_lower
#     ]

#     return {
#         "Technical Skills": tech_skills,
#         "Soft Skills": soft_skills
#     }