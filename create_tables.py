"""This file contains functions to create and fill up the database's
spreadsheets"""
from asyncio import run
from dao import Base, engine
from dao.models import Table
from utils import get_db
# ------------------------------------------------------------------------


async def create_tables() -> None:
    """This function creates the tables in the database"""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    fixtures = [2] * 7 + [3] * 6 + [6] * 3
    db = await get_db()
    for max_persons in fixtures:
        new_table = Table(max_persons=max_persons)
        db.add(new_table)
    await db.commit()
    await db.close()


run(create_tables())
