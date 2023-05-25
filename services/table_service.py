"""This unit contains a TableService class providing a business logic to work
with table spreadsheet"""
from datetime import datetime, timedelta
from typing import Any, Sequence
from fastapi import HTTPException, status
from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from constants import TZ, DEADLINE_HOURS
from dao.models import Table
from dao.table_dao import TableDao
from services.schemas import (
    TableSchema, TableBookSchema, TableBookChangeSchema)
# ----------------------------------------------------------------------------


class TableService:
    """The TableService class provides all necessary functions to work with
    table spreadsheet"""
    def __init__(self, dao: TableDao = TableDao()) -> None:
        """Initialize the TableService class
        :param dao: A TableDao instance to receive a raw data from the database
        """
        self.dao = dao
        self.table_schema = TableSchema

    async def get_all(
            self, db: AsyncSession
    ) -> Sequence[Row | RowMapping | Any] | None:
        """This method returns a list of tables received from the dao or
        raise 404-exception if no tables were received
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :return: a list of Table models
        """
        tables = await self.dao.get_all(db)
        if not tables:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Cannot find vacant tables')

        return tables

    async def get_by_client(
            self, db: AsyncSession, email: str
    ) -> Sequence[Row | RowMapping | Any] | None:
        """This method returns a list of Table models booked by the certain
        client
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param email: the email address of the client
        :return: a list of Table models
        """
        client_tables = await self.dao.get_by_client_email(db, email)

        return client_tables

    async def _check_and_get_table(
            self, db: AsyncSession, table_id: int,
            book: bool = True
    ) -> Table | None:
        """This method serves to check whether the given table exists in the
        database and returns the corresponding model found by its id
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param table_id: the id of the table to check
        :param book: a boolean indicating whether the is booking, updating or
        canceling
        :return: the corresponding model found by the id or None if not found
        """
        table = await self.dao.get_by_id(db, table_id)

        if not table:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The table does not exist'
            )
        elif book and table.is_booked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The table is booked'
            )

        return table

    @staticmethod
    def _check_client_and_time(
            user_id: int, table: TableBookSchema
    ) -> None:
        """This method serves to check whether the given user is a client of
        the table and if time allows to update or cancel the current booking
        :param user_id: the id of the user to check
        :param table: an instance of the TableBookSchema
        """
        if table.client_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You have not credentials to access this table'
            )

        elif table.booking_time < (
                datetime.now(tz=TZ) + timedelta(hours=DEADLINE_HOURS)).time():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You cannot cancel or change booking less than an hour'
            )

    async def book_new(
            self, db: AsyncSession, table: TableBookSchema
    ) -> Table | None:
        """This method serves to book a new table
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param table: an instance of the TableBookSchema with booking details
        :return: a Table model if booking was successful or None otherwise
        """
        checking_table = await self._check_and_get_table(db, table.id)

        if table.persons > checking_table.max_persons:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'The maximum number of persons for table: '
                       f'{checking_table.max_persons}'
            )
        table.max_persons = checking_table.max_persons
        table.is_booked = True
        booked_table = await self.dao.book_one(db, table)

        return booked_table

    async def change_booking(
            self, db: AsyncSession, table: TableBookChangeSchema,
            user_id: int
    ) -> Table | None:
        """This method serves to change the booking details for provided table
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param table: an instance of the TableBookSchema with booking details
        to update
        :param user_id: the id of the table's client
        :return: a Table model if updating was successful or None otherwise
        """
        updating_table = await self._check_and_get_table(
            db, table.id, book=False)
        self._check_client_and_time(user_id, updating_table)
        updated_table = await self.dao.update_booking(db, table)

        return updated_table

    async def cancel_booking(
            self, db: AsyncSession, table_id: int, user_id: int
    ) -> Table | None:
        """This method serves to cancel table's booking
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param table_id: the id of the table to cancel
        :param user_id: the id of the table's client
        :return: a Table model if booking was successful or None otherwise
        """
        table = await self._check_and_get_table(db, table_id, book=False)
        self._check_client_and_time(user_id, table)
        cancelled_table = await self.dao.cancel_booking(db, table_id)
        return cancelled_table
