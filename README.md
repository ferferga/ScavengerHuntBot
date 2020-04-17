# Scavenger Hunt Bot
Organize Scavenger Hunts like a pro using Telegram

--------------------------------------------

*Scavenger Hunts* are a kind of competition where groups or individual contestants race for finding "a treasure" or any sort of
prize. These competitions usually take place in big cities and with a lot of participants that walk around big zones, so managing all of that is usually very difficult for the organizers (trust me, I did one). This userbot for Telegram is aimed at helping you organize any kind of
competition and Scavenger Hunt.

It can keep an updated ranking (with the points that every contestant has) in a channel/group or supergroup (so all the participants can check at a glance their position
while the competition is in progress) and give hints or challenges automatically (with a precise granularity and control) to each participant
while they're progressing through the different challenges, based in a set of rules you can specify beforehand.

This project was made with real-life competitions in mind, some of them which take place in big cities, so it might not be that suitable for
online competitions in Telegram or in other platforms, as probably better alternatives exist.

## Quick Start and Simple Walkthrough

*This bot requires you to sign in to Telegram like any user (with a phone number). It's not a bot that uses the [Telegram's Bot API](https://core.telegram.org/bots).*

* Specify your api_id/api_hash keys in ``config.json`` (see ["Obtaining api_id"](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id))

* Login into the bot

* Open a Telegram Chat with the account used for logging in. Send a message. The bot will return your *User ID*. Stop the bot (CTRL + C) in the terminal
and put your *User ID* in the ``root_user`` key of the ``config.json`` file:

<p align="center">
  <img src="https://github.com/ferferga/ScavengerHuntBot/raw/master/images/get-userid.gif">
</p>

*(This bot is controlled using commands like ``!help`` or ``.h`` (which is the shortcut version of ``!help``) directly
in a Telegram chat. Use ``!help`` or ``.h`` whenever you need help)*

* Create a group (a channel might work as well). Make the userbot admin. Send ``!leaderboards``. The leaderboards will appear and the bot is ready
to accept new contestants.

* Tell the people that will participate in the Scavenger to talk to the bot **(this is always required after starting or restarting the bot for avoiding spam)**. Add them to the group as well, so they can visualize the leaderboards.

* The userbot will send to you the User ID (it will also be logged to bot's Saved Messages) of each user who talked to the bot.

* Add the user to the Scavenger Hunt:

- FROM YOUR PERSONAL ACCOUNT: Go to your chat with the bot and send ``!add UserID.'Alice & Bob'`` or ``.a UserID.'Alice & Bob'``
- FROM THE USERBOT ACCOUNT: Go to the chat with the contestant you want to add and send ``!add Alice & Bob`` or ``.a Alice & Bob``

*(You can control the bot using your personal account or the bot itself at any given time. More on that in **Detailed Walkthrough**)*

* (OPTIONAL) Once every contestant is added to the Scavenger Hunt, close the Scavenger, so people who are not participating
can send you messages without annoyances (otherwise you would receive a lot of ``A new user was recognised`` messages).

- FROM YOUR PERSONAL ACCOUNT: In your chat with the bot: ``!close`` or ``.c``
- FROM THE USERBOT ACCOUNT: In the chat with your personal account or in *Saved Messages*: ``!close`` or ``.c``.

* Give/Remove points to the contestant:

- FROM YOUR PERSONAL ACCOUNT: In your chat with the bot: ``!prom ContestantID.5`` or ``.p ContestantID.5`` (adds 5 points)
- FROM THE USERBOT ACCOUNT: In the chat with the contestant: ``!prom -5`` or ``.p -5`` (substracts 5 points. More on that in **Detailed Walkthrough**)

#### Overview of the process using your personal account
*(Top left: Contestant (Francisco de Goya); Top Right: Personal Account (ferferga); Bottom: Userbot (Diego Velázquez))*

<p align="center">
  <img src="https://github.com/ferferga/ScavengerHuntBot/raw/master/images/personal-walkthrough.webp">
</p>

#### Overview of the process using the userbot account

<p align="center">
  <img src="https://github.com/ferferga/ScavengerHuntBot/raw/master/images/userbot-walkthrough.webp">
</p>

#### Or combine both!

<p align="center">
  <img src="https://github.com/ferferga/ScavengerHuntBot/raw/master/images/combined-walkthrough.webp">
</p>

## Glossary

As this bot is pretty modular and configurable, is a good idea to have some concepts explained before going ahead:

* Root User: An external user that will be able to issue commands to the bot, just as the bot itself. We've been calling this **Personal account** until now.
* Contestant: A telegram user who is registered in the bot and is taking part in the Scavenger.
* Contestant ID: The internal ID that the bot uses for identifying an specific contestant
* User ID: The internal ID that Telegram Messenger uses to identify an user.
* Hint: A message that is sent to a contestant when certain conditions are met.
* Alias: The name that will be shown in the leaderboards for an specific contestant. You can use the contestant's name.
* User (aka *recognised user*): A telegram user that talked to the bot but hasn't been added to the Scavenger.

### Modes
They are configured in the ``root_user`` key in ``config.json``. *See **Configuration values** below*

* Setup mode: In this mode, the bot will reply to every message received with the UserID of the person who sent it.
* In-chat mode: In this mode, the bot won't have any ``Root User`` in particular, so the bot **can only be controlled using the
userbot's account**.

Setting the ``root_user`` key to a valid User ID will make the bot controllable through
the **userbot's account** and the **Root user's account**.

## Configuration values

| Key                 | Description                                                                                                                                         | Allowed Values and Datatypes                                                                   | Default                                                                                     |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| ``random``          | **Ignore the points** values in the hints and give a random hint to the user **everytime** *any* amount of points is given. Hints won't be repeated | ``true`` or ``false``                                                                          | ``false``                                                                                   |
| ``debug``           | Send more messages to your rootentity aside from the errors (when one user receives points, when one user is added, etc)                            | ``true`` or ``false``                                                                          | ``false``                                                                                   |
| ``api_id``          | Telegram's API ID                                                                                                                                   | ``Any positive integer``                                                                       | ``0``                                                                                       |
| ``api_hash``        | Telegram's API Hash                                                                                                                                 | ``String``                                                                                     | ``""``                                                                                      |
| ``root_user``       | The ID of the external user do you want to use for controlling the bot.                                                                             | ``-2`` for **Setup mode**, ``-1`` for **in-chat mode only** and ``Any valid Telegram User ID`` | ``-2``                                                                                      |
| ``header_message``  | The header message that will be used for the leaderboards message                                                                                   | ``String``                                                                                     | ``"**My Scavenger Hunt**\n\n📶 __Leaderboards__:\n\n"``                                      |
| ``point_message``   | The message that will be sent privately to the contestant after earning points                                                                      | ``String`` or ``null``                                                                         | ``"You were given {0} coins in the last challenge"``                                        |
| ``position_line``   | Format of each of the leaderboard's lines. {0} is the position of contestant, {1} the name of the group, {2} the points that the contestant has     | ``String``                                                                                     | ``"**{0}º** - **{1}**: {2} coins"``                                                         |
| ``welcome_message`` | The message that will be sent to the users after being recognised by the bot                                                                        | ``String``                                                                                     | ``"Information received by the organizer of the Scavenger Hunt. Wait for instructions..."`` |

You can use [Telegram's markdown](https://sourceforge.net/p/telegram/wiki/markdown_syntax/) for the following keys:

* ``header_message``
* ``point_message``
* ``position_line``
* ``welcome_message``

## Setting up the hints

For information in how to configure the hints, [check here](https://github.com/ferferga/ScavengerHuntBot/blob/master/HINTS.md)

## Going into the details

### Tips

* You can only have **one** ``RootUser``. However, you can use commands directly in the userbot's account
(as demonstrated in the *Quick Walkthrough*) and, with the cloud's capabilities of Telegram, is also possible to share accounts easily
with other people, so you can have as many "organizers" as you wish for your competition.

* A detailed explanation of every command is in the ``!help`` command. I suggest you to run
it as soon as you have the bot up and running for getting familiar with the commands

* Every time a command is sent from the userbot account, the message containing the command will be deleted (as seen is the images),
so chats with contestants and the leaderboard's group is kept uncluttered.
The same thing applies when you issue a command where it's not allowed. Run ``!help`` to know where you
can issue each command

## Download

I've built binaries for **Windows** and **Linux** for 64 bits, which can be found in the [Releases tab](https://github.com/ferferga/ScavengerHuntBot/releases)

For other architectures and systems, the general procedure to run this is to download Python > 3.6, clone this repository
and install the requirements. One-line:

``sudo apt install -y python3 python3-pip && git clone https://github.com/ferferga/ScavengerHuntBot && cd ScavengerHuntBot && pip3 install -r requirements.txt``

**Make sure you don't forget to ["Get your api_id and api_hash from Telegram"](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id)) and specify it in ``config.json``**

## License

This is licensed as AGPL3, so all the derivatives from this work must be open source as well. Any contribution is welcome!
