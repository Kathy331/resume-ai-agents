#!/usr/bin/env python3
"""
Prep Guide HTML Formatter
========================

Convert markdown prep guides to HTML format matching the guidelines example.
"""

import re
from typing import Dict, Any

def convert_prep_guide_to_html(markdown_content: str) -> str:
    """Convert markdown prep guide to HTML format matching the example"""
    
    # Start with the container
    html = '<div style="font-family: sans-serif; font-size: 16px; line-height: 1.5;">\n'
    html += '  <p>📋 Interview Prep Guide<br>\n'
    
    # Split into sections
    sections = re.split(r'\n## \d+\.\s*', markdown_content)
    
    # Process each section
    for i, section in enumerate(sections):
        if not section.strip():
            continue
            
        # Skip the title section
        if section.startswith('# interview prep requirements template'):
            continue
            
        # Determine section number and title
        if 'before interview' in section.lower():
            section_num = 1
            section_title = "Before Interview"
        elif 'interviewer background' in section.lower():
            section_num = 2
            section_title = "Interviewer Background"
        elif 'company background' in section.lower():
            section_num = 3
            section_title = "Company Background"
        elif 'technical preparations' in section.lower():
            section_num = 4
            section_title = "Technical Preparations"
        elif 'questions to ask' in section.lower():
            section_num = 5
            section_title = "Questions to Ask"
        elif 'common questions' in section.lower():
            section_num = 6
            section_title = "Common Questions"
        else:
            continue
        
        # Add section header
        html += f'  {section_num}. {section_title}:<br>\n'
        
        # Process section content
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Handle bullet points
            if line.startswith('- '):
                content = line[2:].strip()
                # Convert markdown links to HTML
                content = convert_markdown_links_to_html(content)
                html += f'  - {content}<br>\n'
            
            # Handle sub-bullets (indented)
            elif line.startswith('  - '):
                content = line[4:].strip()
                content = convert_markdown_links_to_html(content)
                html += f'    - {content}<br>\n'
            
            # Handle "to interviewer:" and "to company:" labels
            elif line.startswith('- to '):
                label = line[2:].strip()
                html += f'  {label.title()}:<br>\n'
    
    html += '  </p>\n</div>'
    return html

def convert_markdown_links_to_html(text: str) -> str:
    """Convert markdown links [text](url) to HTML links"""
    # Pattern: [text](url)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    replacement = r'<a href="\2" target="_blank">\1</a>'
    return re.sub(pattern, replacement, text)

def generate_juteq_clean_content() -> str:
    """Generate clean JUTEQ prep guide content without title"""
    
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

def generate_dandilyonn_clean_content() -> str:
    """Generate clean Dandilyonn SEEDS prep guide content without title"""
    
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

if __name__ == "__main__":
    print("🎨 JUTEQ HTML Prep Guide:")
    print("=" * 50)
    print(generate_juteq_html())
    print("\n" + "=" * 50)
    
    print("\n🎨 Dandilyonn SEEDS HTML Prep Guide:")
    print("=" * 50)
    print(generate_dandilyonn_html())