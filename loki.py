import karelia

def connect():
    loki = karelia.newBot('Loki', 'test')
    loki.connect()
    for _ in range(3):
        loki.parse()
    return loki

def get_aliases(loki, user):
    loki.send("!alias @{}".format(user))
    while True:
        reply = loki.parse()
        if reply['type'] == 'send-reply':
            send_id = reply['data']['id']
            break
    while True:
        reply = loki.parse()
        reply_type = reply['type'] == 'send-event'
        sender_name = reply['data']['sender']['name'] == 'TellBot'
        sender_id = reply['data']['sender']['id'].startswith('bot:')
        is_child = 'parent' in reply['data'] and reply['data']['parent'] == send_id

        if reply_type and sender_name and sender_id and is_child:
            content = reply['data']['content']
            break
    loki.disconnect()
    return(content)

def parse_aliases(content):
    aliases = []
    content = content.split('): ')[1]
    aliases = [name.replace('and ','').strip() if name.startswith('and ') else name.strip() for name in content.split(', ')]
    return aliases

def check_aliases(user):
    loki = connect()
    content = get_aliases(loki, user)
    aliases = parse_aliases(content)
    return aliases

def add_alias(master, alias):
    return ('''INSERT OR FAIL INTO aliases VALUES (?, ?)''', (master, alias,))

def is_alias(alias):
    return ('''SELECT COUNT(*) FROM aliases WHERE alias IS ?''', (alias,))

def remove_alias(alias):
    return ('''DELETE FROM aliases * WHERE alias IS ?''', (alias,))

def alias_of(alias):
    return ('''SELECT master from aliases WHERE alias IS ?''', (alias))
