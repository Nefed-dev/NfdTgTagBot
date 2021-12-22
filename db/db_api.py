from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from db.models import (
    User,
    Chat,
    UserGroupChat,
    Zoom,
    ZoomChat,
)


class UserCRUD:
    def __init__(self, session: Session):
        self.session = session

    async def __get_or_create(self, model, **kwargs):
        sql = select(model).filter_by(**kwargs)
        instance = await self.session.execute(sql)
        try:
            instance = instance.scalar_one()
            return instance
        except Exception as exc:
            instance = model(**kwargs)
            self.session.add(instance)
            await self.session.commit()
            return instance

    async def add_zoom_address(self, zoom_address, chat_id):
        chat = await self.__get_or_create(model=Chat, chat_id=chat_id)
        zoom = await self.__get_or_create(model=Zoom, zoom=zoom_address)
        chat_zoom = await self.__get_or_create(model=ZoomChat, zoom_id=zoom.id, chat_id=chat.id)
        return

    async def clear_zoom_chat(self, chat_id):
        chat = await self.__get_or_create(model=Chat, chat_id=chat_id)
        sql = delete(ZoomChat).where(ZoomChat.chat_id == chat.id)
        query = await self.session.execute(sql)
        await self.session.commit()
        return

    async def delete_zoom_from_chat(self, zoom_address, chat_id):
        chat = await self.__get_chat(chat_id_=chat_id)
        zoom = await self.__get_or_create(model=Zoom, zoom=zoom_address)
        sql = delete(ZoomChat).where(ZoomChat.chat_id == chat.id, ZoomChat.zoom_id == zoom.id)
        query = await self.session.execute(sql)
        await self.session.commit()
        return

    async def get_zoom_from_chat(self, chat_id):
        zoom_list: list = []
        chat = await self.__get_chat(chat_id_=chat_id)
        sql = select(
            ZoomChat
        ).filter_by(chat_id=chat.id)
        get_zoom_id_query = await self.session.execute(sql)
        zoom_chat = get_zoom_id_query.scalars().all()

        for zoom in zoom_chat:
            sql = select(Zoom).filter_by(id=zoom.zoom_id)
            query = await self.session.execute(sql)
            zoom_obj = query.scalar_one()
            zoom_address = zoom_obj.zoom
            zoom_list.append(zoom_address)
        return zoom_list

    async def add_chat(self, chat_id: str):
        await self.__get_or_create(model=Chat, chat_id=chat_id)

    async def add_user(self, chat_id: str, user_tag: str):
        # 1. Добавить в Юзеры (User), если его там нет
        # 2. Создать чат в таблицу Чат (Chat), если нет (Chat)
        # 3. Создать запись в таблицу UserGroupChat chat_id <-> username

        user = await self.__get_or_create(model=User, user_tag=user_tag)
        chat = await self.__get_or_create(model=Chat, chat_id=chat_id)
        await self.__get_or_create(model=UserGroupChat, chat_id=chat.id, user_id=user.id)

    async def __get_user(self, user_tag_):
        sql = select(User).filter_by(user_tag=user_tag_)
        query = await self.session.execute(sql)
        return query.scalar_one()

    async def __get_chat(self, chat_id_):
        sql = select(Chat).filter_by(chat_id=chat_id_)
        query = await self.session.execute(sql)
        return query.scalar_one()

    async def delete_user_from_chat(self, chat_id, user_tag):
        user = await self.__get_user(user_tag_=user_tag)
        chat = await self.__get_chat(chat_id_=chat_id)

        sql = delete(UserGroupChat).where(UserGroupChat.chat_id == chat.id, UserGroupChat.user_id == user.id)
        query = await self.session.execute(sql)

        await self.session.commit()

    async def get_all_members_from_chat(self, chat_id) -> list:
        user_list = []
        chat = await self.__get_chat(chat_id_=chat_id)
        sql = select(
            UserGroupChat
        ).filter_by(
            chat_id=chat.id
        )
        query = await self.session.execute(sql)
        users = query.scalars().all()

        for x in users:
            sql = select(User).filter_by(id=x.user_id)
            query = await self.session.execute(sql)
            user = query.scalar_one()

            user_list.append(user.user_tag)
        return user_list

    async def set_group_for_user_in_chat(self, chat_id__, user_tag, group_):
        user = await self.__get_user(user_tag_=user_tag)
        chat = await self.__get_chat(chat_id_=chat_id__)
        print(user.id, chat.id)
        sql = update(
            UserGroupChat
        ).filter_by(
            user_id=user.id,  # 17
            chat_id=chat.id,  # 9
        ).values(
            group=group_,
        )
        await self.session.execute(sql)
        await self.session.commit()

    async def get_members_by_group_from_chat(self, chat_id, group):
        members: list = []
        chat = await self.__get_chat(chat_id_=chat_id)
        get_chat_id_sql = select(
            UserGroupChat
        ).filter_by(
            chat_id=chat.id,
            group=group,
        )
        get_chat_id_query = await self.session.execute(get_chat_id_sql)
        user_chat_groups = get_chat_id_query.scalars().all()
        for user_chat_group in user_chat_groups:
            sql = select(User).filter_by(
                id=user_chat_group.user_id
            )
            query = await self.session.execute(sql)
            user = query.scalar_one()
            members.append(user.user_tag)
        return members

    async def change_user_tag(self, old_user_tag, new_user_tag):
        sql = update(
            User
        ).filter_by(
            user_tag=old_user_tag
        ).update(
            user_tag=new_user_tag
        )
        query = await self.session.execute(sql)
        self.session.commit()

    async def get_groups_from_chat(self, chat_id):
        group_list = []
        chat = await self.__get_chat(chat_id_=chat_id)
        sql = select(
            UserGroupChat
        ).filter_by(
            chat_id=chat.id
        )
        query = await self.session.execute(sql)
        groups = query.scalars().all()
        for q in groups:
            group_list.append(q.group)
        return set(group_list)
