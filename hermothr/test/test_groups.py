import unittest
from hermothr import Hermothr

class TestGroups(unittest.TestCase):

    def setUp(self):
        self.hermothr = Hermothr('test_data', test=True)
        self.hermothr.groups = {    'GroupOne': [  "PouncySilverkitten",
                                                    "Hermothr",
                                                    "Heimdall",
                                                    "ThisUserDoesnaeExist"],
                                    'GroupTwo': [  "UserOne",
                                                    "UserTwo",
                                                    "UserThree",
                                                    "UserFour"]}

        self.packet = {  'type': 'send-event',
                    'data': {   'id': 'asdfg',
                                'sender':   {   'id':      'agent:   ',
                                                'name':    'ImAUser'}}}
    def test_grouplist(self):
        packet = self.packet
        packet['data']['content'] = '!notgrouplist'
        assert self.hermothr.parse(packet) == ('GroupOne: PouncySilverkitten, Hermothr, Heimdall, ThisUserDoesnaeExist\nGroupTwo: UserOne, UserTwo, UserThree, UserFour\n') 

    def test_list_group(self):
        packet = self.packet
        packet['data']['content'] = '!notgrouplist *GroupOne'
        assert self.hermothr.parse(packet) == "PouncySilverkitten\nHermothr\nHeimdall\nThisUserDoesnaeExist"
