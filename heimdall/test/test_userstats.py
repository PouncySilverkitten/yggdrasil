import unittest
from heimdall import Heimdall

class TestUserStats(unittest.TestCase):
    def setUp(self):
        self.heimdall = Heimdall('test')

    def test_userstats(self):
        print(self.heimdall.get_user_stats('Pouncy Silverkitten')
