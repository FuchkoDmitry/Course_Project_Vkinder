import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy import and_
import os

Base = declarative_base()
db_login = os.getenv('db_login')
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')


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
    photos_list = sq.Column(sq.Text)


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
    request = session.query(table_name).where(
        table_name.founded_user_link == f'{user_id}').first()
    return bool(request)


def find_in_favorites(favorite_id, user_id):
    request = session.query(Favorites).where(and_(Favorites.favorite_id == f'{favorite_id}',
                                                  Favorites.user_id == f'{user_id}')).first()
    return bool(request)


def add_to_favorites(user_id, favorite_id, photos_list):
    if not find_in_favorites(favorite_id, user_id):
        user = Favorites(user_id=str(user_id), favorite_id=str(favorite_id),
                         photos_list=photos_list)
        session.add(user)
        session.commit()
        return True
    else:
        return False


def find_in_blacklisted(blacklisted_id, user_id):
    request = session.query(BlackList).where(and_(
        BlackList.blacklisted_user_id == f'{blacklisted_id}',
        BlackList.user_id == f'{user_id}')).first()
    return bool(request)


def add_to_blacklist(user_id, blacklisted_user_id, photos_list):
    if not find_in_blacklisted(blacklisted_user_id, user_id):
        user = BlackList(user_id=user_id, blacklisted_user_id=blacklisted_user_id,
                         photos_list=photos_list)
        session.add(user)
        session.commit()
        return True
    else:
        return False


def get_users_in_table(table_name, user_id):
    user_list = session.query(table_name).where(table_name.user_id == user_id).all()
    if user_list:
        return user_list
    else:
        return None


def delete_from_blacklist(user_id, blacklisted_user_id):
    user = session.query(BlackList).where(and_(
        BlackList.user_id == user_id,
        BlackList.blacklisted_user_id == blacklisted_user_id)
    ).first()
    session.delete(user)
    session.commit()


def delete_from_favorites(user_id, favorite_id):
    user = session.query(Favorites).where(and_(
        Favorites.user_id == user_id,
        Favorites.favorite_id == favorite_id)
    ).first()
    session.delete(user)
    session.commit()
