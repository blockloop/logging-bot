import logging
from typing import Set
from slack_sdk.errors import SlackApiError
import consts


def new_message(channel: str, user: str, thread_ts="", **kwargs):
    msg = {
        "channel": channel,
        "username": user,
        "icon_emoji": ":robot_face:",
        "user": user,
        "thread_ts": thread_ts,
    }
    msg.update(kwargs)
    return msg


class LoggingBot():
    """Logging bot auto replies to logging messages"""
    slack_client = None
    trigger_words = set()
    channels = set()
    admin_groups = {}
    onboard_users = set()

    def __init__(self, slack_client, trigger_words: Set[str], channels: Set[str],
                 admin_groups: Set[str], admin_users: Set[str], ignored_users: Set[str]):
        self.slack_client = slack_client
        self.trigger_words = trigger_words
        self.channels = channels
        self.ignored_users = ignored_users
        # add admin_users to a separate group that will not get updated
        self.admin_groups["NONE"] = admin_users

        # loop through the configured groups and get a list of users in those groups
        # so we can cache the admin users
        for group in admin_groups:
            if not group:
                continue
            try:
                users = slack_client.usergroups_users_list(usergroup=group).get("users", [])
                self.admin_groups[group] = users
            except SlackApiError as err:
                logging.error("failed to list users for group '%s': Error: '%s'",
                              group, err.response["error"])

    # pylint: disable=invalid-name # ts is the name of the field slack sends
    def handle_message(self, channel: str, user: str, text: str,
                       ts="", thread_ts="", bot_profile="", **kwargs) -> bool:
        """handle a new message"""
        if bot_profile:
            # this is a bot, possibly myself. Ignore it
            logging.debug("ignoring bot message")
            return False

        if channel not in self.channels:
            logging.debug("ignoring message in unmonitored (%s channel)", channel)
            return False

        if not text:
            return False
        text = text.lower()

        if text in consts.COMMANDS:
            # use thread_ts because if this message is in a main channel you
            # don't want a thread started on that command. If, however, this
            # command was executed in a thread you want it to be executed in
            # the thread
            self.execute_command(text, user, channel, thread_ts)
            return True

        if self.is_admin(user):
            logging.debug("ignoring admin message")
            return False

        for trigger in self.trigger_words:
            if trigger in text:
                logging.debug("triggered word=%s message=%s user=%s", trigger, text, user)
                # if thread_ts then this is already a thread, otherwise create a new thread
                # using the ts of the message
                self.inform_user(user, channel, thread_ts or ts)
                return True
        return False

    def handle_subteam_update(self, subteam_id: str, users: Set[str], **kwargs):
        """update the admin users list when an admin_group is updated"""
        if not subteam_id or not users:
            return False
        if subteam_id in self.admin_groups:
            logging.debug("subteam_updated subteam=%s", subteam_id)
            self.admin_groups[subteam_id] = users
            return True
        return False

    def onboard_user(self, user: str, channel: str, **kwargs):
        """Send a onboard message to a user in the correct context"""
        message = new_message(channel, user, blocks=[consts.ONBOARD_BLOCK])
        # Post the onboarding message in Slack
        self.slack_client.chat_postEphemeral(**message)

    def inform_user(self, user: str, channel: str, thread_ts: str):
        """Send a informational message to a user in the correct context"""
        message = new_message(channel, user, thread_ts=thread_ts, blocks=[consts.AUTOREPLY_BLOCK])
        return self.slack_client.chat_postMessage(**message)

    def execute_command(self, cmd: str, user: str, channel: str, thread_ts=""):
        """send a command result to slack"""
        if cmd not in consts.COMMANDS:
            logging.error("unknown command '%s' from user '%s'", cmd, user)
            return None
        logging.debug("triggered command: user=%s, cmd=%s", user, cmd)
        message = new_message(channel, user, thread_ts)
        message.update(consts.COMMANDS[cmd])
        return self.slack_client.chat_postMessage(**message)

    def is_admin(self, user: str) -> bool:
        """check if a user is an admin"""
        for users in self.admin_groups.values():
            if user in users:
                return True
        return False
