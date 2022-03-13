import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from keys import db_name, db_login, db_password

Base = declarative_base()

db = f'postgresql://{db_login}:{db_password}@localhost:5432/{db_name}'
engine = sq.create_engine(db)
Session = sessionmaker(bind=engine)
session = Session()


class Users(Base):
    __tablename__ = 'search_result'
    founded_user_link = sq.Column(sq.Integer, primary_key=True)


class Favorites(Base):
    __tablename__ = 'favorites'
    user_id = sq.Column(sq.Integer, primary_key=True)
    favorite_id = sq.Column(sq.Integer, primary_key=True)
    photos_list = sq.Column(sq.Text)


class BlackList(Base):
    __tablename__ = 'black_list'
    user_id = sq.Column(sq.Integer, primary_key=True)
    blacklisted_user_id = sq.Column(sq.Integer, primary_key=True)


def create_tables(db_table):
    try:
        db_table.__table__.drop(engine)
        Base.metadata.create_all(engine)
    except:
        Base.metadata.create_all(engine)
    session.commit()


def lines_count(db_table):
    count = session.query(db_table).all()
    return len(count)


def add_user_to_db(user_id):
    user = Users(founded_user_link=user_id)
    try:
        session.add(user)
        session.commit()
        return True
    except (IntegrityError, InvalidRequestError):
        return False


def find_user_in_db(table_name, user_id):
    request = session.query(table_name).where(table_name.founded_user_link == f'{user_id}').first()
    return bool(request)


def find_in_favorites(favorite_id):
    request = session.query(Favorites).where(Favorites.favorite_id == f'{favorite_id}').first()
    return bool(request)


def add_to_favorites(user_id, favorite_id, photos_list):
    if not find_in_favorites(favorite_id):
        user = Favorites(user_id=str(user_id), favorite_id=str(favorite_id), photos_list=photos_list)
        session.add(user)
        session.commit()
        return True
    else:
        return False


def find_in_blacklisted(blacklisted_id):
    request = session.query(BlackList).where(BlackList.blacklisted_user_id == f'{blacklisted_id}').first()
    return bool(request)


def add_to_blacklist(user_id, blacklisted_user_id):
    if not find_in_blacklisted(blacklisted_user_id):
        user = BlackList(user_id=user_id, blacklisted_user_id=blacklisted_user_id)
        session.add(user)
        session.commit()
        return True
    else:
        return False
