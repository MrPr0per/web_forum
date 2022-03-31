import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

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

