import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    verifyed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    keys_already_gen = sqlalchemy.Column(sqlalchemy.Boolean, default=0)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class MainClass:
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    reply_to_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    files = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    blessing = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        title = str(self.title)
        content = str(self.content)
        max_len = 20
        if len(title) > max_len:
            title = title[:max_len - 3] + '...'
        if len(content) > max_len:
            content = content[:max_len - 3] + '...'

        return f'Post(id={self.id}, reply_to_id={self.reply_to_id}, title={title}, content={content})'


class b(SqlAlchemyBase, MainClass):
    __tablename__ = '/b'


class abu(SqlAlchemyBase, MainClass):
    __tablename__ = '/abu'


class media(SqlAlchemyBase, MainClass):
    __tablename__ = '/media'


class r(SqlAlchemyBase, MainClass):
    __tablename__ = '/r'


class soc(SqlAlchemyBase, MainClass):
    __tablename__ = '/soc'


class au(SqlAlchemyBase, MainClass):
    __tablename__ = '/au'


class bi(SqlAlchemyBase, MainClass):
    __tablename__ = '/bi'


class biz(SqlAlchemyBase, MainClass):
    __tablename__ = '/biz'


class bo(SqlAlchemyBase, MainClass):
    __tablename__ = '/bo'


class cc(SqlAlchemyBase, MainClass):
    __tablename__ = '/cc'


class de(SqlAlchemyBase, MainClass):
    __tablename__ = '/de'


class di(SqlAlchemyBase, MainClass):
    __tablename__ = '/di'


class diy(SqlAlchemyBase, MainClass):
    __tablename__ = '/diy'


class mus(SqlAlchemyBase, MainClass):
    __tablename__ = '/mus'


class p(SqlAlchemyBase, MainClass):
    __tablename__ = '/p'


class pa(SqlAlchemyBase, MainClass):
    __tablename__ = '/pa'


class hry(SqlAlchemyBase, MainClass):
    __tablename__ = '/hry'


class news(SqlAlchemyBase, MainClass):
    __tablename__ = '/news'


class po(SqlAlchemyBase, MainClass):
    __tablename__ = '/po'
