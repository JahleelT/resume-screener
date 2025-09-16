from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from backend.db import Base
import datetime

Base = declarative_base()

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key = True, index = True)
  email = Column(String, unique = True, index = True)
  created_at = Column(DateTime, default = datetime.datetime.utcnow)
  password_hash = Column(String, nullable = False)

  resumes = relationship("Resume", back_populates = "owner")

class Resume(Base):
  __tablename = "resumes"

  id = Column(Integer, primary_key = True, index = True)
  user_id = Column(Integer, ForeignKey("users.id"))
  text = Column(Text)
  created_at = Column(DateTime, default = datetime.datetime.utcnow)

  owner = relationship("User", back_populates = "resumes")