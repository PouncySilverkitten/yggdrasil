import unittest

import loki

class Loki:
    def __init__(self):
        self.parse_list = []

    def send(self, string):
        for _ in range(3):
            self.parse_list.append({'type': 'send-reply', 'data': {'id': '12345'}})
            if string == '!alias @PouncySilverkitten':
                reply = {   'type': 'send-event',
                            'data': {   'sender': { 'name': 'TellBot',
                                                    'id':   'bot:12345'},
                                        'parent':   '12345',
                                        'content':  'Aliases of @PouncySilverkitten (4): PouncySilverkitten, PouncySilverkitten:black_nib::scroll:, Pouncy, and PSk'}}
                self.parse_list.append(reply)

    def parse(self):
        message = self.parse_list[0]
        del self.parse_list[0]
        return message

    def disconnect(self):
        pass

class TestLoki(unittest.TestCase):
    def connect(self):
        return Loki()

    def setUp(self):
        self.user = "PouncySilverkitten"
        self.loki = Loki()
        loki.connect = self.connect

    def test_get_aliases(self):
        assert loki.get_aliases(self.loki, self.user) == "Aliases of @PouncySilverkitten (4): PouncySilverkitten, PouncySilverkitten:black_nib::scroll:, Pouncy, and PSk"

    def test_parse_aliases(self):
        assert loki.parse_aliases("Aliases of @PouncySilverkitten (4): PouncySilverkitten, PouncySilverkitten:black_nib::scroll:, Pouncy, and PSk") == ["PouncySilverkitten", "PouncySilverkitten:black_nib::scroll:", "Pouncy", "PSk"]

    def test_all(self):
        assert loki.check_aliases(self.user) == ["PouncySilverkitten", "PouncySilverkitten:black_nib::scroll:", "Pouncy", "PSk"]
