import os
import unittest
from hermothr import Hermothr

class TestGroups(unittest.TestCase):
    def setUp(self):
        self.hermothr = Hermothr('test_data', test=True)

        self.hermothr.not_commands.append("!notify")
        self.packet = { 'type': 'send-event',
                        'data': {   'id': 'asdfg',
                                    'sender':   {   'id':   'agent:   ',
                                                    'name': 'ImAUser'}}}
        packet = self.packet
        packet['data']['content'] = '!group *GroupOne @PouncySilverkitten @Hermothr @Heimdall @ThisUserDoesnaeExist'
        self.hermothr.parse(packet)
        packet['data']['content'] = '!group *GroupTwo @UserOne @UserTwo @UserThree @UserFour'
        self.hermothr.parse(packet)
        packet['data']['content'] = '!group *tradewinds @Nuvanda @totallyhuman @DoctorNumberFour @Xyzzy @ㅇㅈㅇ @K @Garmy'
        self.hermothr.parse(packet)

    def tearDown(self):
        try:
            self.hermothr.c.execute('''DROP TABLE groups''')
            self.hermothr.conn.commit()
            self.hermothr.conn.close()
        except:
            pass

    def test_grouplist(self):
        packet = self.packet
        packet['data']['content'] = '!grouplist'
        assert self.hermothr.parse(packet) == 'GroupOne: PouncySilverkitten, Hermothr, Heimdall, ThisUserDoesnaeExist\nGroupTwo: UserOne, UserTwo, UserThree, UserFour\ntradewinds: Nuvanda, totallyhuman, DoctorNumberFour, Xyzzy, ㅇㅈㅇ, K, Garmy\n'

    def test_list_bad_group(self):
        packet = self.packet
        packet['data']['content'] = "!grouplist *GroupThree"
        assert self.hermothr.parse(packet) == "Group not found. !grouplist to view."
    
    def test_list_group(self):
        packet = self.packet
        packet['data']['content'] = '!grouplist *GroupOne'
        assert self.hermothr.parse(packet) == "PouncySilverkitten\nHermothr\nHeimdall\nThisUserDoesnaeExist"

    def test_ungroup(self):
        packet = self.packet
        packet['data']['content'] = '!ungroup *GroupOne @PouncySilverkitten'
        assert self.hermothr.parse(packet) == "Removing PouncySilverkitten from group GroupOne."
        assert self.hermothr.get_dict_of_groups()['GroupOne'] == "Hermothr,Heimdall,ThisUserDoesnaeExist"

    def test_ungroup_no_users_in_group(self):
        packet = self.packet
        packet['data']['content'] = '!ungroup *GroupOne @Pouncy'
        assert self.hermothr.parse(packet) == "No user(s) specified are in the group."
        
    def test_ungroup_group_does_not_exist(self):
        packet = self.packet
        packet['data']['content'] = '!ungroup *GroupThree @Pouncy'
        assert self.hermothr.parse(packet) == "Group GroupThree not found. Use !grouplist to see a list of all groups."

    def test_ungroup_no_group(self):
        packet = self.packet
        packet['data']['content'] = "!ungroup @PouncySilverkitten"
        assert self.hermothr.parse(packet) == "Couldn't find a group to remove users from. Syntax is !ungroup *Group @User (@UserTwo...)"

    def test_group_no_group(self):
        packet = self.packet
        packet['data']['content'] = "!group @PouncySilverkitten"
        assert self.hermothr.parse(packet) == "Couldn't find a group to add user(s) to. Syntax is !group *Group @User (@UserTwo...)"

    def test_group_mixed(self):
        packet = self.packet
        packet['data']['content'] = "!group *GroupOne @PouncySilverkitten @UserOne"
        assert self.hermothr.parse(packet) == "Adding UserOne to group GroupOne (PouncySilverkitten already added)."
        assert self.hermothr.get_dict_of_groups()["GroupOne"] == "PouncySilverkitten,Hermothr,Heimdall,ThisUserDoesnaeExist,UserOne"

    def test_group(self):
        packet = self.packet
        packet['data']['content'] = "!group *GroupTwo @PouncySilverkitten"
        assert self.hermothr.parse(packet) == "Adding PouncySilverkitten to group GroupTwo."
        assert self.hermothr.get_dict_of_groups()["GroupTwo"] == "UserOne,UserTwo,UserThree,UserFour,PouncySilverkitten"
        packet['data']['content'] = "!group *GroupTwo @Pouncy @Hermothr"
        assert self.hermothr.parse(packet) == "Adding Pouncy, Hermothr to group GroupTwo."
        assert self.hermothr.get_dict_of_groups()["GroupTwo"] == "UserOne,UserTwo,UserThree,UserFour,PouncySilverkitten,Pouncy,Hermothr"

    def test_group_invalid_user(self):
        packet = self.packet
        packet['data']['content'] = "!group *GroupOne Pouncy"
        assert self.hermothr.parse(packet) == "Couldn't find anyone to add. Syntax is !group *Group @User (@UserTwo...)"

    def test_group_user_already_member(self):
        packet = self.packet
        packet['data']['content'] = "!group *GroupOne @PouncySilverkitten"
        assert self.hermothr.parse(packet) == "User(s) specified are already in the group."

    def test_create_group(self):
        packet = self.packet
        packet['data']['content'] = "!group *GroupThree @PouncySilverkitten"
        assert self.hermothr.parse(packet) == "Adding PouncySilverkitten to group GroupThree."
        assert 'GroupThree' in self.hermothr.get_dict_of_groups()
        assert self.hermothr.get_dict_of_groups()['GroupThree'] == "PouncySilverkitten"

    def test_ungroup_invalid_user(self):
        packet = self.packet
        packet['data']['content'] = "!ungroup *GroupTwo PouncySilverkitten"
        assert self.hermothr.parse(packet) == "Couldn't find anyone to remove. Syntax is !ungroup *Group @User (@UserTwo...)"

    def test_delete_group(self):
        packet = self.packet
        packet['data']['content'] = "!ungroup *GroupTwo @UserOne @UserTwo @UserThree @UserFour"
        self.hermothr.parse(packet)
        self.hermothr.get_dict_of_groups == {'GroupOne': "PouncySilverkitten,Hermothr,Heimdall,ThisUserDoesnaeExist", 'tradewinds': "Nuvanda,totallyhuman,DoctorNumberFour,Xyzzy,ㅇㅈㅇ,K,Garmy"}

    def test_ungroup_no_user(self):
        packet = self.packet
        packet['data']['content'] = "!ungroup *GroupTwo"
        assert self.hermothr.parse(packet) == "Couldn't find anyone to remove. Syntax is !ungroup *Group @User (@UserTwo...)"

    def test_group_no_user(self):
        packet = self.packet
        packet['data']['content'] = "!group *GroupOne"
        assert self.hermothr.parse(packet) == "Couldn't find anyone to add. Syntax is !group *Group @User (@UserTwo...)"

    def test_ungroup_mixed(self):
        packet = self.packet
        packet['data']['content'] = "!ungroup *GroupTwo @PouncySilverkitten @UserOne"
        assert self.hermothr.parse(packet) == "Removing UserOne from group GroupTwo (PouncySilverkitten not in group)."
