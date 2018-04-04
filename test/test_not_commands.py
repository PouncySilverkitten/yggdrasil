import unittest
from hermothr import Hermothr

class TestNotCommands(unittest.TestCase):
    def send(self, *args):
        pass

    def parse(self):
        return self.parse_result

    def setUp(self):
        try:
            del(self.parse_result)
        except:
            pass

        self.hermothr = Hermothr('test_data')
        self.hermothr.hermothr.send = self.send
        self.hermothr.hermothr.parse = self.parse
        self.who_with_notbot = {"type": "who-reply",
                                "data": {   "listing":  [   {"name": "Hermothr",
                                                            "id": "bot:"},
                                                            {"name": "NotBot",
                                                            "id": "bot:"}]}}

        self.who_without_notbot = { "type": "who-reply",
                                    "data": {   "listing":  [   {"name": "Hermothr",
                                                                "id": "bot:"},
                                                                {"name": "Heimdall",
                                                                "id": "bot:"}]}}

        self.who_with_notbot_user = {   "type": "who-reply",
                                        "data": {   "listing":  [   {"name": "Hermothr",
                                                                    "id": "bot:"},
                                                                    {"name": "NotBot",
                                                                    "id": "agent:"}]}}



    def test_generate_not_commands_with_notify(self):
        self.parse_result = self.who_without_notbot
        self.hermothr.generate_not_commands()
        assert self.hermothr.not_commands == ['!nnotify', '!herm', '!hermothr', '!notify']

    def test_generate_not_commands_with_notbot_user(self):
        self.parse_result = self.who_with_notbot_user
        self.hermothr.generate_not_commands()
        assert self.hermothr.not_commands == ['!nnotify', '!herm', '!hermothr', '!notify']

    def test_generate_not_commands_without_notify(self):
        self.hermothr.not_commands = ['!nnotify', '!herm', '!hermothr', '!notify']
        self.parse_result = self.who_with_notbot
        self.hermothr.generate_not_commands()
        assert self.hermothr.not_commands == ['!nnotify', '!herm', '!hermothr']

    def test_on_notbot_join(self):
        self.parse_result = self.who_with_notbot
        self.hermothr.parse({"type": "join-event", "data": {"name": "NotBot", "id": "bot:"}})
        assert self.hermothr.not_commands == ['!nnotify', '!herm', '!hermothr']
        assert self.hermothr.hermothr.stockResponses['longHelp'] ==  """A replacement for the much-missed @NotBot.
Accepted commands are !nnotify, !herm, !hermothr (!herm will be used below, but any in the list can be substituted.)
!herm @person (@person_two, @person_three, *group_one, *group_two...) message
    Any combination of nicks and groups can be used.
Use !reply as the child of a notification to reply to the sender:
[Pouncy Silverkitten] checks for mail
    [Hermóðr] <Policy Sisterwritten 08:37:27 ago in &xkcd> Hello :-)
        [Pouncy Silverkitten] !reply Hi!
            [Hermóðr] Will do.
    Nota Bene: any user can !reply to a delivered message. The reply, when delivered, will reflect the nick of the user who replied.
If replying to a message with more than one recipient, a !reply command will send the reply to the sender of the original message, not every recipient.
Use !group and !ungroup to add yourself (or anyone else) to a group that can receive messages just like a person.
!group *group @person (@person_two, @person_three...)
!ungroup *group @person (@person_two, @person_three...)
    Nota Bene: @Hermóðr also obeys the !tgroup and !tungroup commands, so long as they employ the 'basic' syntax described above. It will obey them silently - i.e., it will not reply to them.

Use !grouplist to see all the groups and their members, or !grouplist *group to list the members of a specific group.
    
@Hermóðr also obeys the euphorian bot standards. It\'s likely to have bugs; when you find one, notify Pouncy or log it at https://github.com/PouncySilverkitten/yggdrasil/issues/new. Part of the Yggdrasil Project. 0 messages delivered to date.\nThis is a testing instance and may not be reliable."""
        assert self.hermothr.hermothr.stockResponses['shortHelp'] == "Use !nnotify, !herm, !hermothr to send messages to people who are currently unavailable."

    def test_on_notbot_part(self):
        self.parse_result = self.who_without_notbot
        self.hermothr.parse({"type": "part-event", "data": {"name": "NotBot", "id": "bot:"}})
        assert self.hermothr.not_commands == ['!nnotify', '!herm', '!hermothr', '!notify']
        assert self.hermothr.hermothr.stockResponses['longHelp'] ==  """A replacement for the much-missed @NotBot.
Accepted commands are !nnotify, !herm, !hermothr, !notify (!herm will be used below, but any in the list can be substituted.)
!herm @person (@person_two, @person_three, *group_one, *group_two...) message
    Any combination of nicks and groups can be used.
Use !reply as the child of a notification to reply to the sender:
[Pouncy Silverkitten] checks for mail
    [Hermóðr] <Policy Sisterwritten 08:37:27 ago in &xkcd> Hello :-)
        [Pouncy Silverkitten] !reply Hi!
            [Hermóðr] Will do.
    Nota Bene: any user can !reply to a delivered message. The reply, when delivered, will reflect the nick of the user who replied.
If replying to a message with more than one recipient, a !reply command will send the reply to the sender of the original message, not every recipient.
Use !group and !ungroup to add yourself (or anyone else) to a group that can receive messages just like a person.
!group *group @person (@person_two, @person_three...)
!ungroup *group @person (@person_two, @person_three...)
    Nota Bene: @Hermóðr also obeys the !tgroup and !tungroup commands, so long as they employ the 'basic' syntax described above. It will obey them silently - i.e., it will not reply to them.

Use !grouplist to see all the groups and their members, or !grouplist *group to list the members of a specific group.
    
@Hermóðr also obeys the euphorian bot standards. It\'s likely to have bugs; when you find one, notify Pouncy or log it at https://github.com/PouncySilverkitten/yggdrasil/issues/new. Part of the Yggdrasil Project. 0 messages delivered to date.\nThis is a testing instance and may not be reliable."""

        assert self.hermothr.hermothr.stockResponses['shortHelp'] == "Use !nnotify, !herm, !hermothr, !notify to send messages to people who are currently unavailable."
    def test_on_notbot_user_join_with_notbot(self):
        self.parse_result = self.who_with_notbot
        self.hermothr.parse({"type": "join-event", "data": {"name": "NotBot", "id": "bot:"}})
        self.parse_result = self.who_with_notbot_user
        self.hermothr.parse({"type": "join-event", "data": {"name": "NotBot", "id": "user:"}})
        assert self.hermothr.not_commands == ['!nnotify', '!herm', '!hermothr']

    def test_on_notbot_user_join_without_notbot(self):
        self.parse_result = self.who_without_notbot
        self.hermothr.parse({"type": "part-event", "data": {"name": "NotBot", "id": "bot:"}})
        self.parse_result = self.who_with_notbot_user
        self.hermothr.parse({"type": "join-event", "data": {"name": "NotBot", "id": "user:"}})
        assert self.hermothr.not_commands == ['!nnotify', '!herm', '!hermothr', '!notify']

    def test_on_notbot_part_with_notbot_remain(self):
        self.parse_result = self.who_with_notbot
        self.hermothr.parse({"type": "part-event", "data": {"name": "NotBot", "id": "bot:"}})
        assert self.hermothr.not_commands == ['!nnotify', '!herm', '!hermothr']

