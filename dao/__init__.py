"""This file contains a different database objects to create db models and
provides connection to the database"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from constants import DB_URI
# --------------------------------------------------------------------------

engine = create_async_engine(DB_URI)

SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
