from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, func
from sqlalchemy.orm import relationship, declarative_base
from backend.db import Base
import datetime

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key = True, index = True)
  name = Column(String, nullable=False)
  email = Column(String, unique = True, index = True)
  created_at = Column(DateTime, default = datetime.datetime.utcnow)
  password_hash = Column(String, nullable = False)

  resumes = relationship("Resume", back_populates = "owner")
  analyses = relationship("Analysis", back_populates="owner")

class Resume(Base):
  __tablename__ = "resumes"

  id = Column(Integer, primary_key = True, index = True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
  text = Column(Text)
  created_at = Column(DateTime(timezone=True), server_default=func.now())

  owner = relationship("User", back_populates = "resumes")
  analyses = relationship("Analysis", back_populates="resume")


class Analysis(Base):
  __tablename__ = "analyses"

  id = Column(Integer, primary_key = True, index = True)

  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
  resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

  jd_text = Column(Text, nullable=False)

  result = Column(JSON, nullable=False)

  created_at = Column(DateTime(timezone=True), server_default=func.now())

  owner = relationship("User", back_populates = "analyses")
  resume = relationship("Resume", back_populates = "analyses")






