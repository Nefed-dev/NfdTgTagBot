from .db_api import UserCRUD
from loader import async_session


async def get_db_crud():
    async with async_session() as session:
        async with session.begin():
            return UserCRUD(session)
