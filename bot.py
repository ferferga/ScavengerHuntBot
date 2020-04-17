#!/usr/bin/python3
from telethon import TelegramClient, sync, events
from telethon.errors import *
from telethon.tl.functions.messages import *
from telethon.tl.custom import *
from telethon.tl.types import *
from telethon.utils import *
from telethon.sessions import *
from sys import exit
from operator import itemgetter
from time import sleep
from getpass import getpass
import json
import random

# Variable declaration
api_id = None
api_hash = None
rootuser = None
rootentity = None
botentity = None
trackedchannel = None
editablemsg = None
closed = False
alreadyRecognised = []
alreadyAdded = {}
contestants = []
#JSON-parsed values
point_hints = {}
hints = []
random = False
debug = True
welcomemsg = None
pointmsg = None
header = None
position_line = None

## JSON loading and client initialization

class InvalidJSONData(Exception):
    pass

try:
    with open("config.json", 'r', encoding="utf-8") as f:
        config = json.load(f)
    if not isinstance(config['hints'], list):
        raise InvalidJSONData
    for key, hint in enumerate(config['hints']):
        try:
            if hint['text'] is None and hint['group_message'] is None:
                print("The hint at position " + str(key) + " has the 'text' and the 'group_message' set to 'null', which makes no sense")
                raise InvalidJSONData
            if (isinstance(hint['points'], int) or hint['points'] is None) and (isinstance(hint['text'], str) or hint['text'] is None) and \
                (isinstance(hint['group_message'], str) or hint['group_message'] is None) and \
                    (isinstance(hint['even_contestant'], bool) or hint['even_contestant'] is None) and \
                        (isinstance(hint['even_position'], bool) or hint['even_position'] is None):
                hints.append([hint['text'], hint['group_message'],
                              hint['even_contestant'], hint['even_position']])
                point_hints[hints.index(hints[-1])] = hint['points']
            else:
                raise InvalidJSONData
        except KeyError:
            raise InvalidJSONData
    random = config['random']
    debug = config['debug']
    if not isinstance(random, bool) or not isinstance(debug, bool):
        raise InvalidJSONData
    rootuser = config['root_user']
    api_id = config['api_id']
    if not isinstance(rootuser, int) or not isinstance(api_id, int):
        raise InvalidJSONData
    api_hash = config['api_hash']
    header = config['header_message']
    welcomemsg = config['welcome_message']
    if not isinstance(api_hash, str) or not isinstance(header, str) or not isinstance(welcomemsg, str):
        raise InvalidJSONData
    pointmsg = config['point_message']
    if pointmsg is None or not isinstance(pointmsg, str):
        raise InvalidJSONData
    position_line = config['position_line']
    if not isinstance(position_line, str):
        raise InvalidJSONData
    del config
    print("Config from JSON loaded correctly!\n\n")
except InvalidJSONData:
    getpass("The JSON data includes some variables in an incorrect format. Check documentation before proceeding and press ENTER to exit.")
    exit(1)
except:
    getpass("JSON data is malformed. Check the documentation for more information. Press ENTER to exit.")
    exit(1)

try:
    client = TelegramClient('telegram-session', api_id, api_hash)
except ValueError:
    getpass("\nAttempted to connect to Telegram, but the api_id and api_hash keys are invalid. Exiting...")
    exit(1)
except Exception as e:
    getpass("There was an error while initializing the TelegramClient: " + str(e))
    exit(1)

## Functions

def sortArray():
    global contestants
    return sorted(contestants, key=itemgetter(2), reverse=True)

def getContestantPosition(contestant):
    return sortArray().index(contestant)+1
    
def is_even(number):
    if number%2 == 0:
        return True
    else:
        return False

def is_channel(inputentity):
    if isinstance(inputentity, InputPeerChat) or isinstance(inputentity, InputPeerChannel):
        return True
    else:
        return False

async def sendhint(hint, user_id, contestant):
    if hint[0] is not None:
        await client.send_message(user_id, hint[0])
    if hint[1] is not None:
        await client.send_message(trackedchannel, hint[1].replace("{0}", contestant[1]))
    return

