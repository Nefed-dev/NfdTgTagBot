from sqlalchemy import (
    Column,
    String,
    Integer, ForeignKey
)

from loader import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_tag = Column(String, unique=True)


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, )
    chat_id = Column(String, unique=True)


class Zoom(Base):
    __tablename__ = "zoom"

    id = Column(Integer, primary_key=True)
    zoom = Column(String(255), unique=True)


class ZoomChat(Base):
    __tablename__ = "chatzoom"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey(Chat.id))
    zoom_id = Column(Integer, ForeignKey(Zoom.id))


class UserGroupChat(Base):
    __tablename__ = "usergroupchat"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    chat_id = Column(Integer, ForeignKey(Chat.id))
    group = Column(String(10), default='nogroup')
