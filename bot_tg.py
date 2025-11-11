import logging
from functools import partial
from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env
from error_handler import send_error
from google.cloud import dialogflow
from dialogflow_bot import detect_intent_texts


logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def send_help(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def reply_dialogflow(update, context, project_id):
    """Отвечает первой буквой сообщения пользователя."""
    text = update.message.text

    session_id = f"tg-{update.message.chat_id}"
    response = detect_intent_texts(project_id, session_id, [text], "ru")

    fulfillment = response.query_result.fulfillment_text
    if fulfillment:
        update.message.reply_text(fulfillment)


def _handle_error(update, context, bot, admin_id):

    try:
        err = context.error if hasattr(context, 'error') else None
        if err is None and len(context.args) > 0:

            err = context.args[0]
    except Exception:
        err = None
    if err:
        send_error('Telegram Bot', err, bot, admin_id)

def main() -> None:

    logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO  
)

    env = Env()
    env.read_env()

    tg_bot_token = env.str("TELEGRAM_BOT_TOKEN")
    project_id = env.str("PROJECT_ID")
    bot = Bot(token=env.str("TELEGRAM_BOT_TOKEN"))
    admin_id = env.str("TELEGRAM_CHAT_ID")


    try:
        updater = Updater(token=tg_bot_token)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", send_help))
        

        dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command,
                partial(reply_dialogflow, project_id=project_id),
            )
        )
        dispatcher.add_error_handler(partial(_handle_error, bot=bot, admin_id=admin_id))

        updater.start_polling()

        updater.idle()
    except Exception as e:
        send_error('Telegram Bot', e, bot, admin_id)
        raise
    

if __name__ == '__main__':
    main()
