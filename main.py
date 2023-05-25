"""This is a main file to start the app, it also contains FastApi views"""
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from dao.models import User
from services import schemas
from container import user_service, table_service
from utils import get_db, get_description
from constants import API_VERSION, API_TITLE
# ------------------------------------------------------------------------

app = FastAPI(
    version=API_VERSION, description=get_description(), title=API_TITLE
)


@app.get(
    '/', response_class=RedirectResponse,
    description='The start page of the application')
async def index_page() -> RedirectResponse:
    """This view serves to redirect requests from start route '/' to '/docs'"""
    return '/docs'


@app.post(
    '/user/signup', summary='Register a new user',
    description='This route serves to register a new user')
async def register(
        user_schema: schemas.UserRegisterSchema,
        session: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """This view serves to register a new user
    :param user_schema: an instance of UserRegisterSchema class
    :param session: an instance of AsyncSession providing by get_db function
    :return: a dictionary containing an access token
    """
    token = await user_service.register(session, user_schema)
    return token


@app.post(
    '/user/login', summary='Sign in to user account',
    description='This route serves to log in to the user account')
async def login(
        user_schema: schemas.UserSchema,
        session: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """This view serves to allow user to login
    :param user_schema: an instance of UserRegisterSchema class
    :param session: an instance of AsyncSession providing by get_db function
    :return: a dictionary containing an access token
    """

    token = await user_service.login(session, user_schema)
    return token


@app.post(
    '/user/logout', summary='Sign out from user account',
    description='This route serves to allow user to log out from his account')
async def logout(
        user: User = Depends(user_service.get_by_token),
        session: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """This view serves to log out from account
    :param user: a model representing current user
    :param session: an instance of AsyncSession providing by get_db function
    :return: a dictionary containing an access token
    """

    await user_service.logout(session, user)
    return {'message': 'Logout was successful'}


@app.get(
    '/table/vacant', response_model=list[schemas.TableSchema],
    summary='Get a list of all available tables',
    description='This route returns all vacant tables')
async def all_tables(
        session: AsyncSession = Depends(get_db)
) -> list[schemas.TableSchema]:
    """This view serves to receive all vacant tables
    :param session: an instance of AsyncSession providing by get_db function
    :return: a list of TableSchema instances
    """
    tables = await table_service.get_all(session)
    return tables


@app.get(
    '/table/me', response_model=list[schemas.TableSchema],
    summary='Get all tables of a current user',
    description='This route returns all tables of booked by the current user')
async def client_tables(
        session: AsyncSession = Depends(get_db),
        user: User = Depends(user_service.get_by_token)
) -> list[schemas.TableSchema]:
    """This view serves to receive all tables booked by the current user
    :param session: an instance of AsyncSession providing by get_db function
    :param user: a model representing current user
    :return: a list of TableSchema instances
    """
    tables = await table_service.get_by_client(session, user.email)
    return tables


@app.post(
    '/table/book/{table_id}', summary='Booking a new table',
    description='This route serves to book a new table')
async def book_table(
        table_id: int, table: schemas.TableBookSchema,
        session: AsyncSession = Depends(get_db),
        user: User = Depends(user_service.get_by_token)
) -> dict[str, str]:
    """This view serves to book a table by its id
    :param table_id: the id of the table to book
    :param table: an instance of TableBookSchema class
    :param session: an instance of AsyncSession providing by get_db function
    :param user: a model representing current user
    :return: a dictionary representing a result of the booking
    """
    table.id = table_id
    table.client_id = user.id
    table = await table_service.book_new(session, table)
    if not table:
        return {'message': 'Failed to book table'}
    return {'message': 'The table is booked successfully'}


@app.put(
    '/table/change/{table_id}', summary='Change a booking parameters',
    description='This route serves to allow the current user to change the '
                'parameters of his booking such as persons amount and booking '
                'time')
async def change_table_booking(
        table_id: int, table: schemas.TableBookChangeSchema,
        session: AsyncSession = Depends(get_db),
        user: User = Depends(user_service.get_by_token)
) -> dict[str, str]:
    """This view serves to change booking options of a chosen table
    :param table_id: the id of the table to book
    :param table: an instance of TableBookSchema class
    :param session: an instance of AsyncSession providing by get_db function
    :param user: a model representing current user
    :return: a dictionary representing a result of the booking
    """
    table.id = table_id
    table.client_id = user.id
    table = await table_service.change_booking(session, table, user.id)
    if not table:
        return {'message': 'Failed to change bookings'}
    return {'message': 'The booking was changed successfully'}


@app.delete(
    '/table/cancel/{table_id}', summary='Cancel booking',
    description='This route serves to cancel chosen booking of a table. You '
                'cannot cancel booking less than an hour before early chosen '
                'booking time')
async def cancel_booking(
        table_id: int, session: AsyncSession = Depends(get_db),
        user: User = Depends(user_service.get_by_token)
) -> dict[str, str]:
    """This view serves to cancel booking of a chosen table
    :param table_id: the id of the table to book
    :param session: an instance of AsyncSession providing by get_db function
    :param user: a model representing current user
    :return: a dictionary representing a result of the booking
    """

    canceled = await table_service.cancel_booking(session, table_id, user.id)
    if canceled:
        return {'message': 'Booking is cancelled successfully'}
    return {'message': 'Failed to cancel booking'}
