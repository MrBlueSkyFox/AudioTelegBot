from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_module import Base, User, ImageMessage, AudioMessage

engine = create_engine('sqlite:///dbase.db', echo=True, future=True)
connection = engine.connect()
session = sessionmaker(bind=engine)
Base.metadata.create_all(bind=connection.engine)
session = session()
user_id = "123232"
user = session.query(User).filter(User.user_id == user_id).first()
