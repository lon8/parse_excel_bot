from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from bot.handlers import start, handle_file
from bot.db import create_table
from bot.config import BOT_TOKEN

async def on_startup(_):
    create_table()

def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    
    dp.register_message_handler(start, commands="start")
    dp.register_message_handler(handle_file, content_types=types.ContentType.DOCUMENT)
    
    print('Bot was started')
    executor.start_polling(dp, on_startup=on_startup)

if __name__ == '__main__':
    main()
