import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError, InvalidRequestError

Base = declarative_base()

db = 'postgresql://postgres:789@localhost:5432/vkinder' #убрать названия в отдельный файл
engine = sq.create_engine(db)
Session = sessionmaker(bind=engine)
session = Session()


class VkDb(Base):

    def __init__(self, user_id):
        self.user_id = user_id
    __tablename__ = user_id




    founded_user_link = sq.Column(sq.Integer, primary_key=True)

user = VkDb(1136869)
Base.metadata.create_all(engine)
