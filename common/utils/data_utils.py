''' 

This is old approch, this script/file can be deleted as it is not used anymore.

'''

import spacy
import re

nlp = spacy.load("en_core_web_sm")

def extract_information(text):
    doc = nlp(text)
    resume_data = {
        "name": None,
        "email": None,
        "secondary_email": None,
        "phone_number": None,
        "secondary_phone_number": None,
        "links": {
            "linkedin": None,
            "github": None,
            "website": None,
            "other": []
        },
        "skills": [],
        "education": [],
        "work_experience": [],
        "co_curricular": [],
        "publications": [],
        "achievements": []
    }

    print("##############################\n",doc,"\n##############################\n")
    print("##############################\n",doc.ents,"\n##############################\n")

    # Add custom extraction rules here
    for entity in doc.ents:
        if entity.label_ == "PERSON" and resume_data["name"] is None:
            resume_data["name"] = entity.text
        elif entity.label_ == "EMAIL":
            if resume_data["email"] is None:
                resume_data["email"] = entity.text
            else:
                resume_data["secondary_email"] = entity.text
        elif entity.label_ == "PHONE":
            if resume_data["phone_number"] is None:
                resume_data["phone_number"] = entity.text
            else:
                resume_data["secondary_phone_number"] = entity.text
    
    # Regex based extraction for specific patterns like URLs, skills, etc.
    resume_data["links"]["linkedin"] = extract_linkedin(text)
    resume_data["links"]["github"] = extract_github(text)
    resume_data["links"]["website"] = extract_website(text)
    resume_data["links"]["other"] = extract_other_links(text)
    resume_data["skills"] = extract_skills(text)
    resume_data["education"] = extract_education(text)
    resume_data["work_experience"] = extract_work_experience(text)
    resume_data["co_curricular"] = extract_co_curricular(text)
    resume_data["publications"] = extract_publications(text)
    resume_data["achievements"] = extract_achievements(text)

    return resume_data

def extract_linkedin(text):
    match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", text)
    return match.group(0) if match else None

def extract_github(text):
    match = re.search(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9_-]+", text)
    return match.group(0) if match else None

def extract_website(text):
    match = re.search(r"(https?://)?(www\.)?[A-Za-z0-9-]+(\.[A-Za-z]{2,})+", text)
    return match.group(0) if match else None

def extract_other_links(text):
    matches = re.findall(r"(https?://)?(www\.)?[A-Za-z0-9-]+(\.[A-Za-z]{2,})+", text)
    other_links = [match[0] for match in matches if "linkedin.com" not in match[0] and "github.com" not in match[0]]
    return other_links

def extract_skills(text):
    # Assuming skills are listed under a section labeled "Skills" or similar
    match = re.search(r"Skills\s*:\s*(.*)", text, re.IGNORECASE)
    return match.group(1).split(',') if match else []

def extract_education(text):
    # Assuming education sections are labeled "Education" or similar
    edu_sections = re.findall(r"Education\s*:\s*(.*?)\s*(?=(Education|Work Experience|Experience|$))", text, re.IGNORECASE | re.DOTALL)
    education_list = []
    for section in edu_sections:
        edu = {}
        edu["institute"] = re.search(r"Institution\s*:\s*(.*)", section[0]).group(1) if re.search(r"Institution\s*:\s*(.*)", section[0]) else None
        edu["degree"] = re.search(r"Degree\s*:\s*(.*)", section[0]).group(1) if re.search(r"Degree\s*:\s*(.*)", section[0]) else None
        edu["major"] = re.search(r"Major\s*:\s*(.*)", section[0]).group(1) if re.search(r"Major\s*:\s*(.*)", section[0]) else None
        edu["minor"] = re.search(r"Minor\s*:\s*(.*)", section[0]).group(1) if re.search(r"Minor\s*:\s*(.*)", section[0]) else None
        edu["start_date"] = re.search(r"Start Date\s*:\s*(.*)", section[0]).group(1) if re.search(r"Start Date\s*:\s*(.*)", section[0]) else None
        edu["end_date"] = re.search(r"End Date\s*:\s*(.*)", section[0]).group(1) if re.search(r"End Date\s*:\s*(.*)", section[0]) else None
        education_list.append(edu)
    return education_list

def extract_work_experience(text):
    # Assuming work experience sections are labeled "Work Experience", "Experience", or "Internships"
    exp_sections = re.findall(r"(Work Experience|Experience|Internships)\s*:\s*(.*?)\s*(?=(Work Experience|Experience|Internships|$))", text, re.IGNORECASE | re.DOTALL)
    experience_list = []
    for section in exp_sections:
        exp = {}
        exp["organization"] = re.search(r"Organization\s*:\s*(.*)", section[1]).group(1) if re.search(r"Organization\s*:\s*(.*)", section[1]) else None
        exp["position"] = re.search(r"Position\s*:\s*(.*)", section[1]).group(1) if re.search(r"Position\s*:\s*(.*)", section[1]) else None
        exp["role_description"] = re.search(r"Role Description\s*:\s*(.*)", section[1]).group(1) if re.search(r"Role Description\s*:\s*(.*)", section[1]) else None
        exp["start_date"] = re.search(r"Start Date\s*:\s*(.*)", section[1]).group(1) if re.search(r"Start Date\s*:\s*(.*)", section[1]) else None
        exp["end_date"] = re.search(r"End Date\s*:\s*(.*)", section[1]).group(1) if re.search(r"End Date\s*:\s*(.*)", section[1]) else None
        experience_list.append(exp)
    return experience_list

def extract_co_curricular(text):
    # Assuming co-curricular activities are listed under a section labeled "Co-Curricular Activities" or similar
    match = re.search(r"Co-Curricular Activities\s*:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
    return match.group(1).split(',') if match else []

def extract_publications(text):
    # Assuming publications are listed under a section labeled "Publications" or similar
    pub_sections = re.findall(r"Publications\s*:\s*(.*?)\s*(?=(Publications|$))", text, re.IGNORECASE | re.DOTALL)
    publications_list = []
    for section in pub_sections:
        pub = {}
        pub["title"] = re.search(r"Title\s*:\s*(.*)", section[0]).group(1) if re.search(r"Title\s*:\s*(.*)", section[0]) else None
        pub["link"] = re.search(r"Link\s*:\s*(.*)", section[0]).group(1) if re.search(r"Link\s*:\s*(.*)", section[0]) else None
        pub["description"] = re.search(r"Description\s*:\s*(.*)", section[0]).group(1) if re.search(r"Description\s*:\s*(.*)", section[0]) else None
        publications_list.append(pub)
    return publications_list

def extract_achievements(text):
    # Assuming achievements are listed under a section labeled "Achievements" or similar
    match = re.search(r"Achievements\s*:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
    return match.group(1).split(',') if match else []
