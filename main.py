import asyncio
import time

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
import requests

from environs import env

dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
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


async def start_bot(bot):
    await dp.start_polling(bot)


if __name__ == '__main__':
    env.read_env()
    tg_token = env('TG_TOKEN')
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {env('DEVMAN_TOKEN')}',
    }
    bot = Bot(token=tg_token)
    asyncio.run(start_bot(bot))
