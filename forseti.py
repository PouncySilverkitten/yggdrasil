import multiprocessing
import sqlite3

class Forseti:
    def __init__(self, queue):
        self.queue = queue
        self.file = 'yggdrasil.db'
        self.conn = sqlite3.connect(self.file)
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA journal_mode=WAL;")
        if self.c.fetchall()[0][0] != "wal":
            print("Error enabling write-ahead lookup!")
        
    def main(self):
        while True:
            incoming = self.queue.get()
            if len(incoming) == 3:
                query, values, mode = incoming[0], incoming[1], incoming[2]
            else len(incoming) == 2:
                query = incoming[0]
                if type(incoming[1]) is str:
                    values = ()
                    mode = incoming[1]
                else:
                    values = incoming[1]
                    mode = "execute"

            if mode == 'execute':
                try:
                    self.c.execute(query, values)
                    self.conn.commit()
                except Exception:
                    raise Exception
            elif mode == 'executemany':
                try:
                    self.c.executemany(query, values)
                    self.conn.commit()
                except Exception:
                    raise Exception


def main(queue):
    forseti = Forseti(queue)
    
    forseti.main()
