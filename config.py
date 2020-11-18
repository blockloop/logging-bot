"""application configuration"""

import os

# REQUIRED variables
SlackSigningSecret = os.environ["SLACK_SIGNING_SECRET"]
SlackBotToken = os.environ["SLACK_BOT_TOKEN"]


# OPTIONAL variables

# list of words that will trigger the onboarding response.
TriggerWords = set(
    # Filter out empty strings
    w.strip() for w in os.getenv("ONBOARD_TRIGGER_WORDS", "").split(",") if w
)

# users who should not trigger responses
IgnoredUsers = set(
    # filter out empty strings
    u.strip() for u in os.getenv("ONBOARD_IGNORE_USERS", "").split(",") if u
)

OnboardAdminGroups = set(
    g.strip() for g in os.getenv("ONBOARD_ADMIN_GROUPS", "").split(",") if g
)

# channels to watch for onboarding
OnboardChannels = set(
    c.strip() for c in os.getenv("ONBOARD_CHANNELS", "").split(",") if c
)
