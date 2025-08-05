# Interview Prep Guide Generation Guidelines

## Overview
This document outlines the structured approach for generating comprehensive, research-backed interview preparation guides that provide actionable insights with proper citations and validation systems.

## Core Principles

### 1. **Research-Driven Content**
- All recommendations must be backed by specific research findings
- Include proper citations with clickable links
- Validate information through multiple sources
- Use reflection loops to identify and fill information gaps

### 2. **Structured Format Consistency**
- Follow the 8-section framework outlined below
- Use emoji icons for visual organization
- Provide specific, actionable bullet points
- Include timeline-based preparation steps

### 3. **Personalization Requirements**
- Tailor content to specific company, role, and interviewer
- Include candidate-specific talking points
- Adapt technical focus based on job requirements
- Reference interviewer's background and interests

## Minimum Viable Guide (MVG) Threshold

### Purpose
Not all interviews will have abundant data available. The MVG defines the absolute minimum acceptable standard for a prep guide after 3 reflection loops. If these thresholds aren't met, the system will provide specific warnings about information gaps.

### MVG Criteria (Must achieve ALL to pass)

#### **Critical Sections (Must be Complete)**
- ✅ **Section 1: Summary Overview** - All available logistics captured
- ✅ **Section 2: Company Snapshot** - Minimum 3 factual insights with citations
- ✅ **Section 3: Role Deep Dive** - Job description analysis complete
- ✅ **Section 4: Interviewer Intelligence** - At least basic professional info gathered

#### **Content Quality Minimums**
- ✅ **Minimum 5 Citations**: At least 5 working citations across all sections
- ✅ **Company Specificity**: At least 3 company-specific (not generic) insights
- ✅ **Recent Information**: At least 2 pieces of information from last 12 months
- ✅ **Actionable Questions**: Minimum 8 specific questions across categories
- ✅ **Technical Alignment**: Technical prep matches job requirements (if technical role)

#### **Research Depth Minimums**
- ✅ **Company Research**: Mission, recent news, and 1 competitive insight
- ✅ **Role Context**: Key responsibilities and required skills identified
- ✅ **Interviewer Profile**: Name, title, and basic background (LinkedIn minimum)
- ✅ **Preparation Timeline**: At least 24-hour countdown checklist

### MVG Scoring Thresholds

#### **Aggregate Score Requirements**
- **Content Depth**: Minimum 5/10 (at least "Adequate")
- **Personalization**: Minimum 4/10 (basic customization present)
- **Citation Quality**: Minimum 5/10 (some working citations)
- **Overall MVG Score**: Minimum 15/30 combined

#### **Section-Specific Minimums**

**Section 1 - Summary Overview (MVG: Complete)**
- Company name and role title confirmed
- Interview logistics captured (even if incomplete)
- Format and platform identified

**Section 2 - Company Snapshot (MVG: 3 insights + 2 citations)**
- Company mission/description
- At least 1 recent development with citation
- Basic market position or tech stack info with citation

**Section 3 - Role Deep Dive (MVG: Job analysis + 1 citation)**
- Core responsibilities summarized
- Key technical requirements identified
- At least 1 insight about team/role context

**Section 4 - Interviewer Intelligence (MVG: Basic profile + 1 citation)**
- Name and title confirmed
- LinkedIn profile or professional background
- At least 1 specific insight about their role/expertise

**Sections 5-8 (MVG: Functional but may be generic)**
- Questions present (may include some generic ones)
- Basic technical preparation (even if general)
- Timeline structure exists
- Strategic guidance provided

### Warning System for Sub-MVG Guides

#### **Critical Warnings (Block delivery)**
```
⚠️ CRITICAL: This prep guide does not meet minimum viable standards.
Missing essential elements:
• [Specific missing sections]
• [Citation count: X/5 minimum]
• [Company-specific insights: X/3 minimum]

Recommendation: Additional research required before interview.
```

#### **Quality Warnings (Deliver with caveats)**
```
📋 QUALITY NOTICE: This prep guide meets minimum standards but has limitations:
• Limited recent company information available
• [Specific interviewer intel missing]
• [Technical preparation may be generic]

Suggestion: Supplement with additional manual research.
```

