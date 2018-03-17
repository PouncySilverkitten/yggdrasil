import datetime
import json
import karelia
import multiprocessing as mp
import pprint
import queue
import re
import sys
import time

rooms = ['xkcd', 'music', 'queer', 'bots']

messageIds = {}
lastMessageFrom = "NotNotBot"
messages = {}
groups = {}
surprises = []
surprise = False
notCommand = ['!nnotify', '!notnotify']

def main(room, notnotbot):
    """
    main acts as an input redirector, calling functions as required.

    Currently, `!notnotify @user` and `!notnotify *group` are supported, as well as
    `!group *group @user`, `!ungroup *group @user`, and `!reply message`.

    - `!notnotify` will add a notify for user or group.
    - `!reply`, sent as the child of a notnotification, will send that reply to
    the original sender.
    - `!group` adds the specified user(s) to the specified group
    - `!ungroup` removes the specified user(s) from the specified groups
    """

    notnotbot.stockResponses['longHelp'] = """A  @NotBot alternative. Use !nnotify or !notnotify to send messages to other people who are currently unavailable.
    !notnotify @PERSON (@PERSON2, @PERSON3...) MESSAGE
    !notnotify *GROUP MESSAGE
Use !reply MESSAGE as the child of a notification to reply to the sender:
[Pouncy Silverkitten] checks for mail
    [NotNotBot] <Policy Sisterwritten (2017-05-30 08:37:27 UTC)> Hello :-)
        [Pouncy Silverkitten] !reply Hi!
            [NotNotBot] Will do.
If replying to a group message, a !reply command will send the reply to the sender of the original message, not the group.
Use !group and !ungroup to add yourself (or anyone else) to a group that can send and receive messages just like a person.
    !group *GROUP @PERSON (@PERSON2, @PERSON3...)
    !ungroup *GROUP @PERSON (@PERSON2, @PERSON3...)
Use !notgrouplist to see all the groups and to see their occupants.

@NotNotBot also obeys the euphorian bot standards. It\'s likely to have bugs; when you find one, notify Pouncy or log it at https://github.com/PouncySilverkitten/notnotbot/issues/new."""
    notnotbot.stockResponses['shortHelp'] = 'Use !notify to send messages to other people who are currently unavailable.'

    global notCommand, messageIds
    
    message = ""
    while True:
        try:
            conn = notnotbot.connect()
            
            while True:
                # Load messages
                with open('notnotbotmessages.json', 'r') as f:
                    messages = json.loads(f.read())
                # Load groups
                with open('notnotbotgroups.json', 'r') as f:
                    groups = json.loads(f.read())

                packet = notnotbot.parse()
                if packet == 'Killed':
                    writeOutMessages(messages)
                    writeOutGroups(groups)
                    sys.exit()
                    
                if packet['type'] == 'join-event':
                    if packet['data']['name'] == 'NotBot' and packet['data']['id'].startswith('bot:'):
                        notCommand = [command for command in notCommand if command != '!notify']

                elif packet['type'] == 'part-event':
                    if packet['data']['name'] == 'NotBot' and packet['data']['id'].startswith('bot:'):
                        notCommand.append('!notify')

                elif packet['type'] == 'snapshot-event':
                    connected = [listing['name'] for listing in packet['data']['listing']]
                    if 'NotBot' in connected:
                        notCommand = [command for command in notCommand if command != '!notify']
                    else:
                        notCommand.append('!notify')

                elif packet['type'] == 'send-event' and not 'bot:' in packet['data']['sender']['id']:

                    # Handle a !(not)notify
                    if packet['data']['content'].split()[0] in notCommand and len(packet['data']['content'].split()) > 2:
                        # Returns a list of recipients
                        names = readWhoToNotify(packet['data']['content'])
                        if names == None: notnotbot.send("/me couldn't find a person to notify there (syntax is {} @person message)".format(notCommand[0]), packet['data']['id'])
                        elif names == False: notnotbot.send("/me couldn't find that group (!notgrouplist to see them)", packet['data']['id'])
                        else:
                        
                            # Returns the message body
                            saneMessage = removeNames(packet['data']['content'], len(names))

                            # Indicate in the message body that the message was sent to a group
                            groupFlag = " "
                            sender = re.sub(r'\s+', '', packet['data']['sender']['name'])
                            if packet['data']['content'].split(' ')[1][0] == "*":
                                groupFlag = " to *{} ".format(packet['data']['content'].split(' ')[1][1:])
                                if sender in names: names.remove(sender)

                            # Assemble the final form of the message
                            message = "<{}{}({} UTC) in &{}> {}".format(packet['data']['sender']['name'], groupFlag, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), room, saneMessage)
                            namesAsString = ""

                            # Used to get a list for the response - for group and multi-nick notifies
                            writePacket = {"text": message, "sender": bland(sender)}
                            for name in names:
                                if names.index(name) == len(names) - 1 and not len(names) == 1:
                                    namesAsString += "& {}".format(name)
                                elif names.index(name) == len(names) - 1:
                                    namesAsString += "{}".format(name)
                                elif names.index(name) == len(names) - 2:
                                    namesAsString += "{} ".format(name)
                                else:
                                    namesAsString += "{}, ".format(name)

                                name = bland(name)
                                if name in messages:
                                    messages[name].append(writePacket)
                                else:
                                    messages[name] = [writePacket]
                            notnotbot.send("I'll notify {}.".format(namesAsString), packet['data']['id'])

                            # Back up by writing to file
                            writeOutMessages(messages)
                        
                    elif packet['data']['content'].split(' ')[0] == "!reply" and 'parent' in packet['data'] and len(packet['data']['content'].split()) > 1:
                        parent = packet['data']['parent']
                        if parent in messageIds:
                            name = messageIds[parent]
                            saneMessage = ' '.join(packet['data']['content'].split()[1:])
                            message = "<{} ({} UTC) in &{}> {}".format(packet['data']['sender']['name'], datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), room, saneMessage)
                            message = {"text": message, "sender": re.sub(r'\s+', '', packet['data']['sender']['name']).lower()}
                            if name in messages: messages[name].append(message)
                            else: messages[name] = [message]
                            writeOutMessages(messages)
                            notnotbot.send("Will do.", packet['data']['id'])

                    elif packet['data']['content'].split()[0] == '!group':
                        addToGroup(packet['data'])
                    elif packet['data']['content'].split()[0] == '!ungroup':
                        removeFromGroup(packet['data'])
                    elif packet['data']['content'] == '!notgrouplist':
                        listGroups(packet['data']['id'])
                    elif packet['data']['content'].startswith('!notgrouplist '):
                        groupName = packet['data']['content'].split()[1][1:]
                        if groupName in groups:
                            reply = ""
                            for user in groups[groupName]: reply += user + "\n"
                            notnotbot.send(reply, packet['data']['id'])
                        else:
                            notnotbot.send("Group not found. !notgrouplist to view a list.", packet['data']['id'])

                    sender = re.sub(r'\s+', '', packet['data']['sender']['name']).lower()
                    if sender in messages:
                        replyTo = packet['data']['id']
                        for message in messages[sender]:
                            notnotbot.send(message['text'], replyTo)
                            while True:
                                packet = notnotbot.parse()
                                if packet['type'] == 'send-reply' and packet['data']['content'] == message['text']: break
                            messageIds[packet['data']['id']] = message['sender']
                        messages[sender] = []
                        writeOutMessages(messages)

        except Exception:
            notnotbot.log()
            writeOutMessages(messages)
            writeOutGroups(groups)
            time.sleep(2)
            
