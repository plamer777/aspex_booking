"""This file contains a TableDao class serves as a data access object"""
from datetime import datetime, timedelta
from typing import Any, Sequence
from sqlalchemy import select, update, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from constants import TZ
from dao.models import Table, User
from services.schemas import TableBookSchema, TableBookChangeSchema
# --------------------------------------------------------------------------


class TableDao:
    """The TableDao class provides access to the table spreadsheet"""
    def __init__(self) -> None:
        """Initialize the TableDao class"""
        self.model = Table
        self.user = User

    async def get_all(
            self, db: AsyncSession
    ) -> Sequence[Row | RowMapping | Any]:
        """This method returns a list of all vacant tables
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :return: a list of Table models
        """
        await self.update_availability(db)

        tables = await db.execute(
            select(self.model).where(
                self.model.is_booked == False, self.model.persons == 0))

        return tables.scalars().all()

    async def get_by_id(
            self, db: AsyncSession, table_id: int
    ) -> Table | None:
        """This method returns a table by its id
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param table_id: the id of the searching table
        :return: the Table model or None if table was not found
        """
        table = await db.execute(
            select(self.model).where(self.model.id == table_id))

        return table.scalar()

    async def book_one(
            self, db: AsyncSession, table: TableBookSchema
    ) -> Table | None:
        """This method serves to book a new table
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param table: an instance of the TableBookSchema class
        :return: The Table model or None if booking the table was failed
        """
        try:
            await db.execute(update(self.model).where(
            self.model.id == table.id).values(**table.dict(exclude_none=True)))
            await db.commit()
            new_table = await self.get_by_id(db, table.id)
            return new_table
        except Exception as e:
            await db.rollback()
            print(f'There was an error during booking: {e}')
            return None

    async def get_by_client_email(
            self, db: AsyncSession, email: str
    ) -> Sequence[Row | RowMapping | Any] | None:
        """This method returns a table by email of its client
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param email: the email address of the client of the searching table
        :return: a list of Table models
        """
        tables = await db.execute(
            select(self.model).join(self.user).where(
                self.user.email == email, self.model.is_booked == True))

        return tables.scalars().all()

    async def update_booking(
            self, db: AsyncSession, table: TableBookChangeSchema
    ) -> Table | None:
        """This method serves to update booking details
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param table: an instance of the TableBookChangeSchema class
        :return: the Table model if booking details were updated successfully
        or None otherwise
        """

        updated_table = await self.book_one(db, table)

        return updated_table

    async def cancel_booking(
            self, db: AsyncSession, table_id: int
    ) -> Table | None:
        """This method allows to cancel booking
        :param db: an instance of the AsyncSession provides a connection
        to the database
        :param table_id: the id of the table to cancel
        :return: a Table model if booking was canceled successfully or
        None otherwise
        """
        cancelled_table = await self.get_by_id(db, table_id)
        cancelled_table.is_booked = False
        try:
            db.add(cancelled_table)
            await db.commit()
            return cancelled_table
        except Exception as e:
            await db.rollback()
            print(f'There was an error during canceling your booking: {e}')
            return None

    async def update_availability(
            self, db: AsyncSession,
    ) -> None:
        """This method updates an availability of the early booked tables
        :param db: an instance of the AsyncSession provides a connection
        to the database
        """
        await db.execute(update(self.model).where(
            self.model.booking_time < (datetime.now(tz=TZ) - timedelta(
                hours=2)).time()).values(is_booked=False))
