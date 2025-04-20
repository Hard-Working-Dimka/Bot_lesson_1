import asyncio
import time
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
import requests

from environs import env

env.read_env()
tg_token = env('TG_TOKEN')
url = 'https://dvmn.org/api/long_polling/'
headers = {
    'Authorization': f'Token {env('DEVMAN_TOKEN')}',
}
dev_tg_token = env('DEV_TG_TOKEN')

bot = Bot(token=tg_token)
dp1 = Dispatcher()

dev_bot = Bot(token=dev_tg_token)
dp2 = Dispatcher()


class MyLogsHandler(logging.Handler):
    async def emit(self, record):
        await dev_bot.send_message(5316948794, 'привет!')


logger = logging.getLogger('bot')
logger.setLevel(level=logging.DEBUG)
logger.addHandler(MyLogsHandler())


@dp1.message(CommandStart())
async def cmd_start(message: Message):
    logger.info("Я новый логер!")
    payload = {}
    timestamp = None
    while True:
        try:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            response = response.json()

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(90)
            continue

        if response.get('last_attempt_timestamp'):
            timestamp = response['last_attempt_timestamp']

        if response.get('timestamp_to_request'):
            timestamp = response['timestamp_to_request']

        if response.get('new_attempts'):
            text_message = 'У вас проверили работу: '
            work = response['new_attempts'][0]['lesson_title']
            lesson_url = response['new_attempts'][0]['lesson_url']
            if response['new_attempts'][0]['is_negative']:
                await message.answer(
                    text=f'{text_message} "{work}". \n\n {lesson_url} \n\n Работа не прошла проверку!')
            else:
                await message.answer(text=f'{text_message} "{work}". \n\n {lesson_url} \n\n Работа прошла проверку!')
        payload = {'timestamp': timestamp}


async def start_bots():
    # await asyncio.gather(dp1.start_polling(bot), dp2.start_polling(dev_bot))
    task_bot1 = asyncio.create_task(dp1.start_polling(bot))
    task_bot2 = asyncio.create_task(dp2.start_polling(dev_bot))
    await task_bot1
    await task_bot2

if __name__ == '__main__':
    asyncio.run(start_bots())
