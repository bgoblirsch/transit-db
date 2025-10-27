# database.py
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()   # reads .env at project root

# Unbound session factory
Session = sessionmaker()

def get_engine(username: str = None, password: str = None):
    """Create a SQLAlchemy engine."""
    if username is None:
        username = os.getenv("DB_USER")
    if password is None:
        password = os.getenv("DB_PASS")
    url = f"mysql+pymysql://{username}:{password}@localhost/transitDB"
    return create_engine(url, echo=True)

def configure_engine(engine=None, username=None, password=None):
    """
    Bind the session factory to an engine.
    If engine is provided, use it. Otherwise, create from username/password.
    """
    if engine is None:
        engine = get_engine(username, password)
    Session.configure(bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
