from sqlalchemy import select, update, delete

from models import (
    User,
    Chat,
    UserGroupChat,
)


async def get_or_create(session, model, **kwargs):
    sql = select(model).filter_by(**kwargs)
    instance = await session.execute(sql)
    try:
        instance = instance.scalar_one()
        return instance
    except Exception as exc:
        instance = model(**kwargs)
        session.add(instance)
        await session.commit()
        return instance


async def add_chat(session, chat_id: str):
    await get_or_create(session=session, model=Chat, chat_id=chat_id)


async def add_user(session, chat_id: str, user_tag: str):
    # 1. Добавить в Юзеры (User), если его там нет
    # 2. Создать чат в таблицу Чат (Chat), если нет (Chat)
    # 3. Создать запись в таблицу UserGroupChat chat_id <-> username

    user = await get_or_create(session=session, model=User, user_tag=user_tag)
    chat = await get_or_create(session=session, model=Chat, chat_id=chat_id)
    await get_or_create(session=session, model=UserGroupChat, chat_id=chat.id, user_id=user.id)


async def __get_user(session, user_tag_):
    sql = select(User).filter_by(user_tag=user_tag_)
    query = await session.execute(sql)
    return query.scalar_one()


async def __get_chat(session, chat_id_):
    sql = select(Chat).filter_by(chat_id=chat_id_)
    query = await session.execute(sql)
    return query.scalar_one()


async def delete_user_from_chat(session, chat_id, user_tag):
    user = await __get_user(session=session, user_tag_=user_tag)
    chat = await __get_chat(session=session, chat_id_=chat_id)

    sql = delete(UserGroupChat).where(UserGroupChat.chat_id == chat.id, UserGroupChat.user_id == user.id)
    query = await session.execute(sql)

    await session.commit()


async def get_all_members_from_chat(session, chat_id) -> list:
    user_list = []
    chat = await __get_chat(session=session, chat_id_=chat_id)
    sql = select(
        UserGroupChat
    ).filter_by(
        chat_id=chat.id
    )
    query = await session.execute(sql)
    users = query.scalars().all()

    for x in users:
        sql = select(User).filter_by(id=x.user_id)
        query = await session.execute(sql)
        user = query.scalar_one()

        user_list.append(user.user_tag)
    return user_list


async def set_group_for_user_in_chat(session, chat_id__, user_tag, group_):
    user = await __get_user(session=session, user_tag_=user_tag)
    chat = await __get_chat(session=session, chat_id_=chat_id__)
    print(user.id, chat.id)
    sql = update(
        UserGroupChat
    ).filter_by(
        user_id=user.id,  # 17
        chat_id=chat.id,  # 9
    ).values(
        group=group_,
    )
    await session.execute(sql)
    await session.commit()


async def get_members_by_group_from_chat(session, chat_id, group):
    members: list = []
    chat = await __get_chat(session=session, chat_id_=chat_id)
    sql = select(
        UserGroupChat
    ).filter_by(
        chat_id=chat.id,
        group=group,
    )
    query = await session.execute(sql)
    userchatgroups = query.scalars().all()
    for userchatgroup in userchatgroups:
        sql = select(User).filter_by(
            id=userchatgroup.user_id
        )
        query = await session.execute(sql)
        user = query.scalar_one()
        members.append(user.user_tag)
    return members


async def change_user_tag(old_user_tag, new_user_tag, session):
    sql = update(
        User
    ).filter_by(
        user_tag=old_user_tag
    ).update(
        user_tag=new_user_tag
    )
    query = await session.execute(sql)
    session.commit()


async def get_groups_from_chat(session, chat_id):
    group_list = []
    chat = await __get_chat(session=session, chat_id_=chat_id)
    sql = select(
        UserGroupChat
    ).filter_by(
        chat_id=chat.id
    )
    query = await session.execute(sql)
    groups = query.scalars().all()
    for q in groups:
        group_list.append(q.group)
    return set(group_list)
