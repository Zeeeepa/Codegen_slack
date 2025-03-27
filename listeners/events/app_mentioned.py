from ai.providers import get_provider_response
from logging import Logger
from slack_sdk import WebClient
from slack_bolt import Say
from ..listener_utils.listener_constants import DEFAULT_LOADING_TEXT, MENTION_WITHOUT_TEXT
from ..listener_utils.parse_conversation import parse_conversation
from agents.agent_registry import AgentRegistry
import os

"""
Handles the event when the app is mentioned in a Slack channel, retrieves the conversation context,
and generates an AI response if text is provided, otherwise sends a default response
"""


def app_mentioned_callback(client: WebClient, event: dict, logger: Logger, say: Say):
    try:
        channel_id = event.get("channel")
        thread_ts = event.get("thread_ts")
        user_id = event.get("user")
        text = event.get("text")

        if thread_ts:
            conversation = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=10)["messages"]
        else:
            conversation = client.conversations_history(channel=channel_id, limit=10)["messages"]
            thread_ts = event["ts"]

        conversation_context = parse_conversation(conversation[:-1])

        if text:
            waiting_message = say(text=DEFAULT_LOADING_TEXT, thread_ts=thread_ts)
            
            # Check if we should use an agent or the default AI provider
            active_agent = os.environ.get("ACTIVE_AGENT")
            
            if active_agent and active_agent in AgentRegistry.get_available_agents():
                # Use the active agent
                logger.info(f"Using agent: {active_agent}")
                agent_class = AgentRegistry.get_agent(active_agent)
                agent = agent_class()
                response = agent.process_message(text, conversation_context)
            else:
                # Use the default AI provider
                logger.info("Using default AI provider")
                response = get_provider_response(user_id, text, conversation_context)
                
            client.chat_update(channel=channel_id, ts=waiting_message["ts"], text=response)
        else:
            waiting_message = say(text=DEFAULT_LOADING_TEXT, thread_ts=thread_ts)
            response = MENTION_WITHOUT_TEXT
            client.chat_update(channel=channel_id, ts=waiting_message["ts"], text=response)

    except Exception as e:
        logger.error(e)
        client.chat_update(channel=channel_id, ts=waiting_message["ts"], text=f"Received an error from Bolty:\n{e}")
