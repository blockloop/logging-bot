"""messages and other constants"""
import os

WELCOME_MESSAGE = """
Welcome to Logging! :wave:

*PLEASE READ THE FAQ:* https://bit.ly/2IJSzNV

If your question is not answered in the FAQ feel free to tag @aoslogging in this thread or email us at team-logging@redhat.com
If you want to *provide more information* please *add it to this thread*
We will get back to you *as soon as possible*. If you have not heard a response *within 6 hours* please reach out again by tagging @aoslogging in this thread

Thank you - The Logging Team
"""

FAQ_MESSAGE = "*LOGGING FAQ:* %s" % os.getenv("LOGGING_FAQ_URL", "https://bit.ly/2IJSzNV")

# Message Blocks
WELCOME_BLOCK = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": WELCOME_MESSAGE,
    },
}

# Message Blocks
FAQ_BLOCK = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": FAQ_MESSAGE,
    },
}

DIVIDER_BLOCK = {"type": "divider"}

