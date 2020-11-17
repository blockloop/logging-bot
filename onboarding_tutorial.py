class OnboardingTutorial:
    """Constructs the onboarding message and stores the state of which tasks were completed."""

    WELCOME_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Welcome to Logging! :wave:\n\n"
                "*PLEASE READ THE FAQ: * https://bit.ly/2IJSzNV\n\n"
                "If your question is not answered in the FAQ feel free to tag @aoslogging "
                "in this thread or email us at team-logging@redhat.com\n\n"
                "If you want to *provide more information* please *say it in this thread* "
                "We will get back to you *as soon as possible*. If you have not heard a response "
                "*within 6 hours* please reach out again by tagging @aoslogging in this thread\n\n"
                "Thank you\n\n  - The Logging Team"
            ),
        },
    }
    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel):
        self.channel = channel
        self.username = "Logging Bot"
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""

    def get_message_payload(self, thread_ts: str, user: str):
        res = {
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "timestamp": self.timestamp,
            "blocks": [
                self.WELCOME_BLOCK,
            ],
        }

        if thread_ts:
            res["thread_ts"] = thread_ts
        if user:
            res["user"] = user

        return res

    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]
