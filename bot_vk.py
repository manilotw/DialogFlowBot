import random

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from environs import Env
from dialogflow_bot import detect_intent_texts

env = Env()
env.read_env()

project_id = env.str("PROJECT_ID")
token = env.str("VK_API_TOKEN")

# def echo(event, vk_api):
#     vk_api.messages.send(
#         user_id=event.user_id,
#         message=event.text,
#         random_id=random.randint(1,1000)
#     )

def send_message(event, vk_api):
    response = detect_intent_texts(project_id, str(event.user_id), [event.text], 'ru')
    vk_api.messages.send(
        user_id=event.user_id,
        message=response,
        random_id=random.randint(1,1000)
    )

if __name__ == "__main__":
    vk_session = vk.VkApi(token=token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            send_message(event, vk_api)