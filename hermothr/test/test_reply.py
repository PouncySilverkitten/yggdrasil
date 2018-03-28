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
        packet['data']['content'] = "<PouncySilverkitten 0:00:04 ago in &test> !herm @PouncySilverkitten blah blah"
        self.hermothr.parse(packet)
        assert self.hermothr.message_ids == {"id12345": "Hermothr", "id67890": "PouncySilverkitten"}
