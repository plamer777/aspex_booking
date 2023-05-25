"""This file contains a UserDao class serves as a data access object"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dao.models import User
from services.schemas import UserRegisterSchema
# -------------------------------------------------------------------------


class UserDao:
    """The UserDao class provides access to the user table"""
    def __init__(self) -> None:
        """Initialize the UserDao class"""
        self.model = User

    async def add_new(
            self, db: AsyncSession, user_schema: UserRegisterSchema
    ) -> User | None:
        """This method adds a new user to the user table
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param user_schema: an instance of the UserRegisterSchema with the
        user data
        :return: a User model if user was added successfully or None instead
        """
        try:
            new_user = self.model(**user_schema.dict())
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user
        except Exception as e:
            await db.rollback()
            print(f'There was an error registering user: {e}')
            return None

    async def get_by_email(
            self, db: AsyncSession, email: str
    ) -> User | None:
        """This method returns a user by provided email
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param email: the email address of the searching user
        :return: a User model if user was found or None instead
        """
        found_user = await db.execute(select(self.model).where(
            self.model.email==email))

        return found_user.scalar()

    @staticmethod
    async def update(
            db: AsyncSession, user: User
    ) -> User | None:
        """This method updates user data
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param user: a user model with data to update
        :return: a User model if user was updates successfully or None instead
        """
        try:
            db.add(user)
            await db.commit()
            return user
        except Exception as e:
            await db.rollback()
            print(f'There was an error updating user data: {e}')
            return None
