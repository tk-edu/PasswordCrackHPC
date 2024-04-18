import time
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl
import requests


@cl.on_chat_start
async def on_chat_start():
    # Change model here
    model = ChatOllama(model="mistral:latest")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Ask the user if they want to make an API call",
            ),
            ("human", "{question}"),
        ]
    )
    
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    # Ask the user if they want to make an API call
    api_call_response = input("Do you want to make an API call? (yes/no): ")
    if api_call_response.lower() == "yes":
        make_api_calls()

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()

def make_api_calls():
    def make_api_call(api_data):
        url = "http://localhost:8080/api/user.php"  # Replace this with your actual API endpoint
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=api_data, headers=headers)
        
        if response.status_code == 200:
            print("API call successful!")
            print("Response:", response.json())
        else:
            print("API call failed with status code:", response.status_code)
            print("Response:", response.text)

    # Example API calls
    api_calls = [
        {
            "section": "file",
            "request": "addFile",
            "filename": "doesnt-matter1.txt",
            "fileType": 0,
            "source": "url",
            "accessGroupId": 1,
            "data": "https://github.com/kkrypt0nn/wordlists/blob/main/wordlists/passwords/common_passwords_win.txt",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        },
        {
            "section": "file",
            "request": "addFile",
            "filename": "doesnt-matter1.txt",
            "fileType": 0,
            "source": "url",
            "accessGroupId": 1,
            "data": "https://github.com/stealthsploit/OneRuleToRuleThemStill/blob/main/OneRuleToRuleThemStill.rule",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        },
        
        {
            "section": "file",
            "request": "listFiles",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        },
        # Add the rest of your API calls here...
    ]

    # Make each API call
    for api_call in api_calls:
        make_api_call(api_call)
        time.sleep(5)