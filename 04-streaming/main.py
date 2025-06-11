
import chainlit as cl
import os
import asyncio
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner 
from dotenv import load_dotenv
from agents.run import RunConfig

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

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

my_assistant = Agent(
    name="Personal Assistant",
    instructions="You are a helpful personal assistant."
)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Welcome! How can I assist you today?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    
    msg = cl.Message(content="")
    await msg.send()

    history.append({"role": "user", "content": message.content})
    # Run the agent with streaming enabled
    result = Runner.run_streamed(my_assistant, history, run_config=config)

        # Stream the response token by token
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            token = event.data.delta
            await msg.stream_token(token)

          #exact code to implement streaming in sdk
    # async for event in result.stream_events():
    #     if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
    #         print(event.data.delta, end="", flush=True)
     
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    
    await cl.Message(content=incremental_response).send()




# import os
# from dotenv import load_dotenv
# from typing import cast
# import chainlit as cl
# from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
# from agents.run import RunConfig

# # Load the environment variables from the .env file
# load_dotenv()

# gemini_api_key = os.getenv("GEMINI_API_KEY")

# # Check if the API key is present; if not, raise an error
# if not gemini_api_key:
#     raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# @cl.on_chat_start
# async def start():
#     external_client = AsyncOpenAI(
#         api_key=gemini_api_key,
#         base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#     )

#     model = OpenAIChatCompletionsModel(
#         model="gemini-2.0-flash",
#         openai_client=external_client
#     )

#     config = RunConfig(
#         model=model,
#         model_provider=external_client,
#         tracing_disabled=True
#     )
#     """Set up the chat session when a user connects."""
#     # Initialize an empty chat history in the session.
#     cl.user_session.set("chat_history", [])

#     cl.user_session.set("config", config)
#     agent: Agent = Agent(name="Assistant", instructions="You are a helpful assistant", model=model)
#     cl.user_session.set("agent", agent)

#     await cl.Message(content="Welcome to the Panaversity AI Assistant! How can I help you today?").send()

# @cl.on_message
# async def main(message: cl.Message):
#     """Process incoming messages and generate responses."""
#     # Retrieve the chat history from the session.
#     history = cl.user_session.get("chat_history") or []

#     # Append the user's message to the history.
#     history.append({"role": "user", "content": message.content})

#     # Create a new message object for streaming
#     msg = cl.Message(content="")
#     await msg.send()

#     agent: Agent = cast(Agent, cl.user_session.get("agent"))
#     config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

#     try:
#         print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
#         # Run the agent with streaming enabled
#         result = Runner.run_streamed(agent, history, run_config=config)

#         # Stream the response token by token
#         async for event in result.stream_events():
#             if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
#                 token = event.data.delta
#                 await msg.stream_token(token)

#         # Append the assistant's response to the history.
#         history.append({"role": "assistant", "content": msg.content})

#         # Update the session with the new history.
#         cl.user_session.set("chat_history", history)

#         # Optional: Log the interaction
#         print(f"User: {message.content}")
#         print(f"Assistant: {msg.content}")

#     except Exception as e:
#         await msg.update(content=f"Error: {str(e)}")
#         print(f"Error: {str(e)}")
