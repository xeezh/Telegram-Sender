import asyncio
import configparser
from time import sleep
from os import system
import threading
import os
from ctypes import windll

try:
    from telethon.sync import TelegramClient
    from telethon.tl.functions.messages import GetHistoryRequest
except:
    system('python3 -m pip install telethon')
    from telethon.sync import TelegramClient
    import telethon.tl.functions.messages

config = configparser.ConfigParser()
config.read("config.ini")

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']
api_id_main = config['Telegram_main']['api_id']
api_hash_main = config['Telegram_main']['api_hash']
username_main = config['Telegram_main']['username']

sentMsgs = []


def createClient(msg, uName, id, hash):
    print(msg)
    client = TelegramClient(uName, id, hash)
    client.start()
    return client


def reboot():
    system(f'cd /d {os.getcwd()}')
    system('start python reboot.py')
    quit()


def incorrectDataExit():
    system('cls')
    print('Данные введены неверно!!!')
    print('Закрытие через 5 секунд!!')
    sleep(5)
    exit()


mainCl = createClient('Войдите в мейн аккаунт', username_main, api_id_main, api_hash_main)
mainCl.start()

tasks_queue = []


def new_task(receiver, entity, file, text):
    tasks_queue.append([receiver, entity, file, text])


stop_threads_queue = []


def stop_thread(th_id):
    stop_threads_queue.append(th_id)


async def thread(msg: str, chat: int, thread_id: int, sleep_min: int = 60):
    while thread_id not in stop_threads_queue:
        new_task(
            receiver=chat,
            entity=chat,
            file='banner.jpg',
            text=msg,
        )
        sleep(int(sleep_min) * 60)

    stop_threads_queue.pop(
        stop_threads_queue.index(
            thread_id
        )
    )


def chat_thread(msg: str, chat: int, thread_id: int, sleep_min: int = 60):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(thread(msg, chat, thread_id, sleep_min))
    loop.close()


def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


async def main(mainClient):
    # Console setup
    windll.kernel32.SetConsoleTitleW(f'Auto_Sender by @princemelancholy')
    system('cls')

    # Getting chats
    chats = files(os.getcwd() + '\\chats')

    # Parsing messages
    chats_and_msgs = []
    for chat in chats:
        with open('chats\\' + chat, encoding='utf-8') as f:
            raw = f.readlines()
        chat_id, sleep_min = raw.pop(0).split(';')
        msg = ''.join(raw)

        chats_and_msgs.append([chat_id, msg, sleep_min])

    # Starting threads
    i = 0
    for chat in chats_and_msgs:
        chat_id, message, sleep_min = chat
        chat_id = int(chat_id) if chat_id[1:].isdigit() else chat_id
        x = threading.Thread(target=chat_thread, args=(message, chat_id, i, sleep_min))
        x.start()
        i += 1

    # Waiting for tasks
    while True:
        if len(tasks_queue) > 0:
            task = tasks_queue.pop(0)
            await mainClient.send_message(
                task[0],
                task[3]
            )
        sleep(1)


with mainCl:
    mainCl.loop.run_until_complete(main(mainCl))
