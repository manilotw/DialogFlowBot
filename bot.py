import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env
from run import detect_intent_texts, project_id

env = Env()
env.read_env()

TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO  # Логирование будет на уровне INFO, не показываются ошибки
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def dialogflow_response(update, context):
    """Отвечает первой буквой сообщения пользователя."""
    try:
        text = update.message.text
        response = detect_intent_texts(project_id, str(update.message.chat_id), [text], 'ru')
        update.message.reply_text(response)
    except Exception as e:
        # Ошибка просто игнорируется, без логирования
        pass

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - handle the message with dialogflow
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, dialogflow_response))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT.
    updater.idle()

if __name__ == '__main__':
    main()
