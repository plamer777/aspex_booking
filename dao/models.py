"""This file contains models to get data from the database"""
import sqlalchemy as sqa
from sqlalchemy.orm import relationship
from dao import Base
# ---------------------------------------------------------------------------


class User(Base):
    """The User model to get data from the user spreadsheet"""
    __tablename__ = 'user'
    id = sqa.Column(sqa.Integer, primary_key=True, autoincrement=True)
    email = sqa.Column(sqa.String)
    password = sqa.Column(sqa.String)
    name = sqa.Column(sqa.String)
    phone = sqa.Column(sqa.String)
    is_active = sqa.Column(sqa.Boolean, default=False)
    tables = relationship('Table', back_populates='client')


class Table(Base):
    """The Table model to get data from the table spreadsheet"""
    __tablename__ = 'table'
    id = sqa.Column(sqa.Integer, primary_key=True, autoincrement=True)
    max_persons = sqa.Column(sqa.Integer)
    booking_time = sqa.Column(sqa.Time, nullable=True)
    persons = sqa.Column(sqa.Integer, default=0)
    is_booked = sqa.Column(sqa.Boolean, default=False)
    client_id = sqa.Column(
        sqa.Integer, sqa.ForeignKey('user.id'), nullable=True)
    client = relationship('User', back_populates='tables')
