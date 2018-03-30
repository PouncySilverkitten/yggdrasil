from calendar import timegm
from datetime import datetime
import unittest
from heimdall import Heimdall

class TestBasics(unittest.TestCase):
    def setUp(self):
        self.heimdall = Heimdall('test_data', verbose=False)
        self.heimdall.connect_to_database()

    def tearDown(self):
        self.heimdall.c.execute('''DELETE FROM test_data WHERE id IS "id_of_message_to_be_deleted"''')
        self.heimdall.conn.commit()

    def test_roomstats(self):
        recvd = [line.replace('\t','') for line in self.heimdall.get_room_stats().split('\n') if not line.isspace()]
        self.expcd = [  'There have been 1503 posts in &test_data (0 today), averaging 53 posts per day over the last 28 days (the busiest was 2018-03-12 with 1319 messages sent).',
                        '',
                        'The top ten posters are:', 
                        ' 1) 117    Pouncy Silverkitten',
                        ' 2) 93     User 9',
                        ' 3) 90     User 6',
                        ' 4) 89     User 5',
                        ' 5) 89     User 7',
                        ' 6) 87     User 4',
                        ' 7) 86     User 8',
                        ' 8) 85     User 2',
                        ' 9) 83     User 0',
                        '10) 83     User 1',
                        '',
                        'all_time_url last_28_url']

        for i in range(len(self.expcd)):
            assert self.expcd[i] == recvd[i]

    def test_add_message(self):
        packet = {  'type': 'send-event',
                    'data': {   'content': "Just adding a test message to check that the today count updates itself properly.",
                                'id': "id_of_message_to_be_deleted",
                                'parent': '',
                                'sender': { 'id':   'agent:12345',
                                            'name': 'DeleteMeWhenTestsAreDone'},
                                'time': timegm(datetime.utcnow().utctimetuple())}}

        self.heimdall.parse(packet)

        recvd = [line.replace('\t','') for line in self.heimdall.get_room_stats().split('\n') if not line.isspace()]
        self.expcd = [  'There have been 1504 posts in &test_data (1 today), averaging 53 posts per day over the last 28 days (the busiest was 2018-03-12 with 1319 messages sent).',
                        '',
                        'The top ten posters are:', 
                        ' 1) 117    Pouncy Silverkitten',
                        ' 2) 93     User 9',
                        ' 3) 90     User 6',
                        ' 4) 89     User 5',
                        ' 5) 89     User 7',
                        ' 6) 87     User 4',
                        ' 7) 86     User 8',
                        ' 8) 85     User 2',
                        ' 9) 83     User 0',
                        '10) 83     User 1',
                        '',
                        'all_time_url last_28_url']

        for i in range(len(self.expcd)):
            assert self.expcd[i] == recvd[i]
        
