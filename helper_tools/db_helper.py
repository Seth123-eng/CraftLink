
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

import os

from dotenv import load_dotenv

load_dotenv(override=True)

class Base(DeclarativeBase):
    pass

DATABASE_URI=os.getenv("DATABASE_URI", "").strip()

if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI.replace("postgres://", "postgresql+asyncpg://")


engine=create_async_engine(
    url=DATABASE_URI,
    echo=False
)


def make_session():
    sess = AsyncSession(
        engine,
        expire_on_commit=False,
        autoflush=True
    )
    
    return sess