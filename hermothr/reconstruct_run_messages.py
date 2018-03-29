import sqlite3
from hermothr import Hermothr
import sys

def construct(message):
    packet = {}
    packet['data'] = {}
    packet['data']['sender'] = {}
    packet['data']['content'] = message[0]
    packet['type'] = 'send-event'
    packet['data']['id'] = message[1]
    packet['time'] = message[6]
    packet['data']['sender']['name'] = message[5]
    packet['data']['sender']['id'] = message[4]
    return packet

def send(*args):
    pass

conn = sqlite3.connect('../heimdall/logs.db')
c = conn.cursor()

c.execute('''SELECT * FROM xkcd UNION ALL SELECT * FROM music UNION ALL SELECT * FROM bots ORDER BY time''')
messages = c.fetchall()

hermothr = Hermothr('[auto-detected undelivered NotBot message]')
hermothr.hermothr.send = send
hermothr.messages_file = 'notbot_messages.json'
hermothr.groups_file = 'notbot_group.json'
hermothr.read_messages()
hermothr.read_groups()

hermothr.not_commands = ['!notify']

for i, message in enumerate(messages):
    if i%1000 == 0:
        print("{} of 2500000".format(i))
        hermothr.write_messages()
    if message[0].isspace() or len(message[0]) == 0:
        continue
    try:
        hermothr.check_for_messages(construct(message))
        hermothr.parse(construct(message))
    except:
        print(message)
        sys.exit()
