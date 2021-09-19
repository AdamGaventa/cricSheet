"""
Testing sqlalchemy with dummy db
"""
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class TestUser(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String)


engine = create_engine("sqlite:///Data/sqlite/dummy.db", echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

session = Session()

user = TestUser()
user.id = 0
user.username = "JoeBloggs"

session.add(user)
session.commit()


session.close()
