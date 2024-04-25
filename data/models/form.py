import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class FormSQL(SqlAlchemyBase):
    __tablename__ = 'forms'

    num = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,autoincrement=True)

    id = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)


    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('UserSQL')

    file = sqlalchemy.Column(sqlalchemy.String) #Вопросы

    answers = sqlalchemy.Column(sqlalchemy.String) #Ответы пользователей


