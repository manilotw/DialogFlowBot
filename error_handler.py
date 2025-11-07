import traceback
from functools import lru_cache
from telegram import Bot
from environs import Env


@lru_cache()
def _load_bot_and_admin():
    """Lazy load Bot and admin id from environment.

    This avoids doing file I/O or creating network clients at import time.
    """
    env = Env()
    env.read_env()
    bot = Bot(token=env.str("TELEGRAM_BOT_TOKEN"))
    admin_id = env.str("TELEGRAM_CHAT_ID")
    return bot, admin_id


def send_error(bot_name: str, error: Exception):
    """Отправляет сообщение об ошибке админу в Telegram."""
    error_text = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    message = (
        f"🚨 *Ошибка в боте {bot_name}:*\n"
        f"```\n{error_text}\n```"
    )
    bot, admin_id = _load_bot_and_admin()
    bot.send_message(chat_id=admin_id, text=message, parse_mode="Markdown")