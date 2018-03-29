"""The hermothr module provides a Hermothr object for use elsewhere"""

import datetime
import json
import re
import sys
import time

import karelia

class Hermothr:
    """The Hermothr object is a self-contained instance of the hermothr bot, connected to a single room"""
    def __init__(self, room, **kwargs):
        self.test = True if ('test' in kwargs and kwargs['test']) or room == "test_data" else False

        self.hermothr = karelia.newBot('Hermóðr', room)
        self.not_commands = ['!nnotify', '!herm', '!hermothr']
        self.room = room

        self.last_message_from = "Hermóðr"
        self.message_ids = {}
        self.messages = {}
        self.groups = {}
        self.long_help_template = ""
        self.short_help_template = ""

        self.message_body_template = "<{} to {} {} ago in &{}> {}"

        self.messages_file = "test_messages.json" if self.test else "hermothr_messages.json"
        self.groups_file = "test_groups.json" if self.test else "hermothr_groups.json"
        try:
            self.read_messages()
        except FileNotFoundError:
            with open(self.messages_file, 'w') as f:
                f.write('{}')
        try:
            self.read_groups()
        except FileNotFoundError:
            with open(self.groups_file, 'w') as f:
                f.write('{}')

    def gen_help_messages(self):
        """Produces help messages conforming to the templates below"""
        self.long_help_template = """A replacement for the much-missed @NotBot.
Accepted commands are {} (!herm will be used below, but any in the list can be substituted.)
!herm @person (@person_two, @person_three, *group_one, *group_two...) message
    Any combination of nicks and groups can be used.
Use !reply as the child of a notification to reply to the sender:
[Pouncy Silverkitten] checks for mail
    [Hermóðr] <Policy Sisterwritten 08:37:27 ago in &xkcd> Hello :-)
        [Pouncy Silverkitten] !reply Hi!
            [Hermóðr] Will do.
    Nota Bene: any user can !reply to a delivered message. The reply, when delivered, will reflect the nick of the user who replied.
If replying to a message with more than one recipient, a !reply command will send the reply to the sender of the original message, not every recipient.
Use !group and !ungroup to add yourself (or anyone else) to a group that can receive messages just like a person.
!group *group @person (@person_two, @person_three...)
!ungroup *group @person (@person_two, @person_three...)
    Nota Bene: @Hermóðr also obeys the !tgroup and !tungroup commands, so long as they employ the 'basic' syntax described above. It will obey them silently - i.e., it will not reply to them.

Use !grouplist to see all the groups and their members, or !grouplist *group to list the members of a specific group.
    
@Hermóðr also obeys the euphorian bot standards. It\'s likely to have bugs; when you find one, notify Pouncy or log it at https://github.com/PouncySilverkitten/yggdrasil/issues/new. Part of the Yggdrasil Project."""
        self.short_help_template = 'Use {} to send messages to people who are currently unavailable.'
        self.hermothr.stockResponses['longHelp'] = self.long_help_template.format(', '.join(self.not_commands))
        self.hermothr.stockResponses['shortHelp'] = self.short_help_template.format(', '.join(self.not_commands))

    def read_messages(self):
        """Loads messages from file"""
        with open(self.messages_file, 'r') as f:
            self.messages = json.loads(f.read())

    def read_groups(self):
        """Loads groups from file"""
        with open(self.groups_file, 'r') as f:
            self.groups = json.loads(f.read())

    def list_groups(self):
        """Produces a string in the form group_name: members"""
        groups_as_string = ""
        for group in self.groups.keys():
            groups_as_string += "{}: {}\n".format(group, ', '.join(self.groups[group]))
        return groups_as_string

    def format_recipients(self, names):
        """Produces a nice list of recipients in human-pleasing format"""
        names_as_string = ""
        for i in range(len(names)):
            if i == len(names) - 1 and not len(names) == 1:
                names_as_string += "& {}".format(names[i])
            elif i == len(names) - 1:
                names_as_string += "{}".format(names[i])
            elif i == len(names) - 2:
                names_as_string += "{} ".format(names[i])
            else:
                names_as_string += "{}, ".format(names[i])
        return names_as_string

    def check_messages_for_sender(self, sender):
        """Returns a list of messages for a given sender"""
        self.read_messages()
        if sender in self.messages:
            for_sender = self.messages[sender]
        else:
            return []
        del self.messages[sender]
        self.write_messages()
        return for_sender

    def time_since(self, before):
        """Uses deltas to produce a human-readable description of a time period"""
        now = datetime.datetime.utcnow()
        then = datetime.datetime.utcfromtimestamp(before)

        delta = now - then
        delta_string = str(delta).split('.')[0]
        return delta_string

    def generate_not_commands(self):
        """Adds or removes `!notify` from the list of not_commands"""
        self.hermothr.send({'type': 'who'})
        while True:
            message = self.hermothr.parse()
            if message['type'] == 'who-reply': break
        if not self.check_for_notbot(message['data']['listing']) and '!notify' not in self.not_commands:
            self.not_commands.append('!notify')
        elif '!notify' in self.not_commands:
            self.not_commands.remove('!notify')
        self.gen_help_messages()

    def check_for_notbot(self, listing):
        """Returns True if @NotBot is present, else returns False"""
        for item in listing:
            if 'bot:' in item['id'] and item['name'] == 'NotBot':
                return True
        return False

    def check_for_messages(self, packet):
        """Produces a formatted, usable list of messages for a nick"""
        self.read_messages()
        sender = self.hermothr.normaliseNick(packet['data']['sender']['name'])
        messages_for_sender = self.check_messages_for_sender(sender)
        messages = []
        for message in messages_for_sender:
            messages.append(self.message_body_template.format(  message['sender'],
                                                                message['all_recipients'],
                                                                self.time_since(message['time']),
                                                                message['room'],
                                                                message['text']))

        return messages

    def write_message(self, write_packet):
        """Adds a message to the list of messages"""
        self.read_messages()
        name = write_packet["to"]
        if name in self.messages:
            self.messages[name].append(write_packet)
        else:
            self.messages[name] = [write_packet]
        self.write_messages()

    def check_parent(self, parent):
        """Checks if a message_id belongs to a message sent by the bot"""
        if parent in self.message_ids.keys():
            return True
        return False

    def bland(self, name):
        """Strips whitespace"""
        return re.sub(r'\s+', '', name)

    def write_messages(self):
        """Saves messages to file"""
        with open(self.messages_file, 'w') as f:
            f.write(json.dumps(self.messages))

    def write_groups(self):
        """Saves groups to file"""
        with open(self.groups_file, 'w') as f:
            f.write(json.dumps(self.groups))

    def read_who_to_notify(self, split_content):
        """
        Reads groups and users from a message

        Returns a list of names. If the notnotify is to a group, a list of names
        will still be returned."""
        names = list()
        words = list()
        message = split_content[1:]
        for word in message:
            if word[0] == "@":
                names.append(word[1:])
            elif word[0] == '*':
                if word[1:] in self.groups:
                    names += self.groups[word[1:]]
            elif len(names) > 0:
                return list(set(names))
            else:
                return None

        if names == []:
            return None
        return list(set(names))

    def add_to_group(self, split_contents):
        """Handles !group commands"""
        grouped = []
        not_grouped = []
        del split_contents[0]
        self.read_groups()
        if split_contents[0][0] == '*':
            group_name = split_contents[0][1:]
            if group_name not in self.groups:
                self.groups[group_name] = []
            del split_contents[0]
            for word in split_contents:
                if word[0] == "@":
                    if word[1:] not in self.groups[group_name]:
                        self.groups[group_name].append(word[1:])
                        grouped.append(word[1:])
                        self.write_groups()
                    else:
                        not_grouped.append(word[1:])

            if "!notify" in self.not_commands:
                if grouped == [] and not_grouped == []:
                    return "Couldn't find anyone to add. Syntax is !group *Group @User (@UserTwo...)"
                elif grouped == []:
                    return "User(s) specified are already in the group."
                elif not_grouped == []:
                    return "Adding {} to group {}.".format(", ".join(grouped), group_name)
                else:
                    return "Adding {} to group {} ({} already added).".format(", ".join(grouped), group_name, ", ".join(not_grouped))

        elif "!notify" in self.not_commands:
            return "Couldn't find a group to add user(s) to. Syntax is !group *Group @User (@UserTwo...)"

    def remove_from_group(self, split_content):
        """Handles !ungroup commands"""
        del split_content[0]
        self.read_groups()
        ungrouped = []
        not_ungrouped = []
        if split_content[0][0] == '*':
            group_name = split_content[0][1:]
            if not group_name in self.groups.keys() and '!notify' in self.not_commands:
                return "Group {} not found. Use !grouplist to see a list of all groups.".format(group_name)
            del split_content[0]
            for word in split_content:
                if word[0] == "@":
                    if word[1:] in self.groups[group_name]:
                        self.groups[group_name].remove(word[1:])
                        self.write_groups()
                        ungrouped.append(word[1:])
                    else:
                        not_ungrouped.append(word[1:])

            if self.groups[group_name] == []:
                del self.groups[group_name]

            if "!notify" in self.not_commands:
                if ungrouped == [] and not_ungrouped == []:
                    return "Couldn't find anyone to remove. Syntax is !ungroup *Group @User (@UserTwo...)"
                elif ungrouped == []:
                    return "No user(s) specified are in the group."
                elif not_ungrouped == []:
                    return "Removing {} from group {}.".format(", ".join(ungrouped), group_name)
                else:
                    return "Removing {} from group {} ({} not in group).".format(", ".join(ungrouped), group_name, ", ".join(not_ungrouped))

        elif "!notify" in self.not_commands:
            return "Couldn't find a group to remove users from. Syntax is !ungroup *Group @User (@UserTwo...)"

    def remove_names(self, split_content):
        """Removes the names of the recipients from the text of a message"""
        recipients = []
        while True:
            if len(split_content) > 0 and split_content[0][0] in ['*', '@']:
                if split_content[0][0] == '@':
                    split_content[0] = split_content[0][1:]
                recipients.append(split_content[0])
                del split_content[0]
            else:
                return ' '.join(split_content), ', '.join(recipients)

    def parse(self, packet):
        """Handles all the commands supported"""
        if packet['type'] == 'join-event' or packet['type'] == 'part-event':
            if packet['data']['name'] == 'NotBot' and packet['data']['id'].startswith('bot:'):
                self.generate_not_commands()

        elif packet['type'] == 'send-reply' and packet['data']['content'][0] == "<":
            packet_id = packet['data']['id']
            packet_name = packet['data']['content'].split()[0][1:]
            self.message_ids[packet_id] = packet_name

        elif packet['type'] == 'send-event' and not ('bot:' in packet['data']['sender']['id'] and 'Heimdall' != packet['data']['sender']['name']):
            # Handle a !(not)notify
            split_content = packet['data']['content'].split()
            if split_content[0] in self.not_commands:
                # Returns a list of recipients
                recipients = self.read_who_to_notify(split_content)
                if recipients == None:
                    return "/me couldn't find a person or group to notify there (use !help @Hermóðr to see an example)"
                else:
                    # Returns the message body
                    sane_message, all_recipients = self.remove_names(split_content[1:])

                    if len(sane_message) == 0 or sane_message.isspace():
                        return "/me can't see a message there"

                    sender_name = self.bland(packet['data']['sender']['name'])
                    if sender_name in [self.bland(recipient) for recipient in recipients]:
                        recipients.remove(self.bland(packet['data']['sender']['name']))

                    if len(recipients) == 0: return "/me won't tell you what you already know"
                    recipients.sort()
                    names_as_string = self.format_recipients(recipients)

                    # Used to get a list for the response - for group and multi-nick notifies
                    for name in recipients:
                        write_packet = {"text": sane_message,
                                        "sender": sender_name,
                                        "time": time.time(),
                                        "room": self.room,
                                        "all_recipients": all_recipients,
                                        "to": self.hermothr.normaliseNick(name)}
                        self.write_message(write_packet)

                    return "/me will notify {}.".format(names_as_string)

            elif split_content[0] == "!reply" and 'parent' in packet['data']:
                parent = packet['data']['parent']
                if self.check_parent(parent):
                    recipient = self.message_ids[parent]
                    sane_message = ' '.join(split_content[1:])

                    if len(sane_message) == 0 or sane_message.isspace():
                        return "/me can't see a message there"

                    write_packet = {"text": sane_message,
                                    "sender": self.bland(packet['data']['sender']['name']),
                                    'time': time.time(),
                                    'room': self.room,
                                    'all_recipients': 'you',
                                    'to': self.hermothr.normaliseNick(recipient)}

                    self.write_message(write_packet)
                    return "Will do."

            elif split_content[0] in ["!group", "!tgroup"] and len(split_content) > 1:
                return self.add_to_group(split_content)
            elif split_content[0] in ["!ungroup", "!tungroup"] and len(split_content) > 1:
                return self.remove_from_group(split_content)
            elif len(split_content) == 1 and split_content[0] == '!grouplist':
                return self.list_groups()
            elif split_content[0] == '!grouplist':
                group_name = split_content[1][1:]
                if group_name in self.groups:
                    return '\n'.join(self.groups[group_name])
                else:
                    return "Group not found. !grouplist to view."


    def main(self):
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

        message = ""
        while True:
            try:
                self.hermothr.connect()
                self.generate_not_commands()

                while True:
                    self.read_messages()
                    self.read_groups()

                    packet = self.hermothr.parse()
                    if packet == 'Killed':
                        self.write_messages()
                        self.write_groups()
                        sys.exit()

                    if packet['type'] == 'send-event':
                        messages_for_sender = self.check_for_messages(packet)
                        for message in messages_for_sender:
                            self.hermothr.send(message, packet['data']['id'])
                    reply = self.parse(packet)
                    if reply is not None:
                        self.hermothr.send(reply, packet['data']['id'])

            except Exception:
                self.hermothr.log()
                self.write_messages()
                self.write_groups()
                time.sleep(2)
