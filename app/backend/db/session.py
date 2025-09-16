from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://username:password@localhost/resumescreener"

engine = create_engine(DATABASE_URL, echo = True)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)