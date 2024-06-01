from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    phone = Column(String)
    linkedin = Column(String)

class Education(Base):
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    degree = Column(String)
    institution = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    resume = relationship("Resume", back_populates="education")

class WorkExperience(Base):
    __tablename__ = 'work_experience'
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    job_title = Column(String)
    company = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    description = Column(String)
    resume = relationship("Resume", back_populates="work_experience")

Resume.education = relationship("Education", order_by=Education.id, back_populates="resume")
Resume.work_experience = relationship("WorkExperience", order_by=WorkExperience.id, back_populates="resume")

def setup_database(connection_string):
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    return engine
