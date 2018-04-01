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

        self.hermothr.messages = {}
        self.hermothr.write_messages()
        for message in self.messages:
            self.hermothr.write_message(message)

        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'asdfg',
                                    'content': 'This is a message.',
                                    'sender':   {   'id':      'agent:   ',
                                                    'name':    'Hermothr'}}}
    def test_no_message(self):
        packet = self.packet
        packet['data']['sender']['name'] = "NoMessagesForMe"
        assert self.hermothr.check_for_messages(packet) == []

    def test_single_message(self):
        packet = self.packet
        assert self.hermothr.check_for_messages(packet) == ['<Hermothr to Hermothr 0:00:00 ago in &xkcd> test message 123 blah']
    
    def test_new_message(self):
        packet = self.packet
        packet['data']['sender']['name'] = 'Hermothr-test'
        assert self.hermothr.check_for_messages(packet) == ['<PouncySilverkitten to Hermothr-test 0:01:00 ago in &test_data> test message 123 blah']

    def test_multiple_messages(self):
        delivered = self.hermothr.messages_delivered
        packet = self.packet
        packet['data']['sender']['name'] = 'Multi-Message Test'
        assert self.hermothr.check_for_messages(packet) == ['<PouncySilverkitten to Multi-Message Test 0:03:44 ago in &music> Look at all...', '<PouncySilverkitten to Multi-Message Test 0:03:04 ago in &bots> ...these messages!']
        assert self.hermothr.messages_delivered == delivered + 2

    def test_group(self):
        packet = self.packet
        packet['data']['sender']['name'] = 'HermothrGroup'
        assert self.hermothr.check_for_messages(packet) == ['<PouncySilverkitten to *NotifierBots 0:00:34 ago in &bots> Hi gang!']

    def test_groups(self):
        packet = self.packet
        packet['data']['sender']['name'] = 'HermothrGroups'
        assert self.hermothr.check_for_messages(packet) == ['<PouncySilverkitten to *NotifierBots, *ProjectYggdrasil 0:00:34 ago in &bots> Hi gang!']
        
    def test_pipeline(self):
        with open('test_messages.json','w') as f:
            f.write('{}')
        self.hermothr.read_messages()

        self.hermothr.groups = {"NotifierBots":     ["Hermothr", "TellBot"],
                                "ProjectYggdrasil": ["Heimdall", "Hermothr"],
                                "RandomGroup":      ["me", "you", "some person"]}
        template = self.packet

        template['data']['sender']['name'] = 'Pouncy Silverkitten'
        packet = template

        packet['data']['content'] = "!herm @Hermothr This is the first test message."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm @Hermothr @Pouncy This is the second test message."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm *NotifierBots This is the third test message."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm *NotifierBots *ProjectYggdrasil This is the fourth."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm *NotifierBots @Pouncy This is the fifth."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm *RandomGroup @Hermothr This is the sixth..."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm @Hermothr @Pouncy *NotAGroup ...and the seventh."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm no-one'll get this."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm *RandomGroup and you shouldn't get this."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "!herm @Pouncy or this one, @Hermothr."
        self.hermothr.parse(packet)
        
        packet['data']['content'] = "/me is tired after all that."
        packet['data']['sender']['name'] = "Hermothr"

        assert self.hermothr.check_for_messages(packet) == ['<PouncySilverkitten to Hermothr 0:00:00 ago in &test_data> This is the first test message.',
                                                            '<PouncySilverkitten to Hermothr, Pouncy 0:00:00 ago in &test_data> This is the second test message.',
                                                            '<PouncySilverkitten to *NotifierBots 0:00:00 ago in &test_data> This is the third test message.',
                                                            '<PouncySilverkitten to *NotifierBots, *ProjectYggdrasil 0:00:00 ago in &test_data> This is the fourth.',
                                                            '<PouncySilverkitten to *NotifierBots, Pouncy 0:00:00 ago in &test_data> This is the fifth.',
                                                            '<PouncySilverkitten to *RandomGroup, Hermothr 0:00:00 ago in &test_data> This is the sixth...',
                                                            '<PouncySilverkitten to Hermothr, Pouncy, *NotAGroup 0:00:00 ago in &test_data> ...and the seventh.']

