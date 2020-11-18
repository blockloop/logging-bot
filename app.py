"""
Logging Bot is used in slack for logging team public channels
"""
import logging
from flask import Flask
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
import consts
import config

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(config.SlackSigningSecret, "/slack/events", app)

# Initialize a Web API client
slack_client = WebClient(token=config.SlackBotToken)
# send a test message to make sure we can access what we need
slack_client.api_test()


# list of admin subgroups that should be considered bot admins
admin_groups = {}
# loop through the configured groups and get a list of users in those groups
# so we can cache the admin users
for group in config.OnboardAdminGroups:
    group = group.strip()
    if not group:  # exclude empty strings
        continue
    try:
        response = slack_client.usergroups_users_list(usergroup=group)
        admin_groups[group] = response.get("users", [])
    except SlackApiError as err:
        logging.error("failed to list users for group '%s': Error: '%s'",
                      group, err.response["error"])

# list of commands that can be executed and their message responses
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
# add help commands
commands["!commands"] = {
    "text": "\n".join(commands.keys()),
}
commands["!help"] = {
    "text": "\n".join(commands.keys()),
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
        slack_client.chat_postEphemeral(**message)
    else:
        slack_client.chat_postMessage(**message)


def execute_command(cmd: str, user: str, channel: str, thread_ts=""):
    """send a command result to slack"""
    if cmd not in commands:
        logging.error("unknown command '%s' from user '%s'", cmd, user)
        return None

    logging.debug("triggered command: user='%s', cmd='%s'", user, cmd)
    message = {
        "channel": channel,
        "username": user,
        "icon_emoji": ":robot_face:",
        "user": user,
        "thread_ts": thread_ts,
    }

    message.update(commands[cmd])

    return slack_client.chat_postMessage(**message)


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
    # response = slack_client.im_open(user=user)
    # channel = response["channel"]["id"]

    # Post the onboarding message.
    onboard_user(user, channel, ephemeral=True)


# ============== Message Events ============= #
# This event is handled any time a message is posted to any channel
# that this bot is monitoring.
#
# CAVEATS:
#   1. This also receives events created by other bots and itself
#      so it's possible to get into a loop if you don't capture "bot_profile"
#      and exit.
#   2. This will trigger for all messages in any channel Logging Bot is in.
#      If the bot is inadvertently added to a channel it will react to trigger
#      words in that channel. To avoid any confusion we use the ONBOARD_CHANNELS
#      env var to limit the scope of the bot.
@slack_events_adapter.on("message")
def on_message(payload):
    """Display the onboarding welcome message after receiving a triggering message
    """
    event = payload.get("event", {})

    channel = event.get("channel")

    if channel not in config.OnboardChannels:
        logging.debug("ignoring message in unmonitored (%s channel)", channel)
        return None

    user = event.get("user")
    text = event.get("text")

    if event.get("bot_profile"):
        # this is a bot, possibly myself. Ignore it
        logging.debug("ignoring bot message")
        return None

    if not text:
        return None
    text = text.lower()

    if text.lower() in commands:
        # don't use ts here because if the admin executes this command
        # in the main channel you don't want it to be started in a thread.
        # If, however, this command was executed in a thread you want it
        # to be executed in the thread
        return execute_command(text.lower(), user, channel, event.get("thread_ts"))

    for trigger in config.TriggerWords:
        if trigger in text:
            # if thread_ts then this is already a thread, otherwise create a new thread
            # using the ts of the message
            thread_ts = event.get("thread_ts") or event.get("ts")
            logging.debug("triggered word: '%s'. Text: '%s'", trigger, text)
            return onboard_user(user, channel, thread_ts)

    return None


# ============== Subteam Updated Events ============= #
# This event is triggered when a subteam has been updated. We capture this
# to update the admin users if an admin group has changed
@slack_events_adapter.on("subteam_updated")
def on_subteam_updated(payload):
    """update the admin users list when an admin_group is updated"""
    subteam = payload.get("subteam")
    team = subteam.get("id")

    logging.debug("subteam_updated", team=team)

    new_users = subteam.get("users")

    if new_users and team in admin_groups:
        admin_groups[team].users = new_users
        return


def is_admin(user: str) -> bool:
    """check if a user is an admin"""
    for _, users in admin_groups.items():
        if user in users:
            return True
    return False


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler()],
    )
    app.run(port=3000)
