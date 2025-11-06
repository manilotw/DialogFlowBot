import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env
from error_handler import send_error

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
    try:
        text = update.message.text
        # Call Dialogflow directly to get the fulfillment text
        from google.cloud import dialogflow

        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, str(update.message.chat_id))

        text_input = dialogflow.TextInput(text=text, language_code='ru')
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        fulfillment = response.query_result.fulfillment_text
        if fulfillment:
            update.message.reply_text(fulfillment)
    except Exception as e:
        pass

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
        """Start the bot."""
        updater = Updater(token=TELEGRAM_BOT_TOKEN)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", send_help))

        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_dialogflow))

        # Start the Bot
        updater.start_polling()

        updater.idle()
    except Exception as e:
        send_error('Telegram Bot', e)
        raise
    

if __name__ == '__main__':
    main()