async def sendInformationMessage(message):
    global rootuser, botentity, debug
    try:
        if rootuser > 0 and debug:
            await client.send_message(botentity, message)
            await client.send_message(rootentity, message)
        elif rootuser > 0:
            await client.send_message(rootentity, message)
        elif rootuser <= -1:
            await client.send_message(botentity, message)
    except Exception as e:
        print("Couldn't send debug messages: " + str(e))
    return
        
async def updateMessage():
    global editablemsg, header, trackedchannel, rootentity, position_line
    contestantlist = ""
    for key, item in enumerate(sortArray()):
        
        contestantlist += position_line.replace("{0}", str(key+1)).replace("{1}", str(
            item[1])).replace("{2}", str(item[2])) + "\n"
    msg = header + contestantlist
    try:
        await client.edit_message(trackedchannel, editablemsg, msg)
    except FloodWaitError as e:
        await sendInformationMessage("FloodWaitError while editing the message. The message can be edited after " + str(e.seconds) + " seconds")
    except MessageNotModifiedError:
        pass

async def handlePoints(group_id, newPoints):
    global contestants, point_hints, hints, trackedchannel, pointmsg
    contestant = contestants[int(group_id)]
    ## Sum points
    contestant[2] = int(contestant[2] + int(newPoints))
    user_id = contestant[0]
    await updateMessage()
    if pointmsg is not None:
        await client.send_message(user_id, pointmsg.replace("{0}", str(newPoints)))
    if not random:
        for hintID, points in point_hints.items():
            hint = hints[hintID]
            if contestant[2] == points and hintID not in [index for index in contestant[3]]:
                if isinstance(hint[2], bool) and isinstance(hint[3], bool):
                    if hint[2] and is_even(group_id+1):
                        await sendhint(hint, user_id, contestant)
                    elif not hint[2] and not is_even(group_id+1):
                        await sendhint(hint, user_id, contestant)
                    elif hint[3] and is_even(getContestantPosition(contestant)):
                        await sendhint(hint, user_id, contestant)
                    elif not hint[3] and not is_even(getContestantPosition(contestant)):
                        await sendhint(hint, user_id, contestant)
                elif isinstance(hint[2], bool):
                    if hint[2] and is_even(group_id+1):
                        await sendhint(hint, user_id, contestant)
                    elif not hint[2] and not is_even(group_id+1):
                        await sendhint(hint, user_id, contestant)
                elif isinstance(hint[3], bool):
                    if hint[3] and is_even(getContestantPosition(contestant)):
                        await sendhint(hint, user_id, contestant)
                    elif not hint[3] and not is_even(getContestantPosition(contestant)):
                        await sendhint(hint, user_id, contestant)
                else:
                    await sendhint(hint, user_id, contestant)
                contestant[3].append(hintID)
    else:
        random_hints = [hint for hint in hints if hints.index(hint) not in contestant[3]]
        hint = random.choice(random_hints)
        if isinstance(hint[2], bool) and isinstance(hint[3], bool):
            if hint[2] and is_even(group_id+1):
                await sendhint(hint, user_id, contestant)
            elif not hint[2] and not is_even(group_id+1):
                await sendhint(hint, user_id, contestant)
            elif hint[3] and is_even(getContestantPosition(contestant)):
                await sendhint(hint, user_id, contestant)
            elif not hint[3] and not is_even(getContestantPosition(contestant)):
                await sendhint(hint, user_id, contestant)
        elif isinstance(hint[2], bool):
            if hint[2] and is_even(group_id+1):
                await sendhint(hint, user_id, contestant)
            elif not hint[2] and not is_even(group_id+1):
                await sendhint(hint, user_id, contestant)
            elif isinstance(hint[3], bool):
                if hint[3] and is_even(getContestantPosition(contestant)):
                    await sendhint(hint, user_id, contestant)
                elif not hint[3] and not is_even(getContestantPosition(contestant)):
                    await sendhint(hint, user_id, contestant)
        else:
            await sendhint(hint, user_id, contestant)
        contestant[3].append(hints.index(hint))

