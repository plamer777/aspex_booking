"""This file contains schemas serves as serializers"""
from datetime import time
from datetime import datetime
from pydantic import BaseModel, PositiveInt, validator, Field, root_validator
from pydantic import EmailStr
from constants import TZ
# --------------------------------------------------------------------------


class BaseUserSchema(BaseModel):
    """The base schema to work with user data"""
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class BaseTableSchema(BaseModel):
    """The base schema to work with table data"""
    id: int
    max_persons: PositiveInt
    booking_time: time | None = None
    persons: int = 0
    is_booked: bool = False

    class Config:
        orm_mode = True


class TableSchema(BaseTableSchema):
    """This schema used as serializer to get a list of tables"""
    class Config:
        orm_mode = True


class TableBookSchema(BaseTableSchema):
    """This schema used as serializer to book a table"""
    id: int | None = None
    max_persons: PositiveInt | None = None
    is_booked: bool | None = False
    client_id: int | None = None
    booking_time: time
    persons: int

    @validator('booking_time')
    def check_booking_time(cls, value: time) -> time:
        """This method validates booking time and provides some booking
        restrictions"""
        current_time = datetime.now(tz=TZ).time()
        if current_time > time(22, 0):
            raise ValueError(
                "Booking will be available tomorrow from 12:00 to 22:00"
            )
        elif value < time(12, 0) or value > time(22, 0):
            raise ValueError(
                "Booking time must be between 12:00 and 22:00")
        elif value < current_time:
            raise ValueError(
                f"The current time is {current_time.strftime('%H:%M:%S')}, "
                f"you was trying to book table at time {value}. "
                f"Please choose another time"
            )

        return value

    class Config:
        orm_mode = True


class TableBookChangeSchema(TableBookSchema):
    """This schema used as serializer to update booking details or cancel
    chosen booking"""
    booking_time: time | None = None
    persons: int | None = None

    @root_validator(pre=True)
    def prevent_change_fields(cls, values: dict) -> dict:
        """This method serves to restrict changing some model fields"""
        values.pop('id', None)
        values.pop('max_persons', None)
        values.pop('client_id', None)
        values['is_booked'] = None
        return values


class UserRegisterSchema(BaseUserSchema):
    """This schema used as serializer to register users"""
    password_repeat: str = Field(exclude=True)
    name: str | None = None
    phone: str | None = None

    @root_validator
    def check_password(cls, values: dict) -> dict:
        """This method checks a length of password and compares two provided
        passwords"""
        password = values.get('password', '')
        password_repeat = values.get('password_repeat', '')

        if not password or len(password) < 8 or password != password_repeat:
            raise ValueError('Passwords do not match or invalid')

        return values


class UserSchema(BaseUserSchema):
    """This schema used as serializer to allow users to log in"""


class Token(BaseModel):
    """This schema used as serializer to work with tokens"""
    email: EmailStr
