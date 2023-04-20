

#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation

# This example shows how you can use the MQTT client in a class.

import paho.mqtt.client as mqtt
import threading


class EboxSimulator(mqtt.Client):
    
    # def __init__(self, id):
    #     mqtt.Client.__init__(self)
    #     self.rc = 0
    #     self.id = id
    
    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: "+str(rc))

    def on_connect_fail(self, mqttc, obj):
        print("Connect failed")

    def on_message(self, mqttc, obj, msg):
        print("Nguyen....")
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    def on_publish(self, mqttc, obj, mid):
        print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print("N1...")
        print(string)
        

    def run(self, host, port, username, password, ebox_id):
        self.username_pw_set(username, password)
        self.connect(host, port, 60)
        # self.username_pw_set("uat_mqtt","1kiNIcfT5")
        # self.connect("mqtt-uat.eboost.vn", 8883, 60)
        topic = "CEbox_" + str(ebox_id)
        self.subscribe(topic, 0)
        
    def running(self):
        self.loop()
        
    def stop(self):
        print('def')
        self.rc = 1
        print(f'def = {self.rc}')
        
    

