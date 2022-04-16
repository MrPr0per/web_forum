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
    verifyed=sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

class main_class():
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    reply_to_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    files = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f'{self.id}: (to {self.reply_to_id}) {self.title}\t{self.content}'

class b(SqlAlchemyBase,main_class):
    __tablename__ = '/b'


class abu(SqlAlchemyBase,main_class):
    __tablename__ = '/abu'

class media(SqlAlchemyBase,main_class):
    __tablename__ = '/media'

class r(SqlAlchemyBase,main_class):
    __tablename__ = '/r'

class soc(SqlAlchemyBase,main_class):
    __tablename__ = '/soc'

class au(SqlAlchemyBase,main_class):
    __tablename__ = '/au'

class bi(SqlAlchemyBase,main_class):
    __tablename__ = '/bi'

class biz(SqlAlchemyBase,main_class):
    __tablename__ = '/biz'

class bo(SqlAlchemyBase,main_class):
    __tablename__ = '/bo'

class cc(SqlAlchemyBase,main_class):
    __tablename__ = '/cc'

class de(SqlAlchemyBase,main_class):
    __tablename__ = '/de'

class di(SqlAlchemyBase,main_class):
    __tablename__ = '/di'

class diy(SqlAlchemyBase,main_class):
    __tablename__ = '/diy'

class mus(SqlAlchemyBase,main_class):
    __tablename__ = '/mus'

class p(SqlAlchemyBase,main_class):
    __tablename__ = '/p'

class pa(SqlAlchemyBase,main_class):
    __tablename__ = '/pa'

class hry(SqlAlchemyBase,main_class):
    __tablename__ = '/hry'

class news(SqlAlchemyBase,main_class):
    __tablename__ = '/news'

class po(SqlAlchemyBase,main_class):
    __tablename__ = '/po'
