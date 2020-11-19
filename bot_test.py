"""unit testing the app"""
import unittest
import logging
from unittest.mock import MagicMock
from slack_sdk.web import WebClient

import consts
from bot import LoggingBot


class AnyStringWith(str):
    def __eq__(self, other):
        return self in other

class HandleSubteamUpdate(unittest.TestCase):
    def test_only_updates_observed_teams(self):
        team = "myteam"
        user = "me"
        channel = "challen_abcd"

        tests = [
            ([], [], False),
            ([team], [], False),
            ([], [user], False),
            ([team], [user], True),
            ([team], [user, "user2"], True),
        ]

        client = WebClient()
        client.usergroups_users_list = MagicMock(return_value={"users": []})
        for observed_groups, new_users, should_update in tests:
            subject = LoggingBot(client, [], [channel], observed_groups, [], [])
            subject.handle_subteam_update(team, new_users)
            if should_update:
                self.assertEqual(new_users, subject.admin_groups[team])


    def test_only_updates_if_users_and_team_are_provided(self):
        team = "myteam"
        user = "me"
        channel = "challen_abcd"

        tests = [
            ("", [], False),
            (team, [], False),
            ("", [user], False),
            (team, [user], True),
        ]

        client = WebClient()
        client.usergroups_users_list = MagicMock(return_value={"users": []})
        for team, users, should_handle in tests:
            subject = LoggingBot(client, [], [channel], [team], [], [])
            handled = subject.handle_subteam_update(team, users)
            self.assertEqual(should_handle, handled, "Team=%s User=%s" % (team, user))


class HandleMessage(unittest.TestCase):
    def test_ignores_admin_messages(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()
        logging.debug = MagicMock()

        user = "me"
        trigger_word = "triggered!"
        channel = "channel_8"

        subject = LoggingBot(client, [trigger_word], [channel], [], [user], [])
        handled = subject.handle_message(channel, user, "text")
        self.assertFalse(handled)
        client.chat_postMessage.assert_not_called()
        logging.debug.assert_called_with(AnyStringWith("admin"))

    def test_ignores_bot_messages(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()
        logging.debug = MagicMock()

        subject = LoggingBot(client, [], [], [], [], [])
        handled = subject.handle_message("channel", "user", "text", bot_profile="bot_profile")
        self.assertFalse(handled)
        client.chat_postMessage.assert_not_called()
        logging.debug.assert_called_with(AnyStringWith("bot"))

    def test_ignores_unmonitored_channels(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        subject = LoggingBot(client, [], ["MONITORED"], [], [], [])
        handled = subject.handle_message("NOT_MONITORED", "user", "text", bot_profile="bot_profile")
        self.assertFalse(handled)
        client.chat_postMessage.assert_not_called()

    def test_executes_commands_in_threads(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        channel = "channel"
        subject = LoggingBot(client, [], [channel], [], [], [])

        # choose the first command
        cmd = list(consts.COMMANDS.keys())[0]
        user = "user"

        handled = subject.handle_message(channel, user, cmd, ts="ts", thread_ts="thread_ts")
        self.assertTrue(handled)

        # because we supplied a thread_ts to handle_message that indicates the
        # message was within an existing thread so we should see thread_ts
        # here.
        thread_ts = client.chat_postMessage.call_args.kwargs.get("thread_ts", "")
        self.assertEqual("thread_ts", thread_ts)

    def test_executes_commands_in_channels(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        channel = "channel"
        subject = LoggingBot(client, [], [channel], [], [], [])

        # choose the first command
        cmd = list(consts.COMMANDS.keys())[0]
        user = "user"

        handled = subject.handle_message(channel, user, cmd, ts="ts")
        self.assertTrue(handled)

        # because we did not supply a thread_ts to handle_message that
        # indicates the message was NOT within an existing thread so we should
        # not see a thread_ts (which means post in the original channel)
        thread_ts = client.chat_postMessage.call_args.kwargs.get("thread_ts")
        self.assertFalse(thread_ts)


    def test_triggers_trigger_words(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        user = "user"
        channel = "channel"
        trigger_words = ["help me"]

        for msg, should_handle in [("good morning", False), ("help", False), ("help me", True)]:
            subject = LoggingBot(client, trigger_words, [channel], [], [], [])

            handled = subject.handle_message(channel, user, msg, ts="ts")
            self.assertEqual(should_handle, handled, msg="Message=%s" % msg)

            if handled:
                self.assertEqual(user, client.chat_postMessage.call_args.kwargs.get("user"))

    def test_triggers_uses_threads(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        user = "user"
        channel = "channel"
        trigger_word = "help me"

        subject = LoggingBot(client, [trigger_word], [channel], [], [], [])

        handled = subject.handle_message(channel, user, trigger_word, ts="ts")
        self.assertEqual(True, handled)

        self.assertNotEqual("", client.chat_postMessage.call_args.kwargs.get("thread_ts", ""))


if __name__ == '__main__':
    unittest.main()
