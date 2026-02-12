import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

ENV = os.getenv("ENV", "development")


def generate_uuid():
    return str(uuid.uuid4())

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./receipt_splitter.db")
connect_args = {}
if ENV == "development":
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
