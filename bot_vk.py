import random

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from environs import Env
from dialogflow_bot import detect_intent_texts
from telegram import Bot
from error_handler import send_error 



def send_message(event, vk_api, project_id):

    session_id = f"vk-{event.user_id}"
    response = detect_intent_texts(project_id, session_id, [event.text], "ru")

    if getattr(response.query_result.intent, 'is_fallback', False):
        return

    message = response.query_result.fulfillment_text or ''
    if message:
        vk_api.messages.send(
            user_id=event.user_id,
            message=message,
            random_id=random.randint(1,1000)
        )

def main():

    env = Env()
    env.read_env()

    project_id = env.str("PROJECT_ID")
    token = env.str("VK_API_TOKEN")
    bot = Bot(token=env.str("TELEGRAM_BOT_TOKEN"))
    admin_id = env.str("TELEGRAM_CHAT_ID")

    try:
        vk_session = vk.VkApi(token=token)
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                send_message(event, vk_api, project_id)
    except Exception as e:
        from error_handler import send_error
        send_error("VK Bot", e, bot, admin_id)

if __name__ == "__main__":
    main()
