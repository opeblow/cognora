from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=3600,
    pool_use_lifo=True,
    pool_timeout=30,
    connect_args={"connect_timeout": 10},
)

read_replica_engine = None
if settings.DATABASE_READ_REPLICA_URL:
    read_replica_engine = create_engine(
        settings.DATABASE_READ_REPLICA_URL,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE * 2,
        max_overflow=settings.DB_MAX_OVERFLOW * 2,
        pool_recycle=3600,
        pool_use_lifo=True,
        pool_timeout=30,
        connect_args={"connect_timeout": 10},
    )


@event.listens_for(engine, "connect")
def set_pragma(dbapi_connection, connection_record):
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ReadSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=read_replica_engine) if read_replica_engine else SessionLocal


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    db = ReadSessionLocal()
    try:
        yield db
    finally:
        db.close()
