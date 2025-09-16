from db.session import SessionLocal
from db.models import Base

def get_db_session():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

def create_user(email: str, password_hash: str) -> User(Base):
  db = next(get_db_session())
  user = User(email = email, password_hash = str)
  db.add(user)
  db.commit()
  db.refresh(user)
  return user

def add_user_resume():
  return

