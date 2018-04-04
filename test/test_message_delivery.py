import copy
import pprint
import os
import shutil
import time
import unittest
from hermothr import Hermothr

class testMessageDelivery(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr('test_data', test=True)

        self.messages = [   {   "text": "test message 123 blah",
                                "sender": "Hermothr",
                                "time": time.time(),
                                "room": "xkcd",
                                "all_recipients": "Hermothr",
                                "to": "hermothr"},
                            {   "text": "test message 123 blah",
                                "sender": "PouncySilverkitten",
                                "time": time.time()-60,
                                "room": "test_data",
                                "all_recipients": "Hermothr-test",
                                "to": "hermothr-test"},
                            {   "text": "Look at all...",
                                "sender": "PouncySilverkitten",
                                "time": time.time()-224,
                                "room": "music",
                                "all_recipients": "Multi-Message Test",
                                "to": "multi-messagetest"},
                            {   "text": "...these messages!",
                                "sender": "PouncySilverkitten",
                                "time": time.time()-184,
                                "room": "bots",
                                "all_recipients": "Multi-Message Test",
                                "to": "multi-messagetest"},
                            {   "text": "Hi gang!",
                                "sender": "PouncySilverkitten",
                                "time": time.time()-34,
                                "room": "bots",
                                "all_recipients": "*NotifierBots",
                                "to": "hermothrgroup"},
                            {   "text": "Hi gang!",
                                "sender": "PouncySilverkitten",
                                "time": time.time()-34,
                                "room": "bots",
                                "all_recipients": "*NotifierBots, *ProjectYggdrasil",
                                "to": "hermothrgroups"},
                                ]

        for message in self.messages:
            write_packet = (message['sender'],
                            self.hermothr.hermothr.normaliseNick(message['to']),
                            message['all_recipients'],
                            message['time'],
                            message['room'],
                            message['text'],
                            "{}{}{}{}".format(  message['sender'],
                                                time.time(),
                                                self.hermothr.hermothr.normaliseNick(message['to']),
                                                message['all_recipients']),
                            0,
                            '')

            self.hermothr.write_to_database('''INSERT INTO notifications VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''', values=write_packet)


        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'asdfg',
                                    'content': 'This is a message.',
                                    'sender':   {   'id':      'agent:   ',
                                                    'name':    'Hermothr'}}}

        packet = self.packet
        groupings = {   "NotifierBots":     ["Hermothr", "TellBot", "HermothrGroup"],
                        "ProjectYggdrasil": ["Heimdall", "Hermothr"],
                        "RandomGroup":      ["me", "you", "someperson"]}
        for group in list(groupings.keys()):
            packet['data']['content'] = "!group *{} {}".format(group, " ".join(["@"+name for name in groupings[group]]))
            self.hermothr.parse(packet)

    def tearDown(self):
        self.hermothr.c.execute('''DROP TABLE notifications''')
        self.hermothr.conn.commit()
        self.hermothr.conn.close()

    def test_no_message(self):
        packet = self.packet
        packet['data']['sender']['name'] = "NoMessagesForMe"
        assert self.hermothr.check_for_messages(packet) == []

    def test_single_message(self):
        packet = self.packet
        assert [message[0] for message in self.hermothr.check_for_messages(packet)] == ['<Hermothr to Hermothr 00m00 ago in &xkcd> test message 123 blah']
    
    def test_new_message(self):
        packet = self.packet
        packet['data']['sender']['name'] = 'Hermothr-test'
        assert [message[0] for message in self.hermothr.check_for_messages(packet)] == ['<PouncySilverkitten to Hermothr-test 01m00 ago in &test_data> test message 123 blah']

    def test_multiple_messages(self):
        self.hermothr.c.execute('''SELECT COUNT(*) FROM notifications WHERE delivered IS 1''')
        messages_delivered = self.hermothr.c.fetchone()[0]
        packet = self.packet
        packet['data']['sender']['name'] = 'Multi-Message Test'
        messages = self.hermothr.check_for_messages(packet)
        assert [message[0] for message in messages] == ['<PouncySilverkitten to Multi-Message Test 03m44 ago in &music> Look at all...', '<PouncySilverkitten to Multi-Message Test 03m04 ago in &bots> ...these messages!']
        for message in messages:
            self.hermothr.thought_delivered[message[0]] = message[1]
        packet = self.packet
        packet['type'] = "send-reply"
        packet['data']['id'] = "id12345"
        packet['data']['content'] = "<PouncySilverkitten to Multi-Message Test 03m44 ago in &music> Look at all..."
        self.hermothr.parse(packet)
        packet['data']['id'] = "id67890"
        packet['data']['content'] = "<PouncySilverkitten to Multi-Message Test 03m04 ago in &bots> ...these messages!"
        self.hermothr.parse(packet)
        self.hermothr.c.execute('''SELECT COUNT(*) FROM notifications WHERE delivered IS 1''')
        assert self.hermothr.c.fetchone()[0] == messages_delivered + 2

    def test_group(self):
        packet = self.packet
        packet['data']['sender']['name'] = 'HermothrGroup'
        assert [[part[2:] if part[0].isdigit() else part for part in message[0].split('00m')] for message in self.hermothr.check_for_messages(packet)] == [['<PouncySilverkitten to *NotifierBots ',' ago in &bots> Hi gang!']]

    def test_groups(self):
        packet = self.packet
        packet['data']['sender']['name'] = 'HermothrGroups'
        returned = self.hermothr.check_for_messages(packet)
        responses = [[part[2:] if part[0].isdigit() else part for part in message[0].split('00m')] for message in returned]
        assert len(returned[0]) == 2
        assert responses == [['<PouncySilverkitten to *NotifierBots, *ProjectYggdrasil ',' ago in &bots> Hi gang!']]
        
    def test_pipeline(self):
        template = self.packet

        template['data']['sender']['name'] = 'Pouncy Silverkitten'
        packets = []

        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm @Hermothr This is the first test message."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm @Hermothr @Pouncy This is the second test message."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm *NotifierBots This is the third test message."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm *NotifierBots *ProjectYggdrasil This is the fourth."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm *NotifierBots @Pouncy This is the fifth."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm *RandomGroup @Hermothr This is the sixth..."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm @Hermothr @Pouncy *NotAGroup ...and the seventh."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm no-one'll get this."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm *RandomGroup and you shouldn't get this."
        packets.append(packet)
        
        packet = copy.deepcopy(template)
        packet['data']['content'] = "!herm @Pouncy or this one, @Hermothr."
        packets.append(packet)

        for packet_to_be_sent in packets:
            self.hermothr.parse(packet_to_be_sent)
        
        packet = template
        packet['data']['content'] = "/me is tired after all that."
        packet['data']['sender']['name'] = "Hermothr"

        responses = self.hermothr.check_for_messages(packet)

        assert len(responses[0]) == 2
        assert len(responses[6]) == 2
        responses = [[part[1:] if part[0].isdigit() else part for part in message[0].split('00m0')] for message in responses]
        
        assert responses[1] == ['<PouncySilverkitten to Hermothr ',' ago in &test_data> This is the first test message.']
        assert responses[2] == ['<PouncySilverkitten to Hermothr, Pouncy ',' ago in &test_data> This is the second test message.']
        assert responses[3] == ['<PouncySilverkitten to *NotifierBots ',' ago in &test_data> This is the third test message.']
        assert responses[4] == ['<PouncySilverkitten to *NotifierBots, *ProjectYggdrasil ',' ago in &test_data> This is the fourth.']
        assert responses[5] == ['<PouncySilverkitten to *NotifierBots, Pouncy ',' ago in &test_data> This is the fifth.']
        assert responses[6] == ['<PouncySilverkitten to *RandomGroup, Hermothr ',' ago in &test_data> This is the sixth...']
        assert responses[7] == ['<PouncySilverkitten to Hermothr, Pouncy, *NotAGroup ',' ago in &test_data> ...and the seventh.']
