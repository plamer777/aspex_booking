from datetime import datetime, timedelta
from calendar import timegm
import jwt
from fastapi import HTTPException, status
from constants import (
    JWT_SECRET, JWT_ALGO, JWT_EXP_HOURS, API_DESCRIPTION, README_FILE)
from dao import SessionLocal
# --------------------------------------------------------------------------


async def get_db():
    async with SessionLocal() as db:
        return db


def create_token(email: str) -> dict[str, str]:
    token_data = {
        'email': email,
        'exp': timegm(
            (datetime.utcnow() + timedelta(hours=JWT_EXP_HOURS)).timetuple())
    }
    access_token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGO)
    return {'access_token': access_token}


def decode_token(access_token: str) -> dict[str, str]:

    try:
        token = access_token.split('Bearer ')[-1]
        user_data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return user_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Cannot confirm credentials, error: {e}')


def read_from_file(filename: str) -> str:
    """This function serves to load data from file by provided filename
    :param filename: the name of the file to read
    :return: a string containing the data read from the file
    """
    try:
        with open(filename, encoding='utf-8') as f:
            file_data = f.read()

        return file_data
    except Exception as e:
        print(f'Cannot read from file, error: {e}')
        return ''


def get_description() -> str:
    """This function serves to return a description for application
    :return: a string containing the description
    """
    description = read_from_file(README_FILE)
    if not description:
        description = API_DESCRIPTION

    return description
