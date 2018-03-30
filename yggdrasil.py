import multiprocessing as mp

import heimdall
import hermothr
import karelia

class UpdateDone(Exception):
    pass

class KillError(Exception):
    pass

def on_sigint(signum, frame):
    """Gracefully handle sigints"""
    try:
        heimdall.conn.commit()
        heimdall.conn.close()
        heimdall.heimdall.disconnect()
    finally:
        sys.exit()

def run_heimdall(room):
    heimdall.main(room)

def run_hermothr(room):
    hermothr.main(room)

rooms = ['xkcd', 'music', 'queer', 'bots', 'test']

for room in rooms:
    instance = mp.Process(target = run_hermothr, args=(room,))
    instance.daemon = True
    instance.start()

    instance = mp.Process(target = run_heimdall, args=(room,))
    instance.daemon = True
    instance.start()

yggdrasil = karelia.newBot('Yggdrasil', 'test')
yggdrasil.connect()
while True:
    yggdrasil.parse()
