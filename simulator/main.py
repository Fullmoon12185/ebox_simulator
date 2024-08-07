import os
from dotenv import load_dotenv
import threading
import time


MY_ENV_VAR = os.getenv('MY_ENV_VAR')


from ebox_simulator import EboxSimulator

load_dotenv()
host = os.getenv("MQTT_BROKER_HOST")
port = int(os.getenv("MQTT_BROKER_PORT"))

username = os.getenv("MQTT_BROKER_USERNAME")
password = os.getenv("MQTT_BROKER_PASSWORD")

numberOfBox = int(os.getenv("NUMBER_OF_BOX"))

print(host)
print(port)
print(username)
print(password)

class MyThread (threading.Thread):
    die = False
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id
        self.eboxId = f'{id:04d}'
        print(f'eboxId = {self.eboxId}')
        self.mqttc = EboxSimulator(self.eboxId)

    def run (self):
        self.mqttc.run(host, port, username, password, self.eboxId)
        while not self.die:
            self.mqttc.running()	

    def join(self):
        self.die = True
        super().join()
        
        
if __name__ == '__main__':
    f = []
    try:
        for i in range (1,1+numberOfBox):
            f.append(MyThread(i))
            f[-1].start()
        while True:
            # print("sleep main")
            time.sleep(2)
    except KeyboardInterrupt:
        for i in range (0+numberOfBox):
            f[i].join()
            print(f'terminate thread {i}')
    # id1 = 1
    # eboxId1 = f'{id1+1:04d}'
    # print(f'eboxId = {eboxId1}')
    # box1 = EboxSimulator(eboxId1)
    # box1.run(host, port, username, password, eboxId1)
    
    # id2 = 2
    # eboxId2 = f'{id2+1:04d}'
    # print(f'eboxId = {eboxId2}')
    # box2 = EboxSimulator(eboxId2)
    # box2.run(host, port, username, password, eboxId2)
    # try:    
    #     while True:
    #         box1.running()    
    #         box2.running()
    #         time.sleep(0.1)
    # except KeyboardInterrupt:
    #     print("Exit")