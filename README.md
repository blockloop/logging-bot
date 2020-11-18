# Logging Bot

This is Logging Bot. You can interact with Logging Bot in #forum-logging.

## Developing

Logging Bot is written in python and uses virtualenv. Everything that is needed
for development is under [venv](venv) directory. To write code you need to
activate virtual env in your shell by executing `source ./venv/bin/activate`.
When you are finished with development you can either close the tty or execute
`deactivate`.

Source code uses the [Python Slack SDK](https://github.com/slackapi/python-slack-sdk/). Events are handled with decorators provided
by the SDK.

