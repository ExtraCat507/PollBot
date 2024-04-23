import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class UserSQL(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,autoincrement=True,primary_key=True)

    reference = sqlalchemy.Column(sqlalchemy.String)

    user_id = sqlalchemy.Column(sqlalchemy.String,index=True)

    forms = orm.relationship("Form", back_populates='UserSQL')

