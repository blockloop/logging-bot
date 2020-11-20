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

## Secrets

This project contains an .envrc which is activated by
[direnv](https://direnv.net/), however, .envrc is encrypted with
[git-crypt](https://github.com/AGWA/git-crypt) because it contains some private
information. The file can be seamlessly used with git if you are a member of
the git-crypt allowed users.


### Adding a user to git-crypt:

  1. Only users who have a GPG key already in the repository can add new users
  1. Make sure you have the `USER_ID` installed locally either by having the
     requesting user push their public key to a public keyserver (such as
     keys.gnupg.net) and pulling it from the keyserver or by having the
     requesting user send you their gpg public key.
  1. `git-crypt add-gpg-user <USER_ID>`
     * Note: `USER_ID` can be a key ID, a full fingerprint, an email address,
       anything else that uniquely identifies a public key to GPG (see "HOW TO
       SPECIFY A USER ID" in the gpg man page). Note: git-crypt add-gpg-user
       will add and commit a GPG-encrypted key file in the .git-crypt
       directory of the root of your repository.
  1. `git push`


### Decrypting:
  1. install git-crypt (`dnf install git-crypt` or see the installation instructions)
  1. Ask to be added by an existing member
  1. git crypt unlock
  1. Now the .envrc file will be seamlessly encrypted/decrypted.
