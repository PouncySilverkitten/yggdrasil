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
if __name__ == "__main__":
    
    for room in rooms:
        notnotbot = Hermothr(room)
        instance = mp.Process(target=main, args=(room, notnotbot))
        instance.daemon = True
        instance.start()
        
    notnotbot = karelia.newBot('Hermóðr', 'test')
    main('test', notnotbot)