#### **Information Gap Warnings (Specific guidance)**
```
🔍 RESEARCH GAPS IDENTIFIED:
Company Intelligence:
• ❌ No recent news/developments found
• ❌ Limited technical stack information
• ✅ Basic company profile complete

Interviewer Intelligence:
• ❌ No recent LinkedIn activity found
• ❌ Limited professional background
• ✅ Basic role information available

Technical Preparation:
• ⚠️  Generic technical advice (role-specific info limited)
• ✅ Basic preparation framework provided

RECOMMENDED ACTIONS:
1. Manual LinkedIn search for [Interviewer Name]
2. Check company engineering blog: [suggested URL]
3. Review job posting for additional technical details
```

### Fallback Strategies for Missing Information

#### **When Company Information is Limited**
1. **Industry-Standard Approach**: Use role-based technical preparation
2. **Generic Company Research**: Focus on publicly available information
3. **Competitor Analysis**: Research similar companies in same space
4. **Role-Focused Strategy**: Emphasize technical competencies over company specifics

#### **When Interviewer Information is Unavailable**
1. **Team-Based Preparation**: Research the team/department generally
2. **Role-Based Questions**: Focus on position-specific inquiries
3. **Company Culture Focus**: Prepare questions about team dynamics
4. **Technical Leadership Angle**: Assume technical discussion focus

#### **When Recent Company News is Scarce**
1. **Historical Context**: Use older but significant company milestones
2. **Industry Trends**: Connect company to broader industry movements
3. **Product Focus**: Deep dive on company's main products/services
4. **Market Position**: Analyze competitive landscape thoroughly

### Automated MVG Assessment

#### **Post-Reflection 3 Checklist**
```python
def assess_mvg_compliance(prep_guide):
    mvg_score = {
        'critical_sections': check_critical_sections_complete(),
        'citation_count': count_working_citations(),
        'company_specificity': assess_company_specific_content(),
        'recent_info': count_recent_information(),
        'actionable_questions': count_specific_questions(),
        'technical_alignment': assess_technical_relevance()
    }
    
    if mvg_score['total'] < MVG_THRESHOLD:
        return generate_specific_warnings(mvg_score)
    else:
        return approve_for_delivery(prep_guide)
```

#### **Warning Generation Logic**
- **Critical Failure**: < 50% of MVG criteria met → Block delivery
- **Quality Concerns**: 50-70% of MVG criteria met → Deliver with warnings
- **Acceptable Quality**: 70-85% of MVG criteria met → Minor advisory notes
- **High Quality**: > 85% of MVG criteria met → No warnings needed

### User Interface for MVG Warnings

#### **In Prep Guide Header**
```
📊 GUIDE QUALITY ASSESSMENT
✅ Meets minimum viable standards
⚠️  Some information limitations (see notes below)
❌ Critical information missing - additional research recommended

Last Research Attempt: [Timestamp]
Research Sources Attempted: [Count]
Reflection Loops Completed: 3/3
```

#### **Actionable Improvement Suggestions**
```
🎯 TO IMPROVE THIS GUIDE:
Priority 1 (Critical):
• Search "[Company Name] recent news 2024" manually
• Find [Interviewer Name] LinkedIn profile
• Verify interview logistics directly

Priority 2 (Enhancement):
• Research [Company Name] engineering blog
• Look up [Interviewer Name] recent posts/articles
• Find additional role-specific technical requirements

Priority 3 (Optional):
• Explore [Company Name] GitHub repositories
• Research team structure and dynamics
• Find company culture insights on Glassdoor
```

This MVG framework ensures that users receive either high-quality, research-backed prep guides or clear guidance on what additional research they need to conduct themselves. It prevents the delivery of inadequate guides while providing constructive paths forward when information is limited.

## Required Prep Guide Structure

### 📄 **Section 1: Summary Overview**
**Purpose**: Provide quick reference information for interview logistics

Required Fields:
- Candidate Name (if available)
- Target Role (e.g., "Senior Backend Engineer")
- Company Name
- Interview Date & Time (with timezone)
- Interviewer Name(s) and titles
- Interview Format (virtual/in-person)
- Location/Platform details

**Validation Check**: Ensure all logistical information is accurate and complete