async def processEvent(event, externalChat):
    global trackedchannel, editablemsg, rootentity, rootuser, closed, botentity, alreadyAdded, alreadyRecognised
    if ('!leaderboards' in event.raw_text[0:13]):
        await event.delete()
        trackedchannel = await event.get_input_chat()
        if editablemsg is not None:
            await sendInformationMessage("⚠ You're creating a new leaderboards message. Old one won't be updated anymore")
        if is_channel(trackedchannel):
            editablemsg = await client.send_message(trackedchannel, header)
            await updateMessage()
            await sendInformationMessage("Bot ready. For adding contestants, use the __!add__ command. Use __!help__ whenever in doubt")
        else:
            await sendInformationMessage("**You issued the __!leaderboards__ command in a chat that is not a group or a channel. Ignoring...**")
    elif ('!close' in event.raw_text[0:6] or '.c' in event.raw_text[0:2]):
        if not externalChat:
            await event.reply("No more participants will be accepted")
            closed = True
            alreadyRecognised.clear()
        else:
            await event.delete()
            await sendInformationMessage("You issued the __!close__ command where it wasn't allowed")
    elif ('!add ' in event.raw_text[0:5]) or ('.a ' in event.raw_text[0:3]):
        data = event.raw_text
        data = data.replace("!add ", "").replace(".a ", "")
        inputentity = await event.get_input_chat()
        if not closed:
            if not externalChat:
                try:
                    added_id, groupname = data.split(".")
                    added_id = int(added_id)
                except ValueError:
                    await event.reply("**The data is given in an incorrect format**")
                    return
                groupname = groupname.replace("'", "")
                if int(added_id) in alreadyRecognised:
                    contestants.append([added_id, groupname, 0, []])
                    groupid = str(contestants.index(contestants[-1]) + 1)
                    await event.reply("Added **" + str(groupname) + "** and it was assigned the following contestant ID: **" + groupid + "**")
                else:
                    await event.reply("This user can't be added. Check the following:\n\n" \
                        + "·**The user talked to you after starting the bot and it's been recognised.**\n**The UserID is wrong**" + \
                        "\n\nCheck which users (and their `UserIDs`) have been recognised by the bot using **!list**")
                    return
            elif not is_channel(inputentity):
                await event.delete()
                externalentity = await event.get_chat()
                added_id = get_peer_id(inputentity)
                if added_id not in alreadyRecognised:
                    await sendInformationMessage("**" + externalentity.first_name + "** couldn't be added to the Scavenger" + \
                        " because is necessary for the user to talk you first")
                    return
                else:
                    contestants.append([added_id, data, 0, []])
                    groupid = str(contestants.index(contestants[-1]) + 1)
                    await sendInformationMessage("**" + externalentity.first_name + "** has been added with the name '" + data + \
                        "' and was assigned the following contestant ID: **" + groupid + "**")
                del externalentity
            else:
                await event.delete()
                await sendInformationMessage("You can't issue the **!add** command in a channel")
                return
            alreadyAdded[added_id] = int(groupid)
            alreadyRecognised.remove(added_id)
        else:
            if externalChat:
                await event.delete()
            await sendInformationMessage("You can't add more contestants to the Scavenger Hunt because it's closed." + \
                " For reopening it, you must restart the bot, losing all the progress")
        await updateMessage()
    elif ('!list' in event.raw_text[0:5]) or ('.ls' in event.raw_text[0:3]):
        if not externalChat:
            if len(alreadyRecognised) == 0 and len(contestants) == 0:
                output = "**No users recognised or added**"
            else:
                output = ""
                if len(contestants) > 0:
                    output = "**Currently added contestants (Contestant ID - Alias):**\n\n"
                    for key, item in enumerate(contestants):
                        output = output + str(key+1) + " - **" + str(item[1]) + "**\n"
                if len(alreadyRecognised) > 0:
                    output += "\n**Recognised users (UserID: Name)**\n\n"
                    for item in alreadyRecognised:
                        user = await client.get_entity(item)
                        output += str(item) + ": " + user.first_name + "\n"

            await event.reply(output)
            del output
        else:
            await event.delete()
            await sendInformationMessage("The command __!list__ isn't valid in this context")
    elif ('!help' in event.raw_text[0:5]) or ('.h' in event.raw_text[0:2]):
        if not externalChat:
            msg = ""
            if ('!help add' in event.raw_text) or ('.h a' in event.raw_text) or ('.h add' in event.raw_text) or ('!help a' in event.raw_text):
                msg = "**!add** (or **.a**): Adds an user to the leaderboards and starts tracking their points.\n\n**Usage**:\n\n" + \
                    "This command can be used **from the bot and from the `RootUser`**, in **Saved Messages**, **the chat with the participant**, " + \
                    "or in **the `RootUser`'s chat**\n\n" + \
                    "__In `Saved Messages`, from the `RootUser` or in the `RootUser`'s chat:__\n\n**!add UserID.'Alias that will be used in the leaderboards for the contestant'**\n\n" + \
                    "__In the chat with the participant__:\n\n" + \
                    "**!add __Alias that will be used in the leaderboards for the contestant__**\n\n" + \
                    "The command's shortcut __.a__ does exactly the same as the full command, __!add__"
            elif ('!help close' in event.raw_text) or ('.h c' in event.raw_text) or ('.h close' in event.raw_text) or ('!help c' in event.raw_text):
                msg = "**!close** (or **.c**): Stops sending the welcome message to users that talks to the bot and hasn't been recognised by it. " + \
                    "Useful if you expect to receive messages from your contacts while the Scavenger Hunt is in progress\n\n**Usage**:\n\n" + \
                    "This command can be used **from the bot and from the `RootUser`**, but **only in Saved Messages or in the `RootUser`'s chat**\n\n" + \
                    "__This command doesn't have any extra parameters__\n\n" + \
                    "The command's shortcut __.c__ does exactly the same as the full command, __!close__"
            elif '!help leaderboards' in event.raw_text:
                msg = "**!leaderboards**: Should be the first command to be used, although nothing wrong will happen if you do it afterwards.\n" + \
                    "This command sends the message that contains the leaderboards and the updated positions of each contestant as they earn points\n\n**Usage**:\n\n" + \
                    "This command can be used **from the bot and from the `RootUser`**, and **only in Groups, Supergroups and Channels**\n\n" + \
                    "This command doesn't have an shortcut, so you always need to use the full one, __!leaderboards__"
            elif ('!help list' in event.raw_text) or ('.h ls' in event.raw_text) or ('.h list' in event.raw_text) or ('!help ls' in event.raw_text):
                msg = "**!list** (or **.ls**): Lists the users that are taking part in the Scavenger. Also lists users that talked to the bot and " + \
                    "**ARE NOT** added to the Scavenger that it's currently in progress.\n\n**Usage**:\n\n" + \
                    "This command can be used **from the bot and from the `RootUser`**, but **only in Saved Messages or in the `RootUser`'s chat" + \
                    "\n\n__This command doesn't have any extra parameters__\n\n" + \
                    "The command's shortcut __.ls__ does exactly the same as the full command, __!list__"
            elif ('!help prom' in event.raw_text) or ('.h p' in event.raw_text) or ('.h prom' in event.raw_text) or ('!help p' in event.raw_text):
                msg = "**!prom** (or **.p**): This command sums or substracts the given number of points to a participant in the Scavenger Hunt\n\n**Usage**:\n\n" + \
                    "This command can be used **from the bot and from the `RootUser`**, in **Saved Messages**, **the chat with the participant**, " + \
                    "or in **the `RootUser`'s chat**\n\n" + \
                    "__In `Saved Messages`, from the `RootUser` or in the `RootUser`'s chat:__\n\n**!prom ContestantID.__Points__**\n" + \
                    "Example: !prom 2.5 (adds 5 points to contestant with ID 2)\n\n" + \
                    "__In the chat with the participant__:\n\n" + \
                    "**!prom __Points__**\nExample: !prom -5 (substracts 5 points to the contestant that matches the user whose chat got the command issued)\n\n" + \
                    "The command's shortcut __.p__ does exactly the same as the full command, __!prom__"
            elif ('!help help' in event.raw_text):
                msg = "**!help** (or **.h**): This command can give a quick reference for each of the commands that the bot supports. It explains which parameters are " + \
                    "supported and in which kind of situation you can use them.\n\n__The help command is really handy when you have an Scavenger in progress " + \
                    "but, for further explanation of each command, you must always go to the [GitHub's](github.com/ferferga/ScavengerBot) documentation__" + \
                    "\n\n**Usage**:\n\nThis command can be used **from the bot and from the `RootUser`**, but **only in Saved Messages or in the `RootUser`'s chat**" + \
                    "\n\n**Parameters**:\n__Use '!help' followed by the command you want to check. Example: __!help add__\n\n" + \
                    "The command's shortcut __.h__ does exactly the same as the full command, __!help__"
            else:
                msg = "**Available commands**:\n\n**!add**\n**!close**\n**!leaderboards**\n**!list**\n**!prom**\n**!help**" + \
                    "\n\nType *!help <command>* for more information about an specific command"
            await event.reply(msg)
            del msg
        else:
            await event.delete()
            await sendInformationMessage("The command __!help__ isn't valid in this context")
    elif ('!prom ' in event.raw_text[0:6]) or ('.p ' in event.raw_text[0:3]):
        data = event.raw_text
        data = data.replace("!prom ", "").replace(".p ", "").replace(" ", "")
        inputentity = await event.get_input_chat()
        if not externalChat:
            try:
                groupid, points = data.split(".")
            except ValueError:
                await event.reply("**The data is given in an incorrect format**")
                return
            try:
                points = int(points)
                groupid = int(groupid)
            except ValueError:
                await event.reply("**The specified points or contestant ID couldn't be converted to a number**")
                return
            if groupid in alreadyAdded.values():
                await handlePoints(groupid-1, points)
                await event.reply("**" + str(points) + "** points given to contestant with ID **" + str(groupid) + "**")
            else:
                await event.reply("This `ContestantID` doesn't exist or isn't registered in the Scavenger Hunt. Try again")
                return
        elif not is_channel(inputentity):
            await event.delete()
            if get_peer_id(inputentity) not in alreadyAdded:
                externalentity = await event.get_chat()
                await sendInformationMessage("**" + externalentity.first_name + "** isn't participating in this Scavenger Hunt")
                del externalentity
                return
            else:
                try:
                    points = int(data)
                except ValueError:
                    await sendInformationMessage("**The specified points couldn't be converted to a number**")
                    return
                await handlePoints(alreadyAdded[get_peer_id(inputentity)]-1, points)
        else:
            await event.delete()
            await sendInformationMessage("You can't issue the **!prom** command in a channel")
        del inputentity
    elif ("!" in event.raw_text[0]) or ("." in event.raw_text[0]):
        await event.delete()
        await sendInformationMessage("`" + event.raw_text + "` was not recognised as a valid command")

