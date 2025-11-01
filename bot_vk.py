import random

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from environs import Env

env = Env()
env.read_env()

project_id = env.str("PROJECT_ID")
token = env.str("VK_API_TOKEN")


def send_message(event, vk_api):
    # Call Dialogflow directly here so we can check `is_fallback` and stay silent for VK
    from google.cloud import dialogflow

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, str(event.user_id))

    text_input = dialogflow.TextInput(text=event.text, language_code='ru')
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    # If the detected intent is a fallback (Dialogflow didn't understand), do not reply in VK
    if getattr(response.query_result.intent, 'is_fallback', False):
        return

    message = response.query_result.fulfillment_text or ''
    if message:
        vk_api.messages.send(
            user_id=event.user_id,
            message=message,
            random_id=random.randint(1,1000)
        )

if __name__ == "__main__":
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