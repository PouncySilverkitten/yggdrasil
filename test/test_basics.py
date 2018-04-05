import json
import os
import shutil
import time
import unittest
from hermothr import Hermothr

class TestBasics(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr('test', test=True)
        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'id67890',
                                    'content': '',
                                    'sender':   {   'id':      'agent:   ',
                                                     'name':    'Hermothr'}}}
    
    def test_timesince(self):
        assert self.hermothr.time_since(time.time()-100000) == "1 day, 3h46m40"
        assert self.hermothr.time_since(time.time()-10000000) == "115 days, 17h46m40"
        assert self.hermothr.time_since(time.time()-10000000000) == "115740 days, 17h46m40"
