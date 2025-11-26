import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Postgres-only default (matches docker-compose)
DB_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://sentrascan:changeme@db:5432/sentrascan")
# Increase pool size for concurrent test execution and production load
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    pool_size=10,  # Increased from default 5
    max_overflow=20,  # Increased from default 10
    pool_recycle=3600,  # Recycle connections after 1 hour
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    from sentrascan.core import models  # noqa
    Base.metadata.create_all(bind=engine)
