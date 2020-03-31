from slack import RTMClient

import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
import certifi
from onboarding_tutorial import OnboardingTutorial
import boss

import configsparser

# first time invoking the boss
firstCall = False


# Initialize a Flask app to host the events adapter
app = Flask(__name__)
token = 'xoxb-600605134164-977423189251-T1jDl044w2Ww94pKptF7tFYW'
signing_secret = '4b26af99665e5f84a4542140bdbc65c9'

slack_events_adapter = SlackEventAdapter(signing_secret, "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=token)

# For simplicity we'll store our app data in-memory with the following data structure.
# onboarding_tutorials_sent = {"channel": {"user_id": OnboardingTutorial}}
onboarding_tutorials_sent = {}

received_messages_id = []

history = []

user_ids = []

def response(user_id: str, channel: str, query: str):
    global firstCall
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()
    message["text"] = boss.getAnswer(query, firstCall)
    if firstCall:
        firstCall = False

    # Post the onboarding message in Slack
    response = slack_web_client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial
    history.append(query)
    history.append(message["text"])
    print(history)

@slack_events_adapter.on("app_home_opened")
def sendHello(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    if not user_id in user_ids and len(configsparser.getActiveAgents()) == 1 and configsparser.getActiveAgents()[0] == "AntiCovidAgent":
        user_ids.append(user_id)
        # Create a new onboarding tutorial.
        onboarding_tutorial = OnboardingTutorial(channel_id)

        # Get the onboarding message payload
        message = onboarding_tutorial.get_message_payload()
        message["text"] = "Olá, estou aqui para responder a questões sobre o COVID-19. Toda a informação que tenho provém de fontes oficiais e/ou jornais nacionais."

        # Post the onboarding message in Slack
        response = slack_web_client.chat_postMessage(**message)

        # Capture the timestamp of the message we've just posted so
        # we can use it to update the message after a user
        # has completed an onboarding task.
        onboarding_tutorial.timestamp = response["ts"]

        # Store the message sent in onboarding_tutorials_sent
        if channel_id not in onboarding_tutorials_sent:
            onboarding_tutorials_sent[channel_id] = {}
        onboarding_tutorials_sent[channel_id][user_id] = onboarding_tutorial

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on("message")
def message(payload):

    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    event = payload.get("event", {})


    channel_id = event.get("channel")
    user_id = event.get("user")
    msg_id = event.get("client_msg_id")
    text = event.get("text")
    if user_id != 'UURCF5K7D' and not msg_id in received_messages_id:

        print("receiving message: " + text + " user id " + user_id)
        # avoid repetaed messages
        received_messages_id.append(msg_id)

        response(user_id, channel_id, text)

        #if text and text.lower() == "start":
            #return start_onboarding(user_id, channel_id)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    firstCall = True
    app.run(port=8080)
