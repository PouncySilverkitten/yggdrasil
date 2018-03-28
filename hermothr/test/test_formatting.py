import unittest
from hermothr import Hermothr

class TestFormatting(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr('test_case', test=True)
        self.hermothr.messages = {  'Group One': [  "PouncySilverkitten",
                                                    "Hermothr",
                                                    "Heimdall",
                                                    "ThisUserDoesnaeExist"],
                                    'Group Two': [  "UserOne",
                                                    "UserTwo",
                                                    "UserThree",
                                                    "UserFour"]}
    def test_format_recipients(self):
        assert self.hermothr.format_recipients(['Hermothr']) == "Hermothr"
        assert self.hermothr.format_recipients(['Hermothr', 'Hermothr']) == "Hermothr & Hermothr"
        assert self.hermothr.format_recipients(['Hermothr', 'Hermothr', 'Hermothr']) == "Hermothr, Hermothr & Hermothr"
