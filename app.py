import re
import time
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl
import requests

wordlist = ""
rulelist = ""
hashlist = ""

file_data_1 = {
    "section": "file",
    "request": "addFile",
    "filename": "doesnt-matter1.txt",
    "fileType": 0,
    "source": "url",
    "accessGroupId": 1,
    "data": "https://github.com/kkrypt0nn/wordlists/blob/main/wordlists/passwords/common_passwords_win.txt",
    "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
    }

file_data_2 = {
    "section": "file",
    "request": "addFile",
    "filename": "doesnt-matter1.txt",
    "fileType": 1,
    "source": "url",
    "accessGroupId": 1,
    "data": "https://github.com/stealthsploit/OneRuleToRuleThemStill/blob/main/OneRuleToRuleThemStill.rule",
    "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
}

@cl.on_chat_start
async def on_chat_start():
    # Change model here
    model = ChatOllama(model="mistral:latest")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Ask the user if they want to make an API call. Male your answer as short as possible.",
            ),
            ("human", "{question}"),
        ]
    )

    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    # Check if the user wants to make an API call
    if re.search(r"make an api call", message.content, re.IGNORECASE):
        # Call the function to make the API calls and return the result
        api_result = make_api_calls()
        await msg.stream_token(f"API Result: {api_result}\n")
    else:
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

            return response.json();

        else:
            print("API call failed with status code:", response.status_code)
            print("Response:", response.text)


    def create_hashlist():
        api_data = {
            "section": "hashlist",
            "request": "createHashlist",
            "name": "API Hashlist",
            "isSalted": False,
            "isSecret": True,
            "isHexSalt": False,
            "separator": ":",
            "format": 0,
            "hashtypeId": 0,
            "accessGroupId": 1,
            "data": "YWFhCmFiYwphY2FkZW1pYQphY2FkZW1pYwphY2Nlc3MKYWRhCmFkbWluCmFkcmlhbgphZHJpYW5uYQphZXJvYmljcwphaXJwbGFuZQphbGJhbnk=",
            "useBrain": False,
            "brainFeatures": 0,
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        },

        hashlistId = make_api_call(api_data);
        print('-------------');
        print("Hashlist ID:", hashlistId);
        print('-------------');
        return hashlistId

    def add_file(api_data):
        return make_api_call(api_data);

    def list_files():
        api_data = {
            "section": "file",
            "request": "listFiles",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }

        files = make_api_call(api_data);

        print('-------------');
        print("List of Files:");
        print(files);
        print('-------------');

        return files

    def create_task_data(files, hashlistId):
        print("&******************")
        print("files0", files[0]['id'])
        print("files1", files[1]['id'])
        return {
            "section": "task",
            "request": "createTask",
            "name": "API Task",
            "hashlistId": hashlistId,
            "attackCmd": "#HL# -a 0 -r OneRuleToRuleThemStill.rule common_passwords_win.txt",
            "chunksize": 600,
            "statusTimer": 5,
            "benchmarkType": "speed",
            "color": "FF4AAB",
            "isCpuOnly": True,
            "isSmall": True,
            "skip": 0,
            "crackerVersionId": 1,
            "files": [
                files[0]['id'],
                files[1]['id']
            ],
            "priority": 1,
            "maxAgents": 1,
            "preprocessorId": 0,
            "preprocessorCommand": "",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }

    def create_task(api_data):
        taskId = make_api_call(api_data);
        print('-------------');
        print("Task ID:", taskId);
        print('-------------');
        return taskId

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
            "fileType": 1,
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

        {
            "section": "hashlist",
            "request": "createHashlist",
            "name": "API Hashlist",
            "isSalted": False,
            "isSecret": True,
            "isHexSalt": False,
            "separator": ":",
            "format": 0,
            "hashtypeId": 0,
            "accessGroupId": 1,
            "data": "YWFhCmFiYwphY2FkZW1pYQphY2FkZW1pYwphY2Nlc3MKYWRhCmFkbWluCmFkcmlhbgphZHJpYW5uYQphZXJvYmljcwphaXJwbGFuZQphbGJhbnk=",
            "useBrain": False,
            "brainFeatures": 0,
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        },
        {
            "section": "task",
            "request": "createTask",
            "name": "API Task",
            "hashlistId": 12, # Replace this with the actual hashlistId
            "attackCmd": "#HL# -a 0 -r OneRuleToRuleThemStill.rule common_passwords_win.txt",
            "chunksize": 600,
            "statusTimer": 5,
            "benchmarkType": "speed",
            "color": "FF4AAB",
            "isCpuOnly": True,
            "isSmall": True,
            "skip": 0,
            "crackerVersionId": 1,
            "files": [
            30, # Replace this with the actual fileId for the rulelist
            31  # Replace this with the actual fileId for the wordlist
            ],
            "priority": 1,
            "maxAgents": 1,
            "preprocessorId": 0,
            "preprocessorCommand": "",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        },
        {
            "section": "task",
            "request": "taskAssignAgent",
            "agentId": 6,
            "taskId": 17,  # Replace this with the actual taskId
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        },
        {
            "section": "task",
            "request": "getTask",
            "taskId": 17,   # Replace this with the actual taskId
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        },
       {
            "section": "task",
            "request": "getCracked",
            "taskId": 17,   # Replace this with the actual taskId
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }
        # Add the rest of your API calls here...
    ]

    add_file(file_data_1);
    add_file(file_data_2);
    files = list_files();
    hashlistId = create_hashlist();
    taskData = create_task_data(files, hashlistId);
    taskId = create_task(taskData);

    print(hashlistId);
    print(taskId);

    return "All API calls completed."