def bland(name):
    return re.sub(r'\s+', '', name).lower()

def writeOutMessages(messages):
    """Saves messages to file"""
    with open('notnotbotmessages.json', 'w') as f:
        f.write(json.dumps(messages))


def writeOutGroups(groups):
    """Saves groups to file"""
    with open('notnotbotgroups.json', 'w') as f:
        f.write(json.dumps(groups))


def readWhoToNotify(message):
    """
    Reads groups and users from a message

    Returns a list of names. If the notnotify is to a group, a list of names
    will still be returned."""
    names = list()
    words = list()
    lines = message.split('\n')
    for line in lines:
        words += line.split()
    message = words[1:]
    for word in message:
        if word[0] == "@":
            names.append(word[1:])
        elif word[0] == '*':
            try:
                for name in groups[word[1:]]:
                    names.append(name)
            except KeyError: return False
        elif len(names) > 0:
            return names
        else: return None


def addToGroup(data):
    """Handles !group commands"""
    global groups
    message = data['content'].replace('\n', ' ')
    words = message.split(' ')
    if words[1][0] == '*':
        groupName = words[1][1:]
        if groupName not in groups:
            groups[groupName] = []
        words.remove(words[0])
        words.remove(words[0])
        for word in words:
            word = word.replace('\n', ' ')
            if len(word) > 2 and word[0] == "@" and not word[1:] in groups[groupName]:
                groups[groupName].append(word[1:])
                if "!notify" in notCommand:
                    notnotbot.send("Adding {} to group {}".format(word,groupName),data['id'])
        with open('notnotbotgroups.json', 'w') as f:
            f.write(json.dumps(groups))


def removeFromGroup(data):
    """Handles !ungroup commands"""
    global groups
    message = data['content']
    words = message.split(' ')
    if words[1][0] == '*':
        groupName = words[1][1:]
        words.remove(words[0])
        words.remove(words[0])
        for word in words:
            if word[0] == "@" and word[1:] in groups[groupName]:
                groups[groupName].remove(word[1:])
                if "!notify" in notCommand:
                    notnotbot.send("Removing {} from group {}".format(word,groupName),data['id'])
        if len(groups[groupName]) == 0:
            del groups[groupName]
        with open('notnotbotgroups.json', 'w') as f:
            f.write(json.dumps(groups))


def listGroups(id):
    """Creates a nicely-formatted list of groups and their members."""
    global groups
    reply = ""
    for group in groups:
        reply += "{}: {}\n".format(group,
                                   str(groups[group])[1:-1].replace("'", ''))
    notnotbot.send(reply, id)


def removeNames(message, blah):
    """Removes the names of the notnotifiees from the text of a message"""
    mess = message.split(' ')[1:]
    while True:
        if mess[0][0] == '*' or mess[0][0] == "@":
            mess.remove(mess[0])
        else:
            break
    lessOfAMess = ''
    for m in mess:
        lessOfAMess += m + ' '
    return(lessOfAMess)


if __name__ == "__main__":

    try:
        with open('notnotbotmessages.json', 'r') as f:
            messages = json.loads(f.read())
    except:
        with open('notnotbotmessages.json', 'w') as f:
            f.write('{}')
    try:
        with open('notnotbotgroups.json', 'r') as f:
            groups = json.loads(f.read())
    except:
        with open('notnotbotgroups.json', 'w') as f:
            f.write('{}')
    for room in rooms:
        notnotbot = karelia.newBot('NotNotBot', room)
        instance = mp.Process(target=main, args=(room, notnotbot))
        instance.daemon = True
        instance.start()
        
    notnotbot = karelia.newBot('NotNotBot', 'test')
    main('test', notnotbot)
