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
                "You're a very knowledgeable cybersecurity expert who knows everything about password cracking with hashcat. Your specialty is how you format the Hashcat commands. Ask users to provide a hashlist file, a wordlist file, and a rule file. Please keep all answers as short as possible.",
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

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()

