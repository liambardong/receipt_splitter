import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from logging import Logger

logger = Logger(__name__)
ENV = os.getenv("ENV", "development")


def generate_uuid():
    return str(uuid.uuid4())

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./receipt_splitter.db")
connect_args = {}
if ENV == "development":
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
if "sqlite" in SQLALCHEMY_DATABASE_URL.lower():
    logger.debug("Using SQLite")
else:
    logger.debug("Using PostgreSQL")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
