import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class KeyForReg(SqlAlchemyBase):
    __tablename__ = 'keys'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    key = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=1)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
