import json
import os

from json import JSONDecodeError

import requests
from pydantic import ValidationError

from starlette import status
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from models import ChatRequest, PersonaResponse

load_dotenv()

# os eken api dgtta key eka load krgnnawa
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

app = FastAPI(description="FAST API APP for AI integration")

# functions for generate system prompts
def get_system_prompt(base_prompt : str, persona : str):

    return (f"{base_prompt} \n" 
            "ALWAYS respond ONLY as strict JSON matching this schema and nothing else :\n"
            f"{{\n \"persona\": {persona},\n \"content\": string,\n \"tips\": string [] | null \n }}\n"
            f"Do not include backticks or markdown"
            )



@app.post("/chat")
def call_openrouter(request : ChatRequest):

    # mekedi wenne uda hadpu get system prompt design eka show wenwa | \n backsticks ewa ehema okkoma ethanadi hadala thmai danne
    # print(get_system_prompt(base_prompt="You are a helpful AI assistant", persona="assistant"))


    headers = {
        "Authorization" : f"Bearer {OPENROUTER_KEY}",
        "Content-Type" : "application/json"
    }

    body = {
        "model" : "meta-llama/llama-3.3-70b-instruct:free",
        "messages" : [
            {"role" : "system", "content" : get_system_prompt(base_prompt="You are a helpful AI assistant", persona="assistant")}, # me thiyenne system eke message eka (system prompt) | methana system persona eka apita denna puluwan | function ekak create krla eka apita methanata use krnna plwn design ekata

            {"role" : "user" , "content" : request.message} # api dana message eka

        ]
    }

    llm_response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)

    # print(llm_response.json())

    #content eka witrk show krnna nam apita acess krnna one choises kiyana key eka (swagger eke response output eka show wenwa dict ekk widiyt)
    llm_resp_json = llm_response.json()

    data = llm_resp_json["choices"][0]["message"]["content"]

    try:
        data_json_obj = json.loads(data)  # loads json string to a pythin dictionary object

    except JSONDecodeError as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f"LLM Did not Return a valid json {str(e)}")

    try:
        return PersonaResponse.model_validate(data_json_obj)
    except ValidationError as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f"Pydantic model validation error {str(e)}")