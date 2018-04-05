import unittest
from hermothr import Hermothr

class TestFormatting(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr('test_case', test=True)
        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'asdfg',
                                    'content': 'This is a message.',
                                    'sender':   {   'id':      'agent:   ',
                                                    'name':    'Hermothr'}}}
        
        packet = self.packet
        groupings = {   'GroupOne': [   "PouncySilverkitten",
                                        "Hermothr",
                                        "Heimdall",
                                        "ThisUserDoesnaeExist"],
                        'GroupTwo': [   "UserOne",
                                        "UserTwo",
                                        "UserThree",
                                        "UserFour"]}

        for group in list(groupings.keys()):
            packet['data']['content'] = "!group *{} {}".format(group, " ".join(["@"+name for name in groupings[group]]))
            self.hermothr.parse(packet)



    def test_format_recipients(self):
        assert self.hermothr.format_recipients(['Hermothr']) == "Hermothr"
        assert self.hermothr.format_recipients(['Hermothr', 'Hermothr']) == "Hermothr & Hermothr"
        assert self.hermothr.format_recipients(['Hermothr', 'Hermothr', 'Hermothr']) == "Hermothr, Hermothr & Hermothr"

    def test_format_group_recipient(self):
        packet = self.packet
        packet['data']['content'] = "!herm *GroupOne here's a message for ya"
        assert self.hermothr.parse(packet) == "/me will notify Heimdall, PouncySilverkitten & ThisUserDoesnaeExist."
    
    def test_multiple_users(self):
        packet = self.packet
        packet['data']['content'] = "!herm @PouncySilverkitten @Heimdall @ThisUserDoesnaeExist message"
        assert self.hermothr.parse(packet) == "/me will notify Heimdall, PouncySilverkitten & ThisUserDoesnaeExist."

    def test_multiple_groups(self):
        packet = self.packet
        packet['data']['content'] = "!herm *GroupOne *GroupTwo message"
        assert self.hermothr.parse(packet) == "/me will notify Heimdall, PouncySilverkitten, ThisUserDoesnaeExist, UserFour, UserOne, UserThree & UserTwo."
    
    def test_mixed_groups_users(self):
        packet = self.packet
        packet['data']['content'] = "!herm *GroupOne *GroupTwo @PolicySisterwritten @Pouncy hi hi"
        assert self.hermothr.parse(packet) == "/me will notify Heimdall, PolicySisterwritten, Pouncy, PouncySilverkitten, ThisUserDoesnaeExist, UserFour, UserOne, UserThree & UserTwo."
