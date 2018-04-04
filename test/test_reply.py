import unittest
from hermothr import Hermothr

class TestReply(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr("test_data")
        self.hermothr.write_to_database('''INSERT INTO notifications VALUES(?,?,?,?,?,?,?,?,?)''', values=("Hermothr", "hermothr", "you", "0", "test_data", "hi hi!", "Hermothr0youyou", 1, "id12345"))
        self.hermothr.write_to_database('''INSERT INTO notifications VALUES(?,?,?,?,?,?,?,?,?)''', values=("Hermothr", "hermothr", "you", "0", "test_data", "hi hi!", "PouncySilverkitten0pouncysilverkittenPouncySilverkitten", 0, ""))
        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'id67890',
                                    'content': '',
                                    'sender':   {   'id':      'agent:   ',
                                                    'name':    'Hermothr'}}}

    def tearDown(self):
        self.hermothr.c.execute('''DROP TABLE notifications''')
        self.hermothr.conn.commit()
        self.hermothr.conn.close()

    def test_check_for_parent(self):
        assert self.hermothr.check_parent("id12345") == True
        assert self.hermothr.check_parent("id67890") == False
    
    def test_send_reply_parse(self):
        packet = self.packet
        packet['type'] = "send-reply"
        packet['data']['content'] = "<PouncySilverkitten to PouncySilverkitten 00m04 ago in &test> hi hi!"
        self.hermothr.thought_delivered = {packet['data']['content']: "PouncySilverkitten0pouncysilverkittenPouncySilverkitten"}
        self.hermothr.parse(packet)
        self.hermothr.c.execute('''SELECT COUNT(*) FROM notifications WHERE delivered IS 1''')
        assert self.hermothr.c.fetchone()[0] == 2

    def test_reply_message(self):
        packet = self.packet
        packet['data']['content'] = "/me delivers a message"
        messages = self.hermothr.check_for_messages(packet)
        sendreply = self.packet
        sendreply['type'] = 'send-reply'
        sendreply['data']['id'] = "id34567"
        for message in messages:
            self.hermothr.thought_delivered[message[0]] = message[1]
            sendreply['data']['content'] = message[0]
            self.hermothr.parse(sendreply)
        packet['type'] = "send-event"
        packet['data']['parent'] = "id12345"
        packet['data']['content'] = "!reply Testing replying to a reply here!"
        assert self.hermothr.parse(packet) == "Will do."
        del packet['data']['parent']
        assert self.hermothr.check_for_messages(packet)[0][0] == '<Hermothr to you 00m00 ago in &test_data> Testing replying to a reply here!'

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
