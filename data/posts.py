import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    reply_to_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return f'{self.id}: (to {self.reply_to_id}) {self.title}\t{self.content}'
