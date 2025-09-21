from sqlalchemy import desc, select
from sqlalchemy.orm import Session, SessionLocal
from db.models import User, Resume, Analysis

"""
Below are the User class CRUD methods
"""

def create_user(name: str, email: str, password_hash: str) -> User:
  db = SessionLocal()

  try:
    user = User(name = name, email = email, password_hash = password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
  except:
    db.rollback()
    raise
  finally:
    db.close()

def get_user_by_id(user_id: int):
  db = SessionLocal()

  try:
    result = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    return result
  finally:
    db.close()

def get_user_by_email(user_email: str):
  db = SessionLocal()

  try:
    result = db.execute(select(User).where(User.email == user_email)).scalar_one_or_none()
    return result
  finally:
    db.close()

def get_users(skip=0, limit=100):
  db = SessionLocal()

  try:
    result = db.execute(select(User).order_by(desc(User.created_at)).offset(skip).limit(limit)).scalars().all()
    return result
  finally:
    db.close()

def update_user(user_id: int, updates: dict):
  db = SessionLocal()

  try:
    user = db.get(User, user_id)
    if not user: 
      return None
    allowed_fields = {"name", "email"}
    for key, value in updates.items():
      if key in allowed_fields:
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
  except:
    db.rollback()
    raise
  finally:
    db.close()
  
def delete_user(user_id: int):
  db = SessionLocal()
  try:
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user:
      db.delete(user)
      db.commit()
      return True
    return False
  except:
    db.rollback()
    raise
  finally:
    db.close()

"""
Below are the Resume class CRUD methods
"""

def create_resume(resume: dict, user_id: int) -> Resume:
  db = SessionLocal()
  try:
    new_resume = Resume(
      text=resume["text"],
      user_id = user_id
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return new_resume
  except:
    db.rollback()
    raise
  finally:
    db.close()
  

def get_resume_by_id(resume_id: int):
  db = SessionLocal()
  try:
    result = db.execute(select(Resume).where(Resume.id == resume_id)).scalar_one_or_none()
    return result
  finally:
    db.close()

def get_resumes_by_user(user_id: int):
  db = SessionLocal()
  try:
    result = db.execute(select(Resume).where(Resume.user_id == user_id).order_by(desc(Resume.created_at))).scalars().all()
    return result
  finally:
    db.close()

def delete_resume(resume_id: int):
  db = SessionLocal()
  try:
    resume = db.get(Resume, resume_id)
    if resume:
      db.delete(resume)
      db.commit()
    return None
  except:
    db.rollback()
    raise
  finally:
    db.close()



"""
Below are the Analysis class CRUD methods
"""

def create_analysis(analysis_data: dict, resume_id: int, user_id: int) -> Analysis:
  db = SessionLocal()
  try:
    new_analysis = Analysis(
      user_id = user_id,
      resume_id = resume_id,
      jd_text = analysis_data["jd_text"],
      result = analysis_data["result"]
    )
    
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)
    return new_analysis
  except:
    db.rollback()
    raise
  finally:
    db.close()

def get_analysis_by_id(analysis_id: int):
  db = SessionLocal()

  try:
    result = db.execute(select(Analysis).where(Analysis.id == analysis_id)).scalar_one_or_none()
    return result
  finally:
    db.close()

def get_analyses_by_resume(resume_id: int):
  db = SessionLocal()

  try:
    results = db.execute(select(Analysis).where(Analysis.resume_id == resume_id)).scalars().all()
    return results
  finally:
    db.close()

def get_analyses_by_user(user_id: int):
  db = SessionLocal()
  try:
    results = db.execute(select(Analysis).where(Analysis.user_id == user_id).order_by(desc(Analysis.created_at))).scalars().all()
    return results
  finally:
    db.close()


def delete_analysis(analysis_id: int):
  db = SessionLocal()
  
  try:
    analysis = db.get(Analysis, analysis_id)
    if analysis:
      db.delete(analysis)
      db.commit()
      return True
    return False
  except:
    db.rollback()
    raise
  finally:
    db.close()