### 🏢 **Section 2: Company Snapshot**
**Purpose**: Enable cultural alignment and informed conversation

Required Research Areas:
- **Mission & Values**: Core company purpose (2-3 sentences)
- **Recent News**: Last 6 months of significant developments [Citations required]
- **Tech Stack**: Primary technologies from job postings/engineering blogs [Citations required]
- **Market Position**: Key competitors and differentiation [Citations required]
- **Culture Indicators**: Work environment, values, team dynamics [Citations required]
- **"Why This Company" Talking Points**: 3-5 specific reasons beyond generic statements

**Citation Requirements**: 
- Link to company blog posts, press releases, or news articles
- Include publication dates
- Verify information is current (within 12 months)

### 👔 **Section 3: Role Deep Dive**
**Purpose**: Demonstrate precise understanding of position requirements

Required Analysis:
- **Job Description Synthesis**: Key responsibilities condensed into 3-5 bullet points
- **Technical Requirements**: Must-have skills with proficiency levels
- **Preferred Qualifications**: Nice-to-have skills and experiences
- **Team Context**: How role fits within broader team structure [Citations required]
- **Growth Trajectory**: Potential career progression paths
- **Success Metrics**: How performance will likely be measured
- **Challenge Areas**: Anticipated difficulties or complex aspects of role

**Validation**: Cross-reference multiple job postings for same role to identify patterns

### 👩‍💻 **Section 4: Interviewer Intelligence**
**Purpose**: Build rapport and personalize interactions

Required Research per Interviewer:
- **Basic Info**: Name, current title, tenure at company
- **Professional Background**: Previous roles, education, career progression [Citations required]
- **Public Presence**: LinkedIn URL, GitHub, Twitter, blog posts [Links required]
- **Expertise Areas**: Technical specializations and interests
- **Recent Activities**: Latest posts, projects, or publications (last 6 months)
- **Connection Points**: Shared experiences, interests, or background elements
- **Personalized Questions**: 2-3 tailored questions about their work/team

**Citation Format**: Direct links to social profiles and recent content

### ❓ **Section 5: Strategic Questions to Ask**
**Purpose**: Demonstrate thoughtful preparation and genuine interest

Question Categories (3-4 questions each):
- **For the Interviewer**: About their role, challenges, and experiences
- **Team Dynamics**: Workflow, collaboration, and culture
- **Company/Product Direction**: Strategic initiatives and future plans
- **Role-Specific**: Day-to-day responsibilities and success factors
- **Career Development**: Growth opportunities and learning paths
- **Technical Environment**: Tools, processes, and methodologies

**Quality Standards**: 
- Avoid questions easily answered by company website
- Include follow-up question suggestions
- Reference specific company initiatives or recent news

### 📚 **Section 6: Technical Preparation Checklist**
**Purpose**: Target likely technical assessments and discussions

Required Elements:
- **Likely Interview Topics**: Based on role and company (DSA, system design, etc.)
- **Sample Questions**: 3-5 representative questions with difficulty levels
- **Recommended Study Resources**: Specific links to prep materials
- **Company Tech Stack Deep Dive**: Technologies to research and understand
- **GitHub Repositories**: Relevant codebases to review (if public)
- **Technical Discussion Topics**: Industry trends relevant to company

**Resource Requirements**: All links must be active and relevant

### 🧠 **Section 7: Strategic Framing & Story Preparation**
**Purpose**: Help candidate present their best narrative

Framework Components:
- **STAR Technique Reminders**: Situation, Task, Action, Result structure
- **Key Stories to Prepare**: 
  - Technical challenge overcome
  - Leadership/collaboration example
  - Learning/growth experience
  - Failure and recovery story
- **Value Proposition**: Why you're uniquely qualified (3-4 key points)
- **Career Motivation**: What you're seeking in next role
- **Company Fit Narrative**: Why this specific company appeals to you

### 📋 **Section 8: Interview Execution Plan**
**Purpose**: Provide timeline-based preparation and execution strategy

Timeline Structure:
- **1 Week Before**: Research completion checklist
- **24 Hours Before**: Final review and preparation tasks
- **2 Hours Before**: Technical setup and environment preparation
- **30 Minutes Before**: Final mental preparation and logistics check
- **During Interview**: Key reminders and focus areas
- **Post-Interview**: Follow-up actions and next steps

