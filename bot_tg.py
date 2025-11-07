import logging
from telegram import Update, ForceReply
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

def reply_dialogflow(update, context):
    """Отвечает первой буквой сообщения пользователя."""
    text = update.message.text

    response = detect_intent_texts(
        project_id, str(update.message.chat_id), [text], 'ru'
    )

    fulfillment = response.query_result.fulfillment_text
    if fulfillment:
        update.message.reply_text(fulfillment)


def _handle_error(update, context):
    """Global error handler for dispatcher: report exception to admin."""
    try:
        err = context.error if hasattr(context, 'error') else None
        if err is None and len(context.args) > 0:
            # older versions sometimes pass the exception as first arg
            err = context.args[0]
    except Exception:
        err = None
    if err:
        send_error('Telegram Bot', err)

def main() -> None:

    logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO  
)

    env = Env()
    env.read_env()

    global TELEGRAM_BOT_TOKEN, project_id
    TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")
    project_id = env.str("PROJECT_ID")


    try:
        updater = Updater(token=TELEGRAM_BOT_TOKEN)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", send_help))

        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_dialogflow))
        dispatcher.add_error_handler(_handle_error)

        updater.start_polling()

        updater.idle()
    except Exception as e:
        send_error('Telegram Bot', e)
        raise
    

if __name__ == '__main__':
    main()
