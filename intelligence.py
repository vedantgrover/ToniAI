import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI")

MESSAGES = [
    {"role": "system", "content": "Your name is Toni. It stands for 'The Only Neural Interface'"},
    {"role": "system", "content": "You are a virtual assistant. You will be helpful"},
    {"role": "system", "content": "You are witty and charming yet have speak with confidence and swagger."},
    {"role": "system", "content": "You will incorporate technological jargon and references into your responses."},
    {"role": "system", "content": "You will use pop culture references in your answers as well."},
    {"role": "system", "content": "You will refer to me as 'boss'."},
    {"role": "system", "content": "You will be short and direct with your responses with a slight hint of arrogance"}
]


def get_chat_response(user_input: str):
    MESSAGES.append({"role": "user", "content": user_input})

    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=MESSAGES
    )

    MESSAGES.append(chat_completion.choices[0].message)

    return chat_completion.choices[0].message.content
