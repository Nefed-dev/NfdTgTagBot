from sqlalchemy import (
    Table,
    Column,
    String,
    Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from uuid import uuid4

user = 'postgres'
password = 'zzz'
host = '127.0.0.1'
port = 5432
database_name = 'test'
pg_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database_name}"

DATABASE_URL = pg_url
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)

base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_tag = Column(String, unique=True)


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, )
    chat_id = Column(String, unique=True)


class UserGroupChat(Base):
    __tablename__ = "usergroupchat"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    chat_id = Column(Integer, ForeignKey(Chat.id))
    group = Column(String(10), default='nogroup')
