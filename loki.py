import karelia

def check_aliases(user):
    loki = karelia.newBot('Loki', 'test')
    loki.connect()
    for _ in range(3):
        loki.parse()
    loki.send("!alias @{}".format(user))
    while True:
        reply = loki.parse()
        if reply['type'] == 'send-reply':
            send_id = reply['id']
            break
    while True:
        reply = loki.parse()
        reply_type = reply['type'] == 'send-event'
        sender_name = reply['data']['sender']['name'] == 'TellBot'
        sender_id = reply['data']['sender']['id'].startswith('bot:')
        is_child = 'parent' in reply['data'] and reply['data']['parent'] == send_id

        if reply_type and sender_name and sender_id and is_child:
            pass
