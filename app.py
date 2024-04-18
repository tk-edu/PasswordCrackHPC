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
            # Check if the API call is for listing files and save the fileId accordingly
            if api_data.get('request') == 'listFiles':
                for file_info in response.json().get('files', []):
                    if file_info['fileType'] == 0:
                        wordlist = file_info['fileId']
                        print(wordlist)
                    elif file_info['fileType'] == 1:
                        rulelist = file_info['fileId']
                        print(rulelist)
            # Check if the API call is for creating a hashlist and save the hashlistId accordingly
            elif api_data.get('request') == 'createHashlist':
                hashlist = response.json().get('hashlistId')
                print(hashlist)
            elif api_data.get('request') == 'createTask':
                task_id = response.json().get('taskId')
                print(task_id)
            elif api_data.get('request') == 'getTask':
                if response.json().get('isComplete') == False:
                    print("Sleepy time")
                    time.sleep(10)
                    make_api_call(api_data)
                    
                
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

    # Make each API call
    for api_call in api_calls:
        make_api_call(api_call)
        time.sleep(5)
    
    
    return "All API calls completed."