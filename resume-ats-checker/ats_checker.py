# ats_checker.py
# Core ATS scoring logic

from keywords import JOB_KEYWORDS, GENERAL_KEYWORDS
import re

def clean_text(text):
    """Remove special characters and extra spaces"""
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def check_keywords(resume_text, keywords):
    """Check which keywords are found in resume"""
    found     = []
    not_found = []
    for kw in keywords:
        if kw.lower() in resume_text:
            found.append(kw)
        else:
            not_found.append(kw)
    return found, not_found

def calculate_score(found, total):
    total = len(total) if isinstance(total, list) else total
    if total == 0:
        return 0
    return round((len(found) / total) * 100)

def get_grade(score):
    """Return grade and message based on score"""
    if score >= 80:
        return "Excellent", "Your resume is highly optimized for ATS!"
    elif score >= 60:
        return "Good", "Your resume is decent but can be improved."
    elif score >= 40:
        return "Average", "Your resume needs more relevant keywords."
    else:
        return "Poor", "Your resume needs significant improvements."

def analyze_resume(resume_text, job_role):
    """Main function - analyzes resume against job role"""
    resume_text = clean_text(resume_text)

    # Get keywords for selected job role
    role_keywords    = JOB_KEYWORDS.get(job_role, [])
    general_keywords = GENERAL_KEYWORDS

    # Check role keywords
    role_found,    role_missing    = check_keywords(resume_text, role_keywords)
    general_found, general_missing = check_keywords(resume_text, general_keywords)

    # Calculate scores
    role_score    = calculate_score(role_found, role_keywords)
    general_score = calculate_score(general_found, general_keywords)

    # Overall score (80% role, 20% general)
    overall_score = round((role_score * 0.8) + (general_score * 0.2))
    grade, message = get_grade(overall_score)

    # Word count
    words = len(resume_text.split())

    # Suggestions
    suggestions = []
    if words < 300:
        suggestions.append("Your resume is too short. Add more details about your experience.")
    if words > 1000:
        suggestions.append("Your resume might be too long. Try to keep it concise.")
    if len(role_missing) > 5:
        suggestions.append(f"Add more {job_role} keywords to your resume.")
    if overall_score < 60:
        suggestions.append("Tailor your resume specifically for this job role.")
    if not suggestions:
        suggestions.append("Great job! Keep your resume updated with latest skills.")

    return {
        "overall_score":   overall_score,
        "role_score":      role_score,
        "general_score":   general_score,
        "grade":           grade,
        "message":         message,
        "role_found":      role_found,
        "role_missing":    role_missing[:10],  # top 10 missing
        "general_found":   general_found,
        "general_missing": general_missing,
        "suggestions":     suggestions,
        "word_count":      words,
        "job_role":        job_role,
    }