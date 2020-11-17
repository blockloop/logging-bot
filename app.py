import os
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from onboarding_tutorial import OnboardingTutorial

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)

trigger_words = (os.environ["ONBOARD_TRIGGER_WORDS"] or "").split(",")
ignore_users = (os.environ["ONBOARD_IGNORE_USERS"] or "").split(",")

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

def start_onboarding(user_id: str, channel: str, thread_ts="", ephemeral=False):
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload(thread_ts, user=user_id)

    # Post the onboarding message in Slack
    if ephemeral:
        slack_web_client.chat_postEphemeral(**message)
    else:
        slack_web_client.chat_postMessage(**message)

# ================ Team Join Event =============== #
# When the user first joins a team, the type of the event will be 'team_join'.
# Here we'll link the onboarding_message callback to the 'team_join' event.
@slack_events_adapter.on("member_joined_channel")
def onboarding_message(payload):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    logging.debug("member_joined_channel")
    event = payload.get("event", {})
    channel = event.get("channel")

    # Get the id of the Slack user associated with the incoming event
    user_id = event.get("user")

    # Open a DM with the new user.
    # response = slack_web_client.im_open(user=user_id)
    # channel = response["channel"]["id"]

    # Post the onboarding message.
    start_onboarding(user_id, channel, ephemeral=True)



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
    text = event.get("text")
    # if thread_ts then this is already a thread, otherwise create a thread from the ts
    thread_ts = event.get("thread_ts") or event.get("ts")

    if event.get("bot_profile"):
        # this is a bot, probably myself. Ignore it
        logger.debug("ignoring bot message")
        return

    if not text:
        return
    text = text.lower()
    for trigger in trigger_words:
        if trigger in text:
            logger.debug("triggered word: '%s'. Text: '%s'", trigger, text)
            return start_onboarding(user_id, channel_id, thread_ts)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)
