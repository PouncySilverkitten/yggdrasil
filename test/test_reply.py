import unittest
from hermothr import Hermothr

class TestReply(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr("test_data")
        self.hermothr.message_ids = {"id12345": 'Hermothr'}
        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'id67890',
                                    'content': '',
                                    'sender':   {   'id':      'agent:   ',
                                                    'name':    'Hermothr'}}}
    def test_check_for_parent(self):
        assert self.hermothr.check_parent("id12345") == True
        assert self.hermothr.check_parent("id67890") == False
    
    def test_send_reply_parse(self):
        packet = self.packet
        packet['type'] = "send-reply"
        packet['data']['content'] = "<PouncySilverkitten to PouncySilverkitten 00m04 ago in &test> blah blah"
        self.hermothr.parse(packet)
        assert self.hermothr.message_ids == {"id12345": "Hermothr", "id67890": "PouncySilverkitten"}

    def test_reply_message(self):
        packet = self.packet
        packet['data']['parent'] = "id12345"
        packet['data']['content'] = "!reply Hi hi."
        assert self.hermothr.parse(packet) == "Will do."
        del packet['data']['parent']
        assert self.hermothr.check_for_messages(packet) == ['<Hermothr to you 00m00 ago in &test_data> Hi hi.']

    def test_bad_reply(self):
        packet = self.packet
        packet['data']['parent'] = "id23456"
        packet['data']['content'] = "!reply Hi Hi"
        assert self.hermothr.parse(packet) == None

    def test_empty_reply(self):
        packet = self.packet
        packet['data']['parent'] = "id12345"
        packet['data']['content'] = "!reply"
        assert self.hermothr.parse(packet) == "/me can't see a message there"
