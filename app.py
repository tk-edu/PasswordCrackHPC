import re
import time
import base64
import requests
import validators
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
import chainlit as cl

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
    model = ChatOllama(model="mistral:latest")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Ask the user if they want to make an API call. Make your answer as short as possible.",
            ),
            ("human", "{question}"),
        ]
    )

    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")

    msg = cl.Message(content="")

    if re.search(r"make an api call", message.content, re.IGNORECASE):
        api_result = make_all_calls()
        await msg.stream_token(f"API Result: {api_result}\n")
        
    elif re.search(r"hash\s*list:?", message.content, re.IGNORECASE):
        # Check if the user attached a file
        if len(message.elements) > 0:
            with open(message.elements[0].path, "r") as file:
                hashlist = file.read().strip()
        # Assume the hashlist is in the message
        else:
            # Assume that the hashlist is
            # after the first colon
            hashlist = message.content.split(":", 1)[1].strip()
            # If a URL is provided, get the
            # hashlist from there
            if validators.url(hashlist):
                print("Got hashlist from remote source")
                hashlist = requests.get(hashlist).text.strip()
        api_result = make_all_calls(hashlist=hashlist)
        await msg.stream_token(f"API Result: {api_result}\n")
        
    elif re.search(r"word\s*list:?", message.content, re.IGNORECASE):
        # Check if the user attached a file
        if len(message.elements) > 0:
            with open(message.elements[0].path, "r") as file:
                wordlist = file.read().strip()
        # Assume the wordlist is in the message
        else:
            # Assume that the wordlist is
            # after the first colon
            wordlist = message.content.split(":", 1)[1].strip()
            # If a URL is provided, get the
            # wordlist from there
            if validators.url(wordlist):
                print("Got wordlist from remote source")
                wordlist = requests.get(wordlist).text.strip()
        api_result = make_all_calls(wordlist=wordlist)
        await msg.stream_token(f"API Result: {api_result}\n")
        
    elif re.search(r"rule\s*list:?", message.content, re.IGNORECASE):
        # Check if the user attached a file
        if len(message.elements) > 0:
            with open(message.elements[0].path, "r") as file:
                rulelist = file.read().strip()
        # Assume the rulelist is in the message
        else:
            # Assume that the rulelist is
            # after the first colon
            rulelist = message.content.split(":", 1)[1].strip()
            # If a URL is provided, get the
            # rulelist from there
            if validators.url(rulelist):
                print("Got rulelist from remote source")
                rulelist = requests.get(rulelist).text.strip()
        api_result = make_all_calls(rulelist=rulelist)
        await msg.stream_token(f"API Result: {api_result}\n")
    else:
        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)

        await msg.send()

def make_all_calls(*, hashlist=None, wordlist=None, rulelist=None):
    def make_api_call(api_data):
        url = "http://localhost:8080/api/user.php"
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=api_data, headers=headers)

        if response.status_code == 200:
            print("API call successful!")
            print("Response:", response.json())
            return response.json()
        else:
            print("API call failed with status code:", response.status_code)
            print("Response:", response.text)

    def create_hashlist(hashlist):
        api_data = {
            "section": "hashlist",
            "request": "createHashlist",
            "name": "API Hashlist",
            "isSalted": False,
            "isSecret": False,
            "isHexSalt": False,
            "separator": ":",
            "format": 0,
            "hashtypeId": 0,
            "accessGroupId": 1,
            "data": base64.b64encode(hashlist.encode()).decode(),
            "useBrain": False,
            "brainFeatures": 0,
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }
        return make_api_call(api_data)

    def add_file_url(api_data):
        api_data = {
            "section": "file",
            "request": "addFile",
            "filename": "doesnt-matter1.txt",
            "fileType": 0,
            "source": "url",
            "accessGroupId": 1,
            "data": "https://github.com/kkrypt0nn/wordlists/blob/main/wordlists/passwords/common_passwords_win.txt",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }
        return make_api_call(api_data)
    
    def add_file_inline(thelist, list_name, list_type):
        api_data = {
            "section": "file",
            "request": "addFile",
            "filename": list_name,
            "fileType": list_type,
            "source": "inline",
            "accessGroupId": 1,
            "data": base64.b64encode(thelist.encode()).decode(),
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }
        return make_api_call(api_data)

    def list_files():
        api_data = {
            "section": "file",
            "request": "listFiles",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }
        return make_api_call(api_data)

    def create_task_data(files, hashlistId):
        file_list = [file['fileId'] for file in files['files']]
        hashlistId = hashlistId.get('hashlistId')
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
            "files": file_list,
            "priority": 1,
            "maxAgents": 1,
            "preprocessorId": 0,
            "preprocessorCommand": "",
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }

    def create_task(api_data):
        taskId = make_api_call(api_data)
        return taskId.get('taskId')

    def assign_agent(agentId, taskId):
        api_data = {
            "section": "task",
            "request": "taskAssignAgent",
            "agentId": agentId,
            "taskId": taskId,
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }
        return make_api_call(api_data)

    def get_task(taskId):
        api_data = {
            "section": "task",
            "request": "getTask",
            "taskId": taskId,
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }
        return make_api_call(api_data)

    def get_cracked(taskId):
        api_data = {
            "section": "task",
            "request": "getCracked",
            "taskId": taskId,
            "accessKey": "am1wGeToLAhrlpWErAtxDzXXGsj8s1"
        }
        return make_api_call(api_data)

    def get_plain_text_passwords(cracked):
        return [item['plain'] for item in cracked['cracked']]

    # Add files
    print("WORDLIST: ")
    print(wordlist)
    print("RULELIST: ")
    print(rulelist)
    add_file_inline(wordlist, "api_wordlist.txt", 0)
    add_file_inline(rulelist, "api_rulelist.txt", 1)
    print("FILES ADDED")

    # List files
    files = list_files()
    print("FILES LISTED: ")
    print(files)

    print("HASHLIST: ")
    print(hashlist)
    # Create hashlist
    hashlistId = create_hashlist(hashlist)
    print("HASHLIST CREATED")
    print(hashlistId)

    # Create task data
    taskData = create_task_data(files, hashlistId)
    print("TASK DATA CREATED")
    print(taskData)

    # Create task
    taskId = create_task(taskData)
    print("TASK CREATED")
    print(taskId)

    # Assign agent
    agent = assign_agent(9, taskId)
    print("AGENT ASSIGNED")
    print(agent)

    # Check task status
    while not get_task(taskId).get('isComplete'):
        getTask = get_task(taskId)
        print("TASK DETAILS")
        print(getTask)
        time.sleep(5)

    # Get cracked passwords
    cracked = get_cracked(taskId)
    print("CRACKED")
    print(cracked)

    # Get plain text passwords
    plain_text_passwords = get_plain_text_passwords(cracked)

    return plain_text_passwords
