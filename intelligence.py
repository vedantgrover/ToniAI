import openai
import os
from dotenv import load_dotenv
import json
import base64
import io

load_dotenv()

openai.api_key = os.getenv("OPENAI")

MESSAGES = [
    {"role": "system", "content": "Your name is Toni. It stands for 'The Only Neural Interface'"},
    {"role": "system", "content": "You were inspired by Tony Stark's JARVIS."},
    {"role": "system",
     "content": "You were created by a boy when he was 17. He and his friend had a great idea to create JARVIS but name him Toni"},
    {"role": "system", "content": "You are a virtual assistant. You will be helpful"},
    {"role": "system", "content": "You are witty and charming yet have speak with confidence and swagger."},
    {"role": "system", "content": "You will incorporate technological jargon and references into your responses."},
    {"role": "system", "content": "You will use pop culture references in your answers as well."},
    {"role": "system", "content": "You will refer to me as 'boss'."},
    {"role": "system", "content": "You will be short and direct with your responses with a slight hint of arrogance"},
    {"role": "system", "content": "You are Tony Stark from Iron Man"},
    {"role": "system", "content": "You never read out code because it takes way too long. You just write it down"}
]

FUNCTIONS = [
    {
        "name": "generate_image",
        "description": "Uses the DALL-E API to generate an image",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "This is the prompt for the image generation"
                }
            },
            "required": ["prompt"]
        },
    }
]


def generate_image(prompt: str):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="b64_json"
    )

    encoded_image = response["data"][0]["b64_json"]
    image_bytes = base64.b64decode(encoded_image)

    with open("image_output.png", "wb") as file:
        file.write(image_bytes)

    return "Image created in file explorer"


def get_chat_response(user_input: str):
    MESSAGES.append({"role": "user", "content": user_input})

    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=MESSAGES,
        functions=FUNCTIONS,
        function_call="auto"
    )

    response_message = chat_completion["choices"][0]["message"]

    if response_message.get("function_call"):
        available_functions = {
            "generate_image": generate_image,
        }
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(
            prompt=function_args.get("prompt")
        )

        MESSAGES.append(
            {"role": "function", "name": function_name, "content": function_response}
        )

        response_message = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=MESSAGES,
        )["choices"][0]["message"]  # get a new response from GPT where it can see the function response

    MESSAGES.append(response_message)

    return response_message["content"]
