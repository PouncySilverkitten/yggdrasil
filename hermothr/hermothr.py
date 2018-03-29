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

message_ids = {}
last_message_from = "Hermóðr"
messages = {}
groups = {}
surprises = []
surprise = False
not_command = ['!nnotify', '!herm', '!hermothr']

class Hermothr:
    def __init__(self, room, **kwargs):
        self.test = True if ('test' in kwargs and kwargs['test']) or room == "test_data" else False

        self.hermothr = karelia.newBot('Hermóðr', room)
        self.not_commands = ['!nnotify', '!herm', '!hermothr']
        self.room = room

        self.last_message_from = "Hermóðr"
        self.message_ids = {}
        self.messages = {}
        self.groups = {}

        self.message_body_template = "<{} to {} {} ago in &{}> {}"

        self.messages_file = "test_messages.json" if self.test else "hermothr_messages.json"
        self.groups_file = "test_groups.json" if self.test else "hermothr_groups.json"
        try:
            self.read_messages()
        except:
            with open(self.messages_file, 'w') as f:
                f.write('{}')
        try:
            self.read_groups()
        except:
            with open(self.groups_file, 'w') as f:
                f.write('{}')
        
    def gen_help_messages(self):
        self.long_help_template = """A replacement for the much-missed @NotBot.
Accepted commands are {} (!herm will be used below, but any in the list can be substituted.)
!herm @PERSON (@PERSON2, @PERSON3...) MESSAGE
!herm *GROUP MESSAGE
Use !reply MESSAGE as the child of a notification to reply to the sender:
[Pouncy Silverkitten] checks for mail
    [Hermóðr] <Policy Sisterwritten 08:37:27 ago in &xkcd> Hello :-)
        [Pouncy Silverkitten] !reply Hi!
            [Hermóðr] Will do.
If replying to a group message, a !reply command will send the reply to the sender of the original message, not the group.
Use !group and !ungroup to add yourself (or anyone else) to a group that can send and receive messages just like a person.
!group *GROUP @PERSON (@PERSON2, @PERSON3...)
!ungroup *GROUP @PERSON (@PERSON2, @PERSON3...)
Use !hermgrouplist to see all the groups and to see their occupants.
    
@Hermóðr also obeys the euphorian bot standards. It\'s likely to have bugs; when you find one, notify Pouncy or log it at https://github.com/PouncySilverkitten/yggdrasil/issues/new. Part of the Yggdrasil Project."""
        self.short_help_template = 'Use {} to send messages to other people who are currently unavailable.'
        self.hermothr.stockResponses['longHelp'] = self.long_help_template.format(', '.join(self.not_commands))
        self.hermothr.stockResponses['shortHelp'] = self.short_help_template.format(', '.join(self.not_commands))

    def read_messages(self):
        with open(self.messages_file, 'r') as f:
            self.messages = json.loads(f.read())

    def read_groups(self):
        with open(self.groups_file, 'r') as f:
            self.groups = json.loads(f.read())

    def list_groups(self):
        groups_as_string = ""
        for group in self.groups.keys():
            groups_as_string += "{}: {}\n".format(group, ', '.join(self.groups[group]))
        return groups_as_string

    def format_recipients(self, names):
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
        return(names_as_string)

    def check_messages_for_sender(self, sender):
        self.read_messages()
        if sender in self.messages:
            for_sender = self.messages[sender]
        else:
            return([])
        del self.messages[sender]
        self.write_messages()
        return(for_sender)

    def time_since(self, before):
        now = datetime.datetime.utcnow()
        then = datetime.datetime.utcfromtimestamp(before)

        delta = now - then
        return str(delta).split('.')[0]
        
    def generate_not_commands(self):
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
        for item in listing:
            if 'bot:' in item['id'] and item['name'] == 'NotBot':
                return True
        return False

    def check_for_messages(self, packet):
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

        return(messages)
    
    def write_message(self, write_packet):
        self.read_messages()
        name = write_packet["to"]
        if name in self.messages:
            self.messages[name].append(write_packet)
        else:
            self.messages[name] = [write_packet]
        self.write_messages()

    def check_parent(self, parent):
        if parent in self.message_ids.keys():
            return True
        return False

    def bland(self, name):
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
    
    def add_to_group(self, data):
        """Handles !group commands"""
        message = data['content'].replace('\n', ' ')
        words = message.split(' ')
        if words[1][0] == '*':
            group_name = words[1][1:]
            if group_name not in self.groups:
                self.groups[group_name] = []
            words.remove(words[0])
            words.remove(words[0])
            for word in words:
                word = word.replace('\n', ' ')
                if len(word) > 2 and word[0] == "@" and not word[1:] in self.groups[group_name]:
                    self.groups[group_name].append(word[1:])
                    if "!notify" in not_command:
                        hermothr.send("Adding {} to group {}".format(word,group_name),data['id'])
        
        self.write_groups() 
    
    def remove_from_group(self, data):
        """Handles !ungroup commands"""
        global groups
        message = data['content']
        words = message.split(' ')
        if words[1][0] == '*':
            group_name = words[1][1:]
            words.remove(words[0])
            words.remove(words[0])
            for word in words:
                if word[0] == "@" and word[1:] in groups[group_name]:
                    groups[group_name].remove(word[1:])
                    if "!notify" in not_command:
                        hermothr.send("Removing {} from group {}".format(word,group_name),data['id'])
            if len(groups[group_name]) == 0:
                del groups[group_name]
            with open('hermothrgroups.json', 'w') as f:
                f.write(json.dumps(groups))

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
            if split_content[0] in self.not_commands and len(split_content) > 2:
                # Returns a list of recipients
                recipients = self.read_who_to_notify(split_content)
                if recipients == None:
                    return "/me couldn't find a person or group to notify there (use !help @Hermóðr to see an example)"
                else:
                    # Returns the message body
                    sane_message, all_recipients = self.remove_names(split_content[1:])
                    
                    if len(sane_message) == 0 or sane_message.isspace():   
                        return("/me can't see a message there")

                    sender_name = self.bland(packet['data']['sender']['name'])
                    if packet['data']['sender']['name'] in recipients: recipients.remove(sender_name)
    
                    if len(recipients) == 0: return("/me won't tell you what you already know")
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

                    return("/me will notify {}.".format(names_as_string))
                
            elif split_content[0] == "!reply" and 'parent' in packet['data'] and len(split_content) > 1:
                parent = packet['data']['parent']
                if self.check_parent(parent):
                    recipient = self.message_ids[parent]
                    sane_message = ' '.join(split_content[1:])
                    
                    write_packet = {"text": sane_message,
                                    "sender": self.bland(packet['data']['sender']['name']),
                                    'time': time.time(),
                                    'room': self.room,
                                    'all_recipients': 'you',
                                    'to': self.hermothr.normaliseNick(recipient)}
                    
                    self.write_message(write_packet)
                    return("Will do.")
    
            elif split_content[0] in ["!group", "!tgroup"] and len(split_content) > 1:
                self.add_to_group(packet['data'])
            elif split_content[0] == ["!ungroup", "!tungroup"] and len(split_content) > 1:
                self.remove_from_group(packet['data'])
            elif len(split_content) == 1 and split_content[0] == '!grouplist':
                return(self.list_groups())
            elif split_content[0] == '!grouplist':
                group_name = split_content[1][1:]
                if group_name in self.groups:
                    return('\n'.join(self.groups[group_name]))
                else:
                    return("Group not found. !grouplist to view.")
            

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
