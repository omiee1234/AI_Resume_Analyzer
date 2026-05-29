"""
controllers/ai_service.py
─────────────────────────
All AI business logic using Ollama (llama3).
"""

import json

import streamlit as st
from groq import Groq
from config.settings import API

# ── Ollama config ────────────────────────────────────────────────────────────
client = Groq(api_key=API)

MODEL_NAME = "llama-3.3-70b-versatile"

_SYSTEM_PROMPT = """
You are an elite ATS (Applicant Tracking System) Resume Analyzer, 
Resume Optimizer, and Senior HR Specialist with 15+ years of experience 
in technical recruitment at top companies like Google, Amazon, and Microsoft.

Your job is to:
- Deeply analyze resumes for ATS compatibility
- Assess whether a person is a good fit for an AI-enabled role for a specific job role and company
- Identify gaps, weaknesses, and missing keywords
- Provide actionable, specific improvement suggestions
- Generate professional, job-winning resume content
- Score resumes fairly and consistently based on actual content quality

You always respond with structured, well-formatted JSON. 
You never add commentary outside the JSON. 
You never hallucinate skills or experience not present in the resume.
"""


# ── Low-level Ollama call ────────────────────────────────────────────────────
def ask_ai(prompt: str) -> str:
    """Send prompt to Groq Llama 3.3 70B and return response."""

    try:
        with st.spinner("🤖 Llama 3.3 70B is analyzing your resume..."):

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": _SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
            )

            text = response.choices[0].message.content

            if not text:
                st.error("❌ Empty response from Groq.")
                return "AI response generation failed."

            st.success("✅ Analysis complete!")

            return text

    except Exception as exc:
        st.error(f"❌ Groq API Error: {exc}")
        return "AI response generation failed."


# ── Comprehensive Resume Analysis (SINGLE API CALL) ──────────────────────────

def comprehensive_analysis(resume_text: str, hr_question: str = None) -> str:
    """
    Single API call that returns ALL analysis data at once:
    - General ATS analysis
    - AI Enablement check
    - HR Chatbot ready data
    """
    hr_query_json    = json.dumps(hr_question) if hr_question else "null"
    hr_question_json = json.dumps(hr_question) if hr_question else '""'

    prompt = f"""
Analyze this resume comprehensively and return ONE complete JSON object with ALL analysis data.
No extra text. No markdown. No code fences. Start with {{ end with }}.

ATS Scoring Rules:
  - Beginner / minimal content  : 40–60
  - Average fresher             : 60–72
  - Good fresher                : 72–82
  - Strong / experienced        : 82–92
  - Exceptional                 : 92–98

Return EXACTLY this JSON structure (all keys required):

{{
  "ats_score": <integer 0-100>,
  
  "quick_resume_snapshot": {{
    "candidate_name": "<name from resume or 'Not Found'>",
    "current_role": "<current or target role>",
    "total_experience": "<e.g. Fresher / 2 years / 5+ years>",
    "education": "<highest degree and college>",
    "top_tech_skills": ["<skill1>", "<skill2>", "<skill3>"],
    "resume_strength": "<one-line verdict>"
  }},
  
  "top_strengths": [
    "<specific strength 1>",
    "<specific strength 2>",
    "<specific strength 3>"
  ],
  
  "weaknesses": [
    "<specific weakness 1>",
    "<specific weakness 2>",
    "<specific weakness 3>"
  ],
  
  "missing_skills": [
    "<skill 1>",
    "<skill 2>",
    "<skill 3>"
  ],
  
  "important_ats_keywords_missing": [
    "<keyword 1>",
    "<keyword 2>",
    "<keyword 3>",
    "<keyword 4>",
    "<keyword 5>"
  ],
  
  "improvement_suggestions": [
    "<actionable suggestion 1>",
    "<actionable suggestion 2>",
    "<actionable suggestion 3>",
    "<actionable suggestion 4>"
  ],
  
  "improved_professional_summary": "<Write a powerful 3-4 sentence ATS-optimized professional summary>",
  
  "ai_enablement": {{
    "ai_enablement_score": <integer 0-100>,
    "ai_enablement_status": "<HIGHLY AI-ENABLED | AI-ENABLED | MODERATELY AI-ENABLED | LIMITED AI-SKILLS | NO AI-EXPERIENCE>",
    "ai_related_skills": [
      "<AI/ML skill 1 e.g. TensorFlow, PyTorch, Machine Learning>",
      "<skill 2>",
      "<skill 3>",
      "<skill 4>"
    ],
    "ai_tools_and_frameworks": [
      "<tool/framework 1 e.g. Scikit-learn, OpenCV>",
      "<tool 2>",
      "<tool 3>"
    ],
    "ai_related_projects": [
      {{
        "project_name": "<Project Name>",
        "ai_technologies": "<technologies used>",
        "description": "<what AI/ML work was done>",
        "outcome": "<quantifiable result if available>"
      }}
    ],
    "ai_experience_summary": "<paragraph describing overall AI/ML experience>",
    "ai_readiness": "<1-2 sentences assessing AI role readiness>",
    "recommended_ai_roles": [
      "<Recommended role 1 e.g. ML Engineer>",
      "<role 2>",
      "<role 3>"
    ],
    "gaps_for_ai_roles": [
      "<AI skill gap 1>",
      "<gap 2>",
      "<gap 3>"
    ]
  }},
  
  "hr_suitability": {{
    "candidate_fit_summary": "<General assessment of candidate quality and fit for typical roles - 2 sentences>",
    "key_hiring_points": [
      "<key point 1 from resume>",
      "<key point 2>",
      "<key point 3>"
    ],
    "hiring_concerns": [
      "<concern 1 if any>",
      "<concern 2 if any>"
    ]
  }},
  
  "hr_query": {hr_query_json},
  
  "hr_answer": {{
    "question": {hr_question_json},
    "answer": "<comprehensive answer addressing the question - 2-3 sentences. If no HR question is provided, return an empty string.>",
    "suitability_verdict": "<HIGHLY SUITABLE | SUITABLE | MODERATELY SUITABLE | NOT SUITABLE>",
    "key_points": [
      "<key point 1 from resume supporting this>",
      "<key point 2>",
      "<key point 3>"
    ],
    "concerns": [
      "<concern 1 if any>"
    ],
    "recommendation": "<actionable recommendation for the HR team>"
  }}
}}

Resume:
{resume_text}
"""
    return ask_ai(prompt)


