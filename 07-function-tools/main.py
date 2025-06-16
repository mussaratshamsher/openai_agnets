
import os 
import asyncio
import chainlit as cl
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from agents.run import RunConfig
from agents.tool import function_tool

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)    
model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=external_client
)

@function_tool("get_weather")
def get_weather(location: str, unit: str = "C") -> str:
    return f"The weater in {location} is 22 degrees {unit}"

async def main():
   my_assistant = Agent(
    name="Weather Assistant",
    instructions="You respond to weather queries. You also respond to tell any location with in a specific area. Show temperature in celsius and fahrenheit."
    "Show suggestion to show temperatue of next 24hours. Show map of the area.",
    tools=[get_weather],
    model=model
   )     

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="⛅☔Check weather by Location.🌍")
    
@cl.on_message
async def handle_message(message:cl.Message):
    history = cl.user_session.get("history")
    msg = cl.Message(content="")
    await msg.send()

    history.append({"role":"user", "content":message.content})
    result = Runner.run_streamed(my_assistant, history, run_concfig=config)

    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            token = event.data.delta
            await msg.stream_token(token)    

    history.append({"role":"assistant", "content":result.final_output})
    cl.user_session.set("history", history)

