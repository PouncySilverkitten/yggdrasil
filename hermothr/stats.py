import json

with open('notbot_messages.json', 'r') as f:
    messages = json.loads(f.read())

print(len(messages))

print(len(messages['pouncysilverkitten']))
