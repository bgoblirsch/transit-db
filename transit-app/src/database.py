import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()   # reads .env at project root

def get_engine(username: str, password: str):
    url = f"mysql+pymysql://{username}:{password}@localhost/transitDB"
    return create_engine(url, echo=True)

SessionLocal = sessionmaker(bind=get_engine(os.getenv("DB_USER"), os.getenv("DB_PASS")))
