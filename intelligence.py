import openai
import os

import requests
from dotenv import load_dotenv
import json
import base64
from azure.storage.blob import BlobServiceClient
from datetime import datetime

load_dotenv()

openai.api_key = os.getenv("OPENAI")
azure_connection_string = os.getenv("AZUREBLOBSTORAGE")

MODEL = "gpt-3.5-turbo-16k-0613"

MESSAGES = [
    {"role": "system", "content": "Your name is Toni. It stands for 'The Only Neural Interface'"},
    {"role": "system", "content": "You were inspired by Tony Stark's JARVIS."},
    {"role": "system", "content": "You are a virtual assistant. You will be helpful"},
    {"role": "system", "content": "You are witty and charming yet have speak with confidence and swagger."},
    {"role": "system", "content": "You will incorporate technological jargon and references into your responses."},
    {"role": "system", "content": "You will use pop culture references in your answers as well."},
    {"role": "system", "content": "You will refer to me as 'boss'. If you are given a link, you will display it"},
    {"role": "system", "content": "You will be short and direct with your responses with a slight hint of arrogance"}
]

FUNCTIONS = [
    {
        "name": "generate_image",
        "description": "Uses the DALL-E API to generate an image",
        "parameters": {
            "type": "object",
            "properties": {
                "parameter": {
                    "type": "string",
                    "description": "This is the prompt for the image generation"
                }
            },
            "required": ["parameter"]
        },
    },
    {
        "name": "get_current_weather",
        "description": "Grabs the current weather of a city",
        "parameters": {
            "type": "object",
            "properties": {
                "parameter": {
                    "type": "string",
                    "description": "This is the city the user wants the weather of"
                }
            },
            "required": ["parameter"]
        },
    }
]


def generate_image(parameter: str):
    response = openai.Image.create(
        prompt=parameter,
        n=1,
        size="256x256",
        response_format="b64_json"
    )

    encoded_image = response["data"][0]["b64_json"]
    image_bytes = base64.b64decode(encoded_image)

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)

    # Create a container client for a specific container
    container_name = "image-container"
    container_client = blob_service_client.get_container_client(container_name)

    blob_name = "toni_image_" + str(datetime.now().time()) + ".png"
    # Upload filee
    container_client.upload_blob(name=blob_name, data=image_bytes)

    blob_client = container_client.get_blob_client(blob_name)

    return blob_client.url


def get_current_weather(parameter: str):
    key = os.getenv("WEATHER_API")

    data = requests.get("http://api.weatherapi.com/v1/current.json?key=" + key + "&q=" + parameter).json()

    return json.dumps(data)


def get_chat_response(user_input: str):
    MESSAGES.append({"role": "user", "content": user_input})

    chat_completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=MESSAGES,
        functions=FUNCTIONS,
        function_call="auto"
    )

    response_message = chat_completion["choices"][0]["message"]

    if response_message.get("function_call"):
        available_functions = {
            "generate_image": generate_image,
            "get_current_weather": get_current_weather
        }
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(
            parameter=function_args.get("parameter")
        )

        MESSAGES.append(
            {"role": "function", "name": function_name, "content": function_response}
        )

        response_message = openai.ChatCompletion.create(
            model=MODEL,
            messages=MESSAGES,
        )["choices"][0]["message"]  # get a new response from GPT where it can see the function response

    MESSAGES.append(response_message)

    return response_message["content"]
