import datetime
import json
import karelia
import multiprocessing as mp
import pprint
import queue
import re
import sys
import time

from hermothr import Hermothr

rooms = ['xkcd', 'music', 'queer', 'bots']

def main(room):
    hermothr = Hermothr(room)
    while True:
        hermothr.main()

if __name__ == "__main__":
    
    for room in rooms:
        instance = mp.Process(target=main, args=(room,))
        instance.daemon = True
        instance.start()
        
    main('test')