@client.on(events.NewMessage)
async def messageEventHandler(event):
    global closed, rootentity, welcomemsg, botentity, alreadyRecognised
    print("Message event!")
    try:
        if rootuser == -2 and (event.sender_id != get_peer_id(botentity)):
            await event.reply("**Scavenger Bot is running in** `Setup` **mode**\nYour ID: " + str(event.sender_id) + \
                "\n\nPaste this ID in config.json and reload the bot.")
        elif event.sender_id == get_peer_id(botentity):
            if (await event.get_input_chat() == await client.get_input_entity('self')) or \
                (await event.get_input_chat() == await client.get_input_entity(rootuser)):
                await processEvent(event, False)
            else:
                await processEvent(event, True)
        elif event.sender_id == rootuser:
            await processEvent(event, False)        
        elif not closed:
            if (event.sender_id not in alreadyRecognised):
                user = await client.get_entity(await event.get_sender())
                await sendInformationMessage("**A new user was recognised\n\nName: **" + user.first_name + "\n**Id**: " + str(user.id))
                await event.reply(welcomemsg)
                alreadyRecognised.append(event.sender_id)
    except Exception as e:
        print("ERROR!:\n" + str(e))
        await sendInformationMessage("ERROR!\n\n**" + str(e) + "**")

## Main function
print("BOT STARTING...\n")
client.start()
try:
    botentity = client.get_me(True)
    if rootuser == -1:
        print("Bot running in 'In-chat' mode only. Read the documentation for knowing what this means")
        rootentity = client.get_me(True)
    elif rootuser == -2:
        print("Bot running in 'Setup' mode. That means that it will only reply the UserID of the user that sends a message")
    if rootuser > 0:
        rootentity = client.get_entity(rootuser)
except ValueError:
    print("The 'rootuser' in JSON file is invalid. Full details: " + str(e))
    getpass("\nPress ENTER to exit")
    exit(1)
print("BOT STARTED... LISTENING TO EVENTS")
print("You can now start the Scavenger by issuing the '!leaderboards' command. You also have '!help' when needed. Read the documentation before for a comprenhensive explanation of every concept\n")
print("\n\nYou can close the bot at any time by pressing CTRL+C")
try:
    client.run_until_disconnected()
except KeyboardInterrupt:
    client.disconnect()
