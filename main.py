import asyncio
import configparser
from random import choice
from pyrogram import Client, filters, idle


async def UserBot():
    config = configparser.ConfigParser()
    config.read("apies.ini")
    channels = {}
    session = config["apies"]["api_session"]
    appUserBot = Client("my_account", api_id=config["apies"]["api_id"], api_hash=config["apies"]["api_hash"],
                        session_string=session, in_memory=True)

    await appUserBot.start()
    ALLOWED_USER_ID = (await appUserBot.get_me()).id
    await appUserBot.stop()

    with open("phrases.txt", mode="r", encoding="utf-8") as file:
        lines = list(map(lambda line: line.rstrip(), file.readlines()))

    @appUserBot.on_message(filters.user(ALLOWED_USER_ID))
    async def on_message(client, message):
        if message.forward_from_chat:
            if str(message.forward_from_chat.type) == 'ChatType.CHANNEL':
                channel_info = await appUserBot.get_chat(message.forward_from_chat.id)
                try:
                    await appUserBot.join_chat(channel_info.linked_chat.id)
                    channels[str(message.forward_from_chat.id)] = channel_info.linked_chat.id
                    await appUserBot.send_message(ALLOWED_USER_ID, 'Канал добавлен!', reply_to_message_id=message.id)
                except Exception as e:
                    if str(e) == "'NoneType' object has no attribute 'id'":
                        await appUserBot.send_message(
                            ALLOWED_USER_ID, 'Ошибка, в этом канале нет комментариев!',
                            reply_to_message_id=message.id
                        )
                    else:
                        await appUserBot.send_message(
                            ALLOWED_USER_ID,
                            'Подайте заявку на вступление в группу для обсужения, после ее одобрения отправьте пост заново',
                            reply_to_message_id=message.id
                        )

    @appUserBot.on_message()
    async def handle_new_message(client, message):
        if message.sender_chat:
            if str(message.sender_chat.id) in channels.keys() and \
                    str(message.chat.type) == 'ChatType.SUPERGROUP' and message.views:
                comment_text = choice(lines)
                await appUserBot.send_message(
                    channels[str(message.sender_chat.id)],
                    comment_text,
                    reply_to_message_id=message.id
                )

    await appUserBot.start()

    await idle()



from fastapi import FastAPI

app = FastAPI()
#
#
@app.get("/")
async def read_root():
    loop = asyncio.get_event_loop()
    task = loop.create_task(UserBot())
    future = asyncio.Future()

    # Прикрепляем задачу и Future к текущему event loop
    asyncio.ensure_future(task, loop=loop)
    asyncio.ensure_future(future, loop=loop)
    return {"Hello": "Space!"}

# asyncio.run(UserBot())
#
# if __name__ == '__main__':
#     appUserBot.run()
