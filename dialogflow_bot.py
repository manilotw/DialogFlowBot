from google.cloud import dialogflow_v2 as dialogflow
from environs import Env
import os
import json
import time
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

env = Env()
env.read_env()

credentials_path = env.str("GOOGLE_APPLICATION_CREDENTIALS")

# Устанавливаем переменную для Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

project_id = env.str("PROJECT_ID")

def detect_intent_texts(project_id, session_id, texts, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    from google.cloud import dialogflow

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    # Use the provided session_id (allow callers to build composite ids like "vk-..." or "tg-...")
    # and return the full DetectIntentResponse so callers can inspect intent fields.
    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        return response
    
