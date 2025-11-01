import traceback
import os
from telegram import Bot
from environs import Env

env = Env()
env.read_env()

bot = Bot(token=env.str('TELEGRAM_BOT_TOKEN'))
admin_id = env.str('TELEGRAM_CHAT_ID')

def send_error(bot_name: str, error: Exception):
    """Отправляет сообщение об ошибке админу в Telegram."""
    error_text = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    message = (
        f"🚨 *Ошибка в боте {bot_name}:*\n"
        f"```\n{error_text}\n```"
    )
    bot.send_message(chat_id=admin_id, text=message, parse_mode='Markdown')
