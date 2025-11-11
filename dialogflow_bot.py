from google.cloud import dialogflow_v2 as dialogflow
from environs import Env
import os
import json
import time
import requests
from google.oauth2 import service_account
import google.auth.transport.requests


def main():
    env = Env()
    env.read_env()

    credentials_path = env.str("GOOGLE_APPLICATION_CREDENTIALS")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    project_id = env.str("PROJECT_ID")

def detect_intent_texts(project_id, session_id, texts, language_code):
 
    from google.cloud import dialogflow

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
  
    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        return response
    

if __name__ == '__main__':
    main()

