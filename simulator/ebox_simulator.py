

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
import time

TIME_LOOP   = 1 #second

PERIOD_3_SECOND = 3/TIME_LOOP

NUMBER_OF_OUTLET = 10

OUTLET_AVAILABLE = 0
OUTLET_READY = 1
OUTLET_CHARGING = 2
OUTLET_FULLCHARGE = 3



class EboxSimulator(mqtt.Client):
    
    # def __init__(self, id):
    #     mqtt.Client.__init__(self)
    #     self.rc = 0
    #     self.id = id
    STATUS_TOPIC = ""
    CURRENT_TOPIC = ""    
    VOLTAGE_TOPIC = ""
    POWER_TOPIC = ""
    POWER_FACTOR_TOPIC = ""
    outletStatus = []
    outletCurrent = []
    outletPowerFactor = []
    outletPower = []
    eboxId = 0
    
    counter = 0
    topicIndex = 0
    
    def on_connect(self, mqttc, obj, flags, rc):
        self.printCustom("rc: "+str(rc))

    def on_connect_fail(self, mqttc, obj):
        self.printCustom("Connect failed")

    def on_message(self, mqttc, obj, msg):
        self.printCustom("Nguyen....")
        self.printCustom(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.processCommand(msg.topic, msg.payload)
        

    def on_publish(self, mqttc, obj, mid):
        self.printCustom("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        self.printCustom("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        self.printCustom("N1...")
        self.printCustom(string)
        

    def run(self, host, port, username, password, ebox_id):
        self.username_pw_set(username, password)
        self.connect(host, port, 60)
        # self.username_pw_set("uat_mqtt","1kiNIcfT5")
        # self.connect("mqtt-uat.eboost.vn", 8883, 60)
        topic = "CEbox_" + str(ebox_id)
        self.subscribe(topic, 0)
        self.eboxId = ebox_id
        
        self.box_initialization()
        
        
        
    def running(self):
        self.loop()
        time.sleep(TIME_LOOP)
        self.appPublishData()
        
        
        
    def printCustom(self, message):
        print(f'[{self.eboxId}] - {message}')    
        
    def appPublishData(self):
        self.counter = self.counter + 1.0
        self.printCustom(f'counter = {self.counter}')
        if(self.counter == PERIOD_3_SECOND):
            
            self.printCustom(f'topicIndex = {self.topicIndex}')
            
            
            if(self.topicIndex == 0):
                self.publish_ebox_statuses()
            # elif(self.topicIndex == 1):
            #     self.publish_ebox_currents()
            
            self.counter = 0
            self.topicIndex = (self.topicIndex + 1)%5
    
    def clearTopicIndex(self):
        self.topicIndex = 0
        
    def processCommand(self, topic, payload):
        self.printCustom(f'topic = {topic}')
        self.printCustom(f'payload = {payload}')

        self.printCustom(f'self.eboxId = {self.eboxId}')
        self.printCustom(f' str(self.eboxId) in topic = { str(self.eboxId) in topic}')
        self.printCustom(f'payload[0] = {int(payload[0])}')
        if str(self.eboxId) in topic and int(payload[0]) == 49:
            tempOutletId = int(payload[1]) - 48
            self.printCustom(f'tempOutletId = {tempOutletId}')
            if(tempOutletId > NUMBER_OF_OUTLET - 1):
                return
            
            tempOutletStatus = int(payload[2]) - 48
            
            self.printCustom(f'tempOutletId = {tempOutletId}')
            self.printCustom(f'tempOutletStatus = {tempOutletStatus}')
            if(tempOutletStatus == 0):
                self.outletAvailable(tempOutletId)
            elif(tempOutletStatus == 1):
                self.outletReady(tempOutletId)
                
                
            self.clearTopicIndex()    
    
    
    def publish_ebox_statuses(self):
        # Publish message to MQTT Broker
        self.publish(self.STATUS_TOPIC,self.statuses_update())
    def publish_ebox_currents(self):
        # Publish message to MQTT Broker
        self.publish(self.CURRENT_TOPIC,self.currents_update())
    def publish_ebox_power_factors(self):
        # Publish message to MQTT Broker
        self.publish(self.POWER_FACTOR_TOPIC,self.power_factors_update())
    def publish_ebox_powers(self):
        # Publish message to MQTT Broker
        self.publish(self.POWER_TOPIC,self.powers_update())
        
    
    def publish_ebox_voltage(self):
        # Publish message to MQTT Broker
        self.publish(self.VOLTAGE_TOPIC,self.voltage_update())    
        
    def box_initialization(self):
        for i in range(0,NUMBER_OF_OUTLET+1):
            self.outletStatus.append(OUTLET_AVAILABLE)
            self.outletCurrent.append(0)
            self.outletPowerFactor.append(0)
            self.outletPower.append(0)
            
        self.topic_intialization(self.eboxId)
        
    def topic_intialization(self, box_id):
        self.STATUS_TOPIC = "SEbox_" + str(box_id)
        self.CURRENT_TOPIC = "AEbox_" + str(box_id)
        self.VOLTAGE_TOPIC = "VEbox_" + str(box_id)
        self.POWER_TOPIC = "PEbox_" + str(box_id)
        self.POWER_FACTOR_TOPIC = "PFEbox_" + str(box_id)

    def statuses_update(self):
        statusMessage = ""
        for id in range (0, NUMBER_OF_OUTLET):
            statusMessage = statusMessage +  str(id) + '-' + str(self.outletStatus[id]) + ','	
        
        statusMessage = statusMessage +  str(NUMBER_OF_OUTLET) + '-' + str(self.outletStatus[NUMBER_OF_OUTLET])
        self.printCustom(f'statusMessage = {statusMessage}')
        return statusMessage    
    def set_outlet_status(self, id, status):
        self.outletStatus[id] = status
    
    def outletAvailable(self, id):
        self.set_outlet_status(id, OUTLET_AVAILABLE)
    def outletReady(self, id):
        self.set_outlet_status(id, OUTLET_READY)
    def outletCharging(self, id):
        self.set_outlet_status(id, OUTLET_CHARGING)
    def outletFullCharge(self, id):
        self.set_outlet_status(id, OUTLET_FULLCHARGE)
    
    
    def currents_update(self):
        currentMessage = ""
        for id in range (0, NUMBER_OF_OUTLET):
            currentMessage = currentMessage +  str(id) + '-' + str(self.outletCurrent[id]) + ','	
        
        currentMessage = currentMessage + str(NUMBER_OF_OUTLET) + '-' + str(self.outletCurrent[NUMBER_OF_OUTLET])
        return currentMessage 

    def set_outlet_current(self, id, current):
        self.outletCurrent[id] = current    


    def power_factors_update(self):
        powerFactorMessage = ""
        for i in range (0, NUMBER_OF_OUTLET):
            powerFactorMessage = powerFactorMessage +  str(id) + '-' + str(self.outletPowerFactor[id]) + ','	
        powerFactorMessage = powerFactorMessage +  str(NUMBER_OF_OUTLET) + '-' + str(self.outletPowerFactor[NUMBER_OF_OUTLET])
        return powerFactorMessage
    
    def set_outlet_power_factor(self, id, powerFactor):
        self.outletPowerFactor[id] = powerFactor
        
        
    def powers_update(self):
        powerMessage = ""
        for i in range (0, NUMBER_OF_OUTLET):
            powerMessage = powerMessage +  str(id) + '-' + str(self.outletPower[id]) + ','	
        
        powerMessage = powerMessage +  str(NUMBER_OF_OUTLET) + '-' + str(self.outletPower[NUMBER_OF_OUTLET])
        return powerMessage
    
    def set_outlet_power(self, id, power):
        self.outletPower[id] = power
        
        
    def voltage_update(self):
        voltageMessage = "0-228"
        return voltageMessage
      
        
    