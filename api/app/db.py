from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.DATABASE_URL)

# Each request to db create a new session that is used by ORM to interact with db
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# Closing connections to avoid db connection leaks
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()
        
def ping_db():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()
        
