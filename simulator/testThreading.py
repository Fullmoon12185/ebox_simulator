import threading
import time

class MyThread (threading.Thread):
    die = False
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run (self):
        while not self.die:
            time.sleep(1)
            print (self.name)

    def join(self):
        self.die = True
        super().join()

if __name__ == '__main__':
    f = MyThread('first')
    f.start()
    s = MyThread('second')
    s.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        f.join()
        s.join()