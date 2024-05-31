import re

def extract_information(text):
    # Simplistic regex-based extraction for example purposes
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\b\d{10}\b|\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}'
    linkedin_pattern = r'(https?://www\.linkedin\.com/in/[A-z0-9_-]+)'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    linkedin_profiles = re.findall(linkedin_pattern, text)
    
    education_pattern = r'(Bachelor|Master|PhD|Associate)\s*of\s*[A-Za-z\s]+'
    work_pattern = r'(Internship|Intern|Work Experience|Job|Position|Title):\s*[A-Za-z\s]+'
    
    education_entries = re.findall(education_pattern, text)
    work_entries = re.findall(work_pattern, text)
    
    return {
        'email': emails[0] if emails else None,
        'phone': phones[0] if phones else None,
        'linkedin': linkedin_profiles[0] if linkedin_profiles else None,
        'education': [{'degree': edu} for edu in education_entries],
        'work_experience': [{'job_title': work} for work in work_entries]
    }
