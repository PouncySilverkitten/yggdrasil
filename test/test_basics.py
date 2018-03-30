import json
import os
import shutil
import time
import unittest
from hermothr import Hermothr

class TestBasics(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr('test', test=True)
        self.hermothr.messages_file = 'test_messages.test'
        self.hermothr.groups_file = 'test_groups.test'
        with open('test_messages.test', 'w') as f:
            f.write('{}')
        with open('test_groups.test', 'w') as f:
            f.write('{}')
        self.hermothr.read_messages()
        self.hermothr.read_groups()
        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'id67890',
                                    'content': '',
                                    'sender':   {   'id':      'agent:   ',
                                                     'name':    'Hermothr'}}}
    
    def tearDown(self):
        os.remove('test_messages.test')
        os.remove('test_groups.test')

    def test_timesince(self):
        assert self.hermothr.time_since(time.time()-100000) == "1 day, 3:46:40"
        assert self.hermothr.time_since(time.time()-10000000) == "115 days, 17:46:40"
        assert self.hermothr.time_since(time.time()-10000000000) == "115740 days, 17:46:40"

    def test_data_create(self):
        with open(self.hermothr.messages_file, 'r') as f:
            assert json.loads(f.read()) == {}

        with open(self.hermothr.groups_file, 'r') as f:
            assert json.loads(f.read()) == {}

    def test_read_write_messages(self):
        packet = self.packet
        packet['data']['content'] = "!herm @PouncySilverkitten test test :-)"
        self.hermothr.parse(packet)
        self.hermothr.write_messages()
        self.hermothr.messages = []
        self.hermothr.read_messages()
        assert len(self.hermothr.messages.keys()) == 1
        assert 'pouncysilverkitten' in self.hermothr.messages.keys()
        assert len(self.hermothr.messages['pouncysilverkitten']) == 1

    def test_read_write_groups(self):
        packet = self.packet
        packet['data']['content'] = "!group *Pouncies @PouncySilverkitten @Pouncy"
        self.hermothr.parse(packet)
        self.hermothr.write_groups()
        self.hermothr.groups = []
        self.hermothr.read_groups()
        assert self.hermothr.groups == {'Pouncies': ['PouncySilverkitten', 'Pouncy']}