# ── General Resume Analysis ──────────────────────────────────────────────────

def general_analysis(resume_text: str) -> str:
    return comprehensive_analysis(resume_text)


# ── AI Enablement Check ──────────────────────────────────────────────────────

def ai_enablement_check(resume_text: str) -> str:
    return comprehensive_analysis(resume_text)


# ── HR Chatbot for Candidate Suitability ────────────────────────────────────

def hr_chatbot_query(resume_text: str, hr_question: str) -> str:
    return comprehensive_analysis(resume_text, hr_question=hr_question)


# ── Generate Improved Resume ─────────────────────────────────────────────────

def generate_improved_resume(original_resume: str, analysis: str) -> str:
    prompt = f"""
You are a world-class ATS Resume Writer.
Using the original resume and the analysis provided, write a complete, 
fully ATS-optimized, recruiter-ready resume.

Return ONLY a valid JSON object. No extra text. No markdown. No code fences.
Start with {{ end with }}.

Return exactly this JSON structure:

{{
  "final_resume": {{

    "name"    : "<candidate full name>",
    "title"   : "<professional title e.g. 'Full Stack Developer | Python | React'>",
    "contact" : {{
      "email"    : "<email or 'Not provided'>",
      "phone"    : "<phone or 'Not provided'>",
      "linkedin" : "<linkedin url or 'Not provided'>",
      "github"   : "<github url or 'Not provided'>",
      "location" : "<city, country or 'Not provided'>"
    }},

    "objective": "<Write a powerful 4-5 sentence ATS-optimized career objective. Include role, key skills, top achievements, and what value the candidate brings. Use action words and quantify where possible.>",

    "technical_skills": {{
      "languages"           : ["<lang1>", "<lang2>", "<lang3>"],
      "frameworks_libraries": ["<fw1>", "<fw2>", "<fw3>"],
      "databases"           : ["<db1>", "<db2>"],
      "concepts"            : ["<concept1>", "<concept2>", "<concept3>"]
    }},

    "tools_and_platforms": ["<tool1>", "<tool2>", "<tool3>", "<tool4>", "<tool5>"],

    "projects": [
      {{
        "name"       : "<Project Name>",
        "tech_stack" : "<comma-separated technologies used>",
        "description": "<2-3 sentence description with action verbs and impact. Quantify results where possible e.g. 'Reduced load time by 40%'>",
        "highlights" : ["<key achievement 1>", "<key achievement 2>"]
      }},
      {{
        "name"       : "<Project 2 Name>",
        "tech_stack" : "<tech stack>",
        "description": "<description>",
        "highlights" : ["<achievement 1>", "<achievement 2>"]
      }}
    ],

    "experience": [
      {{
        "role"        : "<Job Title>",
        "company"     : "<Company Name>",
        "duration"    : "<Start Month Year – End Month Year or Present>",
        "location"    : "<City or Remote>",
        "achievements": [
          "<Achievement with action verb and metric e.g. 'Increased API performance by 30% by implementing caching'>",
          "<Achievement 2>",
          "<Achievement 3>"
        ]
      }}
    ],

    "education": [
      {{
        "degree"     : "<Degree Name>",
        "institution": "<College / University Name>",
        "year"       : "<Graduation Year or Expected Year>",
        "score"      : "<CGPA / Percentage or 'Not mentioned'>"
      }}
    ],

    "certifications": [
      "<Certification 1 — Issuer — Year>",
      "<Certification 2 — Issuer — Year>"
    ],

    "achievements": [
      "<Notable achievement or award 1>",
      "<Notable achievement 2>"
    ]
  }}
}}

Original Resume:
{original_resume}

Analysis:
{analysis}
"""
    return ask_ai(prompt)