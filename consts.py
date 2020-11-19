"""messages and other constants"""
import os


ONBOARD_MESSAGE = """
Welcome to Logging! :wave:

*PLEASE READ THE FAQ before asking any questions:* https://bit.ly/2IJSzNV

If your question is not answered in the FAQ feel free to tag @aoslogging or email us at team-logging@redhat.com with your question.
*Please provide as much detail as possible* with your question in a thread.
We will get back to you *as soon as possible*.
If you have not heard a response *within 6 hours* please reach out again by tagging @aoslogging in the thread

Thank you - The Logging Team
"""

AUTOREPLY_MESSAGE = """
Welcome to Logging! :wave:

*PLEASE READ THE FAQ:* https://bit.ly/2IJSzNV

If your question is not answered in the FAQ feel free to tag @aoslogging in this thread or email us at team-logging@redhat.com
If you want to *provide more information* please *add it to this thread*
We will get back to you *as soon as possible*. If you have not heard a response *within 6 hours* please reach out again by tagging @aoslogging in this thread

Thank you - The Logging Team
"""

FAQ_MESSAGE = "*LOGGING FAQ:* %s" % os.getenv("LOGGING_FAQ_URL", "https://bit.ly/2IJSzNV")

# Message Blocks
ONBOARD_BLOCK = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": ONBOARD_MESSAGE,
    },
}

AUTOREPLY_BLOCK = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": AUTOREPLY_MESSAGE,
    },
}

FAQ_BLOCK = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": FAQ_MESSAGE,
    },
}

DIVIDER_BLOCK = {"type": "divider"}

# list of commands that can be executed and their message responses
COMMANDS = {
    "!question": {
        "blocks": [AUTOREPLY_BLOCK]
    },
    "!faq": {
        "blocks": [FAQ_BLOCK]
    },
    "!ping": {
        "text": "pong",
    },
}
# add help commands
COMMANDS["!commands"] = {
    "text": "\n".join(COMMANDS.keys()),
}
COMMANDS["!help"] = {}
COMMANDS["!help"] = {
    "text": "\n".join(COMMANDS.keys()),
}
