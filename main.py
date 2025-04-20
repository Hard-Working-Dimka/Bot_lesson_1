import asyncio
import time
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
import requests
from environs import env

bot_dispatcher = Dispatcher()
dev_bot_dispatcher = Dispatcher()


class MyLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.tg_bot.send_message(self.chat_id, log_entry))


@bot_dispatcher.message(CommandStart())
async def cmd_start(message: Message):
    try:
        payload = {}
        timestamp = None
        while True:
            try:
                response = requests.get(url, headers=headers, params=payload)
                response.raise_for_status()
                response = response.json()

            except requests.exceptions.ReadTimeout:
                logger.warning('No response was received from the server in the expected time.')
                continue
            except requests.exceptions.ConnectionError:
                logging.warning('Internet connection lost.')
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
                    await message.answer(
                        text=f'{text_message} "{work}". \n\n {lesson_url} \n\n Работа прошла проверку!')
            payload = {'timestamp': timestamp}
    except Exception as error:
        logger.error(error, exc_info=True)


async def start_bots():
    task_bot = asyncio.create_task(bot_dispatcher.start_polling(bot))
    task_dev_bot = asyncio.create_task(dev_bot_dispatcher.start_polling(dev_bot))
    logger.info('Bot is running.')
    await task_bot
    await task_dev_bot


if __name__ == '__main__':
    env.read_env()
    tg_token = env('TG_TOKEN')
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {env('DEVMAN_TOKEN')}',
    }
    dev_tg_token = env('DEV_TG_TOKEN')
    chat_id = env('CHAT_ID')

    bot = Bot(token=tg_token)
    dev_bot = Bot(token=dev_tg_token)

    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(MyLogsHandler(dev_bot, chat_id=chat_id))
    asyncio.run(start_bots())
