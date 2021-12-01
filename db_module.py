from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)


class ImageMessage(Base):
    __tablename__ = "image_message"
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey(User.user_id))
    img_path = Column(String)


class AudioMessage(Base):
    __tablename__ = "audio_message"
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey(User.user_id))
    audio_path = Column(String)
