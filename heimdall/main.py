import argparse
import multiprocessing as mp
import signal
import sys
from heimdall import Heimdall, KillError

def on_sigint(signum, frame):
    """Handles sigints"""
    try:
        heimdall.conn.commit()
        heimdall.conn.close()
        heimdall.heimdall.disconnect()
    finally:
        sys.exit()

def run(heimdall):
    while True:
        try:
            heimdall.main()
        except KillError:
            sys.exit()

rooms = ['xkcd','music','queer','bots']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("room", nargs='?')
    parser.add_argument("--stealth", help="If enabled, bot will not present on nicklist", action="store_true")
    parser.add_argument("--force-new-logs", help="If enabled, Heimdall will delete any current logs for the room", action="store_true", dest="new_logs")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, on_sigint)

    if args.room is not None:
        room = args.room
        stealth = args.stealth
        new_logs = args.new_logs

        heimdall = Heimdall(room, stealth=stealth, new_logs=new_logs)

        run(heimdall)

    else:
        for room in rooms:
            heimdall = Heimdall(room)
            instance = mp.Process(target=run, args=(heimdall,))
            instance.daemon = True
            instance.start()

        heimdall = Heimdall('test')
        run(heimdall)

if __name__ == '__main__':
    main()