**Risk Mitigation**:
- Technical backup plans
- Topics/questions to avoid
- Communication style guidelines
- Red flags and how to address them

## Citation and Validation System

### Citation Requirements
1. **Format**: [Source Title - Publication Date](actual-link)
2. **Placement**: At the end of each claim requiring validation
3. **Quality**: Primary sources preferred (company websites, official announcements)
4. **Recency**: Information should be within 12 months unless historical context needed
5. **Accessibility**: All links must be publicly accessible

### Example Citation Format:
"Company X recently launched their new AI platform focusing on ethical machine learning [Company X Blog - Machine Learning Ethics Initiative - March 2024](https://companyx.com/blog/ml-ethics-march-2024)"

## Reflection and Validation Loops

### Three-Stage Reflection Process

#### **Reflection 1: Content Completeness**
**Trigger**: After initial research and guide generation
**Focus Areas**:
- Are all 8 sections fully populated?
- Is critical information missing from any section?
- Do citations support all factual claims?
- Are questions specific and valuable?

**Action Items**:
- Identify information gaps
- Flag sections needing additional research
- Verify citation accuracy and accessibility
- Enhance generic content with specific details

#### **Reflection 2: Personalization and Relevance**
**Trigger**: After content completeness validation
**Focus Areas**:
- Does content reflect specific company culture and values?
- Are interviewer insights meaningful and actionable?
- Do technical preparations align with actual role requirements?
- Is the strategic framing compelling and authentic?

**Action Items**:
- Deepen company-specific research
- Enhance interviewer intelligence with recent activities
- Align technical prep with job requirements
- Strengthen narrative and value proposition

#### **Reflection 3: Actionability and Practicality**
**Trigger**: After personalization enhancements
**Focus Areas**:
- Can the candidate realistically execute the preparation plan?
- Are timeline recommendations practical and achievable?
- Do questions demonstrate genuine research and interest?
- Is the guide comprehensive without being overwhelming?

**Action Items**:
- Streamline overwhelming sections
- Prioritize most impactful preparation activities
- Ensure all recommendations are specific and actionable
- Final quality assurance on all citations and links

### Validation Checkpoints
- [ ] All sections contain substantive, specific content
- [ ] Every factual claim includes proper citation with working link
- [ ] Interviewer research includes recent (last 6 months) activities
- [ ] Technical preparation aligns with actual job requirements
- [ ] Questions demonstrate deep company research
- [ ] Timeline is realistic and actionable
- [ ] Content is personalized beyond generic advice
- [ ] All links and citations are accessible and current

## Quality Metrics

### Content Depth Score
- **Excellent (9-10)**: Rich, specific details with comprehensive citations
- **Good (7-8)**: Solid research with most areas well-covered
- **Adequate (5-6)**: Basic information present but lacking depth
- **Poor (1-4)**: Generic content with minimal research

### Personalization Score
- **Excellent (9-10)**: Highly tailored to specific company, role, and interviewer
- **Good (7-8)**: Good customization with some generic elements
- **Adequate (5-6)**: Basic customization attempt
- **Poor (1-4)**: Mostly generic template content

### Citation Quality Score
- **Excellent (9-10)**: All claims cited with high-quality, recent sources
- **Good (7-8)**: Most claims cited with good sources
- **Adequate (5-6)**: Some citations present but incomplete
- **Poor (1-4)**: Few or no citations, or low-quality sources

## Implementation Notes

### For AI Generation
1. Always trigger reflection loops when information gaps are detected
2. Prioritize recent, specific information over generic industry knowledge
3. Use company engineering blogs, recent press releases, and interviewer social media for insights
4. Validate all generated links before inclusion
5. Ensure each section provides genuine value beyond basic research

### For Quality Assurance
1. Test all citation links for accessibility
2. Verify interview logistics accuracy
3. Check that technical preparation matches actual job requirements
4. Ensure questions couldn't be answered by a simple website visit
5. Confirm timeline recommendations are realistic

This framework ensures every interview prep guide is research-backed, highly personalized, and immediately actionable for the candidate's success.
