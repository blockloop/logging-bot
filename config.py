"""application configuration"""

import os
from typing import Set


def csv_env_var(var: str) -> Set[str]:
    # Filter out empty strings
    return set(w.strip() for w in os.getenv(var, "").split(",") if w)


# ==================== REQUIRED variables ==================== #
SlackSigningSecret = os.environ["SLACK_SIGNING_SECRET"]
SlackBotToken = os.environ["SLACK_BOT_TOKEN"]


# ==================== OPTIONAL variables ==================== #
# list of words that will trigger the onboarding response.
TriggerWords = csv_env_var("ONBOARD_TRIGGER_WORDS")
# users who should not trigger responses
OnboardIgnoredUsers = csv_env_var("ONBOARD_IGNORE_USERS")

# Subgroups that contain users which are admins
AdminGroups = csv_env_var("ADMIN_GROUPS")
AdminGroups.add("SGXV9CT42")  # @aoslogging

# Users to be considered admins
AdminUsers = csv_env_var("ADMIN_USERS")
AdminUsers.add("U0130B5DQPL")  # @BrettJones

# Channels to watch for onboarding
OnboardChannels = csv_env_var("ONBOARD_CHANNELS")
