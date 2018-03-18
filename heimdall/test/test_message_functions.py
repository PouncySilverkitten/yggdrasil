import time
import unittest
from heimdall import Heimdall

class TestBasics(unittest.TestCase):
    def setUp(self):
        self.heimdall = Heimdall('test', verbose = False)
        self.message_with_data_parent = {   'type': 'send-event',
                                            'data': {   'content': 'test message',
                                                        'id': 'uniqueid1',
                                                        'parent': 'parent',
                                                        'time': str(time.time()),
                                                        'sender': { 'id': 'uniqueid',
                                                                    'name': 'Testing Heimdall'}}}


        self.message_with_data = {  'type': 'send-event',
                                    'data': {   'content': 'test message',
                                                'id': 'uniqueid2',
                                                'time': str(time.time()),
                                                'sender': { 'id': 'uniqueid',
                                                            'name': 'Testing Heimdall'}}}


        self.message_with_parent = {'type': 'send-event',
                                    'content': 'test message',
                                    'id': 'uniqueid3',
                                    'parent': 'parent',
                                    'time': str(time.time()),
                                    'sender': { 'id': 'uniqueid',
                                                'name': 'Testing Heimdall'}}

        self.message_with_none = {  'type': 'send-event',
                                    'content': 'test message',
                                    'id': 'uniqueid4',
                                    'time': str(time.time()),
                                    'sender': { 'id': 'uniqueid',
                                                'name': 'Testing Heimdall'}}
        self.heimdall.connect_to_database()

    def test_data_parent(self):
        assert self.heimdall.insert_message(self.message_with_data_parent) == None
    
    def test_data(self):
        assert self.heimdall.insert_message(self.message_with_data) == None

    def test_parent(self):
        assert self.heimdall.insert_message(self.message_with_parent) == None

    def test_none(self):
        assert self.heimdall.insert_message(self.message_with_none) == None

    def test_user_stats(self):
        recvd = [line.replace("\t","") for line in self.heimdall.get_user_stats('Testing Heimdall').split('\n')[1:]]
        expcd = [   "User:Testing Heimdall",
                    "Messages:4",
                    "Messages Sent Today:4",
                    "First Message Date:Today",
                    "First Message:test message",
                    "Most Recent Message:Today",
                    "Average Messages/Day:4",
                    "Busiest Day:2018-03-18, with 4 messages",
                    "Ranking:23 of 29.",
                    "url_goes_here url_goes_here"]
        for i in range(len(expcd)):
            assert recvd[i] == expcd[i]

        self.heimdall.c.execute('''DELETE FROM test WHERE normname = ?''',('testingheimdall',))
        self.heimdall.conn.commit()
