import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Postgres-only default (matches docker-compose)
DB_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://sentrascan:changeme@db:5432/sentrascan")
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    from sentrascan.core import models  # noqa
    Base.metadata.create_all(bind=engine)
