from environs import Env
import json
import argparse
import textwrap
from google.oauth2 import service_account


def create_intent(
    project_id, display_name, training_phrases_parts, message_texts, credentials=None
):
    """Create an intent of the given intent type."""
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        default="questions.json",
        help=textwrap.dedent(
            """Введите путь до JSON,
                        откуда будут браться данные для обучения.
                        По умолчанию данные находятся в questions.json
                        в корне проекта."""
        ),
    )
    env = Env()
    env.read_env()

    credentials = service_account.Credentials.from_service_account_file(
        env.str("GOOGLE_APPLICATION_CREDENTIALS"),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    args = parser.parse_args()
    project_id = env.str("PROJECT_ID")

    questions_path = args.path
    with open(questions_path, "r", encoding="utf-8") as file:
        topics = json.loads(file.read())
    for topic, phrase in topics.items():
        response = create_intent(
            project_id,
            topic,
            phrase["questions"],
            [phrase["answer"]],
            credentials
        )
        print(f"Intent created: {response.display_name}")

if __name__ == '__main__':
    main()
