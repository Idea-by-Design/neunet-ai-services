from sqlalchemy.orm import sessionmaker
from .db_setup import Resume, Education, WorkExperience, setup_database

def save_or_update_resume(engine, resume_data):
    Session = sessionmaker(bind=engine)
    session = Session()

    existing_resume = session.query(Resume).filter_by(email=resume_data['email']).first()
    if existing_resume:
        for key, value in resume_data.items():
            if key in ['education', 'work_experience']:
                continue
            setattr(existing_resume, key, value)
        session.commit()
    else:
        new_resume = Resume(
            email=resume_data['email'],
            name=resume_data.get('name'),
            phone=resume_data.get('phone'),
            linkedin=resume_data.get('linkedin')
        )
        session.add(new_resume)
        session.flush()
        
        for education in resume_data.get('education', []):
            new_education = Education(resume_id=new_resume.id, **education)
            session.add(new_education)
        
        for work in resume_data.get('work_experience', []):
            new_work = WorkExperience(resume_id=new_resume.id, **work)
            session.add(new_work)
        
        session.commit()
    
    session.close()
