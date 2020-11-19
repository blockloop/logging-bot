"""
Logging Bot is used in slack for logging team public channels
"""
import os
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from prometheus_flask_exporter import PrometheusMetrics
import config
from bot import LoggingBot

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
metrics = PrometheusMetrics(app)
slack_events_adapter = SlackEventAdapter(config.SlackSigningSecret, "/slack/events", app)

# Initialize a Web API client
slack_client = WebClient(token=config.SlackBotToken)
# send a test message to make sure we can access what we need
slack_client.api_test()

bot = LoggingBot(slack_client, config.TriggerWords, config.OnboardChannels,
                 config.AdminGroups, config.AdminUsers, config.OnboardIgnoredUsers)


@app.route("/ping")
def ping():
    return 'PONG'


# ================ Member Joined Channel Event =============== #
# When a user first joins a channel that the bot is watching.
# We want to provide users joining channels with an ephemeral
# welcome message. The ephemeral message is only visible to
# the user to whom it is directed.
@slack_events_adapter.on("member_joined_channel")
def onboarding_message(payload):
    """Create and send an onboarding message to new users.
    """
    logging.debug("member_joined_channel")
    event = payload.get("event", {})
    bot.onboard_user(**event)


@slack_events_adapter.on("message")
def on_message(payload):
    """This event is handled any time a message is posted to any channel
    that this bot is monitoring.

    CAVEATS:
      1. This also receives events created by other bots and itself
         so it's possible to get into a loop if you don't capture "bot_profile"
         and exit.
      2. This will trigger for all messages in any channel Logging Bot is in.
         If the bot is inadvertently added to a channel it will react to trigger
         words in that channel. To avoid any confusion we use the ONBOARD_CHANNELS
         env var to limit the scope of the bot.
    """
    event = payload.get("event", {})
    if "subtype" in event:
        # message subtypes aren't used. See more here:
        # https://api.slack.com/events/message#message-event-type__message-subtypes
        return
    bot.handle_message(**event)


if __name__ == "__main__":
    LEVEL = logging.ERROR
    if os.getenv("FLASK_ENV", "") == "development":
        LEVEL = logging.DEBUG
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=LEVEL,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler()],
    )
    app.run(port=3000, threaded=True)
