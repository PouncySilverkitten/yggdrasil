import os
import shutil
import time
import unittest
from hermothr import Hermothr

class testMessageDelivery(unittest.TestCase):
    def setUp(self):
        shutil.copyfile('test_messages.json', 'test_messages.backup')
        shutil.copyfile('test_groups.json', 'test_groups.backup')
        os.remove('test_messages.json')
        os.remove('test_groups.json')
        self.hermothr = Hermothr('test_data', test=True)
        self.messages = [   {   "text": "test message 123 blah",
                                "sender": "Hermothr",
                                "time": time.time(),
                                "room": "test",
                                "group": "",
                                "recipient": "Hermothr"},
                            {   "text": "test message 123 blah",
                                "sender": "Hermothr",
                                "time": time.time()-60,
                                "room": "test",
                                "group": "",
                                "recipient": "Hermothr-test"},
                                ]

        for message in self.messages:
            self.hermothr.write_message(message)
        self.hermothr.read_messages()
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
        assert self.hermothr.check_for_messages(packet) == ['<Hermothr 0:00:00 ago in &test> test message 123 blah']
    
    def test_new_message(self):
        packet = self.packet
        packet['data']['sender']['name'] = 'Hermothr-test'
        assert self.hermothr.check_for_messages(packet) == ['<Hermothr-test 0:01:00 ago in &test> test message 123 blah']

    def tearDown(self):
        shutil.copyfile('test_messages.backup', 'test_messages.json')
        shutil.copyfile('test_groups.backup', 'test_groups.json')
        os.remove('test_messages.backup')
        os.remove('test_groups.backup')
