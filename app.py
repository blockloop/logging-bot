"""
Logging Bot is used in slack for logging team public channels
"""
import os
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
import consts

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

trigger_words = set(
    # filter out empty strings
    word.strip() for word in os.getenv("ONBOARD_TRIGGER_WORDS", "").split(",") if word
)
ignored_users = set(
    # filter out empty strings
    user.strip() for user in os.getenv("ONBOARD_IGNORE_USERS", "").split(",") if user
)

admin_groups = {}
for group in os.getenv("ONBOARD_ADMIN_GROUPS", "").split(","):
    group = group.strip()
    if not group:  # exclude empty strings
        continue
    try:
        response = slack_web_client.usergroups_users_list(usergroup=group)
        admin_groups[group] = response.get("users", [])
    except SlackApiError as err:
        logging.error("failed to list users for group '%s': Error: '%s'", group, err.response["error"])

commands = {
    "!welcome": {
        "blocks": [consts.WELCOME_BLOCK]
    },
    "!onboard": {
        "blocks": [consts.WELCOME_BLOCK]
    },
    "!faq": {
        "blocks": [consts.FAQ_BLOCK]
    },
}


def onboard_user(user: str, channel: str, thread_ts="", ephemeral=False):
    """Send a welcome message to a user in the correct context"""
    message = {
        "channel": channel,
        "username": user,
        "icon_emoji": ":robot_face:",
        "user": user,
        "thread_ts": thread_ts,
        "blocks": [
            consts.WELCOME_BLOCK,
        ],
    }

    # Post the onboarding message in Slack
    if ephemeral:
        slack_web_client.chat_postEphemeral(**message)
    else:
        slack_web_client.chat_postMessage(**message)


def execute_command(cmd: str, user: str, channel: str, thread_ts=""):
    """send a command result to slack"""
    if cmd not in commands:
        logging.error("unknown command '%s' from user '%s'", cmd, user)
        return None

    logger.debug("triggered command: user='%s', cmd='%s'", user, cmd)
    message = {
        "channel": channel,
        "username": user,
        "icon_emoji": ":robot_face:",
        "user": user,
        "thread_ts": thread_ts,
    }

    message.update(commands[cmd])

    return slack_web_client.chat_postMessage(**message)


# ================ Member Joined Channel Event =============== #
# When a user first joins a channel that the bot is watching.
# We want to provide users joining channels with an ephemeral
# welcome message. The ephemeral message is only visible to
# the user to whom it is directed.
@slack_events_adapter.on("member_joined_channel")
def onboarding_message(payload):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    logging.debug("member_joined_channel")
    event = payload.get("event", {})
    channel = event.get("channel")

    # Get the id of the Slack user associated with the incoming event
    user = event.get("user")

    # Open a DM with the new user.
    # response = slack_web_client.im_open(user=user)
    # channel = response["channel"]["id"]

    # Post the onboarding message.
    onboard_user(user, channel, ephemeral=True)


# ============== Message Events ============= #
# This event is handled any time a message is posted to any channel
# that this bot is monitoring.
#
# CAVEAT: this also receives events created by other bots and itself
# so it's possible to get into a loop if you don't capture "bot_profile"
# and exit.
@slack_events_adapter.on("message")
def on_message(payload):
    """Display the onboarding welcome message after receiving a triggering message
    """
    event = payload.get("event", {})

    channel_id = event.get("channel")
    user = event.get("user")
    text = event.get("text")

    if event.get("bot_profile"):
        # this is a bot, possibly myself. Ignore it
        logger.debug("ignoring bot message")
        return None

    if not text:
        return None
    text = text.lower()

    if text.lower() in commands:
        # don't use ts here because if the admin executes this command
        # in the main channel you don't want it to be started in a thread.
        # If, however, this command was executed in a thread you want it
        # to be executed in the thread
        return execute_command(text.lower(), user, channel_id, event.get("thread_ts"))

    for trigger in trigger_words:
        if trigger in text:
            # if thread_ts then this is already a thread, otherwise create a new thread
            # using the ts of the message
            thread_ts = event.get("thread_ts") or event.get("ts")
            logger.debug("triggered word: '%s'. Text: '%s'", trigger, text)
            return onboard_user(user, channel_id, thread_ts)

    return None


# ============== Subteam Updated Events ============= #
# This event is triggered when a subteam has been updated. We capture this
# to update the admin users if an admin group has changed
@slack_events_adapter.on("subteam_updated")
def on_subteam_updated(payload):
    """update the admin users list when an admin_group is updated"""
    subteam = payload.get("subteam")
    team = subteam.get("id")

    logger.debug("subteam_updated", team=team)

    new_users = subteam.get("users")

    if team in admin_groups:
        admin_groups[team].users = new_users
        return


def is_admin(user: str) -> bool:
    """check if a user is an admin"""
    for _, users in admin_groups.items():
        if user in users:
            return True
    return False


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    app.run(port=3000)
