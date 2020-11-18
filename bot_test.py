"""unit testing the app"""
import unittest
import logging
from unittest.mock import MagicMock
from slack_sdk.web import WebClient

import consts
from bot import LoggingBot, new_message


class AnyStringWith(str):
    def __eq__(self, other):
        return self in other

class HandleMessage(unittest.TestCase):
    def testIgnoresBotMessages(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()
        logging.debug = MagicMock()

        subject = LoggingBot(client, [], [], [], [])
        handled = subject.handle_message("channel", "user", "text", bot_profile="bot_profile")
        self.assertFalse(handled)
        client.chat_postMessage.assert_not_called()
        logging.debug.assert_called_with(AnyStringWith("bot"))

    def testIgnoresUnmonitoredChannels(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        subject = LoggingBot(client, [], ["MONITORED"], [], [])
        handled = subject.handle_message("NOT_MONITORED", "user", "text", bot_profile="bot_profile")
        self.assertFalse(handled)
        client.chat_postMessage.assert_not_called()

    def testExecutesCommandsInThreads(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        channel = "channel"
        subject = LoggingBot(client, [], [channel], [], [])

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

    def testExecutesCommandsInChannels(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        channel = "channel"
        subject = LoggingBot(client, [], [channel], [], [])

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


    def testTriggers(self):
        client = WebClient()
        client.chat_postMessage = MagicMock()

        user = "user"
        channel = "channel"
        trigger_words = ["help me"]

        for msg, should_handle in [("good morning", False), ("help", False), ("help me", True)]:
            subject = LoggingBot(client, trigger_words, [channel], [], [])

            handled = subject.handle_message(channel, user, msg, ts="ts")
            self.assertEqual(should_handle, handled, msg="Message=%s" % msg)

            if handled:
                self.assertEqual(user, client.chat_postMessage.call_args.kwargs.get("user"))


if __name__ == '__main__':
    unittest.main()
