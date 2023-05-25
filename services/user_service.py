"""This unit contains a UserService class providing a business logic to work
with user spreadsheet"""
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from constants import TOKEN_URL
from dao.models import User
from services import schemas
from dao.user_dao import UserDao
from services.schemas import Token
from utils import create_token, decode_token, get_db
# -------------------------------------------------------------------------

oauth_schema: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)


class UserService:
    """The UserService class providing all the functionality needed to work
    with the user spreadsheet"""
    def __init__(self, dao: UserDao = UserDao()) -> None:
        """Initialize the UserService class
        :param dao: A UserDao instance
        """
        self.dao = dao
        self.register_schema = schemas.UserRegisterSchema
        self.user_schema = schemas.UserSchema

    async def register(
            self, db: AsyncSession, user_data: schemas.UserRegisterSchema
    ) -> dict[str, str]:
        """This method serves to register a user and check if the user is
        not already registered. The password will be hashed before being
        stored. The token will be returned if registration is successful
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param user_data: an instance of the UserRegisterSchema with data to
        be stored
        :return: a dictionary with access token
        """
        user = await self.dao.get_by_email(db, user_data.email)

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The email is already registered')

        user_data.password = bcrypt.hashpw(
            user_data.password.encode(), bcrypt.gensalt()).decode()

        new_user = await self.dao.add_new(db, user_data)
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Failed to create new user')
        user.is_active = True
        await self.dao.update(db, user)

        return create_token(new_user.email)

    async def login(
            self, db: AsyncSession, user_data: schemas.UserSchema
    ) -> dict[str, str]:
        """This method serves to allow registered user to log in his account.
        The token will be returned if login is successful
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param user_data: an instance of the UserSchema with data to
        log in
        :return: a dictionary with access token
        """
        user = await self.dao.get_by_email(db, user_data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found')

        elif not bcrypt.checkpw(
                user_data.password.encode(), user.password.encode()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The password is incorrect')
        user.is_active = True
        await self.dao.update(db, user)

        return create_token(user.email)

    async def logout(
            self, db: AsyncSession, user: User
    ) -> None:
        """This method serves to allow registered user to log out
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param user: a User model representing the current user
        """
        user.is_active = False
        loggedout_user = await self.dao.update(db, user)
        if not loggedout_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Failed to logout')

    async def get_by_token(
            self, db: AsyncSession = Depends(get_db),
            token: str = Depends(oauth_schema)
    ) -> User:
        """This method serves to get user by provided token
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param token: a string representing the token
        :return: a User model
        """
        user_data = decode_token(token)
        try:
            token_schema = Token(**user_data)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'There was an error while retrieving user data: {e}'
            )

        user = await self.dao.get_by_email(db, token_schema.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User is not found'
            )
        elif not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User is unauthorized'
            )

        return user
