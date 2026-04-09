from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL="postgresql://admin:admin@localhost:5434/jobs"

engine = create_engine(DATABASE_URL)

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
        
