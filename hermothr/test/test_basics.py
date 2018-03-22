import json
import os
import shutil
import time
import unittest
from hermothr import Hermothr

class TestBasics(unittest.TestCase):
    def setUp(self):
        shutil.copyfile('test_messages.json', 'test_messages.json.backup')
        shutil.copyfile('test_groups.json', 'test_groups.json.backup')
        os.remove('test_messages.json')
        os.remove('test_groups.json')
        self.hermothr = Hermothr('test', test=True)
        
    def test_timesince(self):
        assert self.hermothr.time_since(time.time()-100000) == "1 day, 3:46:40"
        assert self.hermothr.time_since(time.time()-10000000) == "115 days, 17:46:40"
        assert self.hermothr.time_since(time.time()-10000000000) == "115740 days, 17:46:40"

    def test_data_create(self):
        with open("test_messages.json", 'r') as f:
            assert json.loads(f.read()) == {}

        with open("test_groups.json", 'r') as f:
            assert json.loads(f.read()) == {}

    def tearDown(self):
        shutil.copyfile('test_messages.json.backup', 'test_messages.json')
        shutil.copyfile('test_groups.json.backup', 'test_groups.json')
        os.remove('test_messages.json.backup')
        os.remove('test_groups.json.backup')
