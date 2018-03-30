import json
import unittest
from hermothr import Hermothr

class TestReadWhoToNotify(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr('test_data', test=True)
        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'asdfg',
                                    'content': 'This is a message.',
                                    'sender':   {   'id':      'agent:   ',
                                                    'name':    'Hermothr'}}} 

    def test_single_name(self):
        assert self.hermothr.read_who_to_notify('!herm @PouncySilverkitten hi!'.split()) == ["PouncySilverkitten"]
        assert self.hermothr.read_who_to_notify('!hermothr @Xyzzy hello'.split()) == ['Xyzzy']

    def test_multiple_names(self):
        assert self.hermothr.read_who_to_notify('!herm @PouncySilverkitten @herm hi!'.split()).sort() == ["PouncySilverkitten","herm"].sort()
        assert self.hermothr.read_who_to_notify('!hermothr @Xyzzy @Stormageddon @greenie Hey!'.split()).sort() == ["Xyzzy","Stormageddon","greenie"].sort()

    def test_no_name(self):
        packet = self.packet
        packet['data']['content'] = "!herm PouncySilverkitten hi!"
        assert self.hermothr.parse(packet) == "/me couldn't find a person or group to notify there (use !help @Hermóðr to see an example)"
    def test_no_ident(self):
        packet = self.packet
        packet['data']['content'] = "!herm yeah sure, no bother"
        assert self.hermothr.parse(packet) == "/me couldn't find a person or group to notify there (use !help @Hermóðr to see an example)"

    def test_no_group(self):
        packet = self.packet
        packet['data']['content'] = "!herm *IGT link.com"
        assert self.hermothr.parse(packet) == "/me couldn't find a person or group to notify there (use !help @Hermóðr to see an example)"

    def test_only_to_sender(self):
        packet = self.packet
        packet['data']['content'] = "!herm @Hermothr hi!"
        assert self.hermothr.parse(packet) == "/me won't tell you what you already know"

    def test_acceptable_message(self):
        packet = self.packet
        packet['data']['content'] = "!herm @PouncySilverkitten hi!"
        assert self.hermothr.parse(packet) == "/me will notify PouncySilverkitten."

    def test_nick_in_message(self):
        packet = self.packet
        packet['data']['content'] = "!herm @PouncySilverkitten after further consideration, I do not believe @Heimdall to be spammy."
        assert self.hermothr.parse(packet) == "/me will notify PouncySilverkitten."

    def test_no_message(self):
        packet = self.packet
        packet['data']['content'] = "!herm @PouncySilverkitten *tradewinds"
        assert self.hermothr.parse(packet) == "/me can't see a message there"

    def test_only_command(self):
        packet = self.packet
        packet['data']['content'] = "!herm"
        assert self.hermothr.parse(packet) == "/me couldn't find a person or group to notify there (use !help @Hermóðr to see an example)"

    def test_messaging_only_self(self):
        packet = self.packet
        packet['data']['sender']['name'] = "Pouncy Silverkitten"
        packet['data']['content'] = "!herm @PouncySilverkitten blah"
        assert self.hermothr.parse(packet) == "/me won't tell you what you already know"

    def test_messaging_self_others(self):
        packet = self.packet
        packet['data']['content'] = "!herm @Hermothr @PouncySilverkitten Testing"
        assert self.hermothr.parse(packet) == "/me will notify PouncySilverkitten."
