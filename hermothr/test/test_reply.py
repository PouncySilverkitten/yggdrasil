import unittest
from hermothr import Hermothr

class TestReply(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr("test_data")

    def test_check_for_parent(self):
        self.hermothr.message_ids = ["id12345"]
        assert self.hermothr.check_parent("id12345") == True
        assert self.hermothr.check_parent("id67890") == False
