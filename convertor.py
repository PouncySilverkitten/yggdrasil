import json
import sqlite3

with open('hermothr_messages.json', 'r') as f:
    messages = json.loads(f.read())

print(messages.keys())
