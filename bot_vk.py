import random

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from environs import Env
from google.cloud import dialogflow
from dialogflow_bot import detect_intent_texts 


def send_message(event, vk_api):

    response = detect_intent_texts(
        project_id, str(event.user_id), [event.text], 'ru'
    )

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

    global project_id, token
    project_id = env.str("PROJECT_ID")
    token = env.str("VK_API_TOKEN")

    try:
        vk_session = vk.VkApi(token=token)
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                send_message(event, vk_api)
    except Exception as e:
        from error_handler import send_error
        send_error("VK Bot", e)

if __name__ == "__main__":
    main()
