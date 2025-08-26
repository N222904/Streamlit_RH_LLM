from langchain_google_genai import ChatGoogleGenerativeAI
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory

from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

from instructions import instruction

from dotenv import load_dotenv
load_dotenv()

import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.65,
    safety_settings=safety_settings,
    cache=True
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instruction),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)

set_llm_cache(InMemoryCache())

chain = prompt | llm