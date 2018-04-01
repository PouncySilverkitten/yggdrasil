import multiprocessing
import sqlite3

class Forseti:
    def __init__(self, queue):
        self.queue = queue
        self.file = 'logs.db'
        self.conn = sqlite3.connect(self.file)
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA journal_mode=WAL;")
        if self.c.fetchall()[0][0] != "wal":
            print("Error enabling write-ahead lookup!")
        
    def main(self):
        while True:
            incoming = self.queue.get()
            if len(incoming) == 2:
                query, parameters = incoming[0], incoming[1]
            else:
                query = incoming
                parameters = ()
            try:
                self.c.execute(query, parameters)
                self.conn.commit()
            except:
                pass

def main(queue):
    forseti = Forseti(queue)
    
    forseti.main()
