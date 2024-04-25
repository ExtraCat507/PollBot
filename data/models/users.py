import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class UserSQL(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)

    #reference = sqlalchemy.Column(sqlalchemy.String)

    reference = sqlalchemy.Column(sqlalchemy.String,index=True)

    first_name = sqlalchemy.Column(sqlalchemy.String)
    last_name = sqlalchemy.Column(sqlalchemy.String)
    polls_list = sqlalchemy.Column(sqlalchemy.String,nullable=True)

    forms = orm.relationship("FormSQL", back_populates='user')

