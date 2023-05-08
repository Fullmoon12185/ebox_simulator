

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

TIME_LOOP   = 0.01 #second
MCU_POWER_USAGE = 6


PUBLISH_DURATION = 3
DURATION_FROM_READY_TO_CHARGING = 10
DURATION_FOR_CHARGING_COMPLETE = 180
DURATION_AFTER_CHARGING_COMPLETE = 30

NUMBER_OF_OUTLET = 10

OUTLET_AVAILABLE = 0
OUTLET_READY = 1
OUTLET_CHARGING = 2
OUTLET_FULLCHARGE = 3


FSM_START_STATE = 0
FSM_READY_STATE = 1
FSM_CHARGING_STATE = 2
FSM_WAIT_FOR_CHARGING_COMPLETE = 3
FSM_CHARGING_COMPLETE = 4

FSMStateDict = {
  FSM_START_STATE: "FSM_START_STATE",
  FSM_READY_STATE: "FSM_READY_STATE",
  FSM_CHARGING_STATE: "FSM_CHARGING_STATE",
  FSM_WAIT_FOR_CHARGING_COMPLETE: "FSM_WAIT_FOR_CHARGING_COMPLETE",
  FSM_CHARGING_COMPLETE: "FSM_CHARGING_COMPLETE"
}


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
    
    powerTotal = 0
    outletStatus = []
    outletVoltage = 280
    outletCurrent = []
    
    outletPowerFactor = []
    outletPower = []
    
    previousFSMState = []
    FSMState = []
    outletLastTime = []
    outletCurrentTime = []
    
    updateDataLastTime = 0
    updateDataCurrentTime = 0
    
    eboxId = 0
    
    counter = 0
    topicIndex = 0
    
    lastPublishTime = 0
    currentPublishTime = 0
    
    def on_connect(self, mqttc, obj, flags, rc):
        self.printCustom("rc: "+str(rc))

    def on_connect_fail(self, mqttc, obj):
        self.printCustom("Connect failed")

    def on_message(self, mqttc, obj, msg):
        # self.printCustom("Nguyen....")
        self.printCustom(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.processCommand(msg.topic, msg.payload)
        

    def on_publish(self, mqttc, obj, mid):
        # self.printCustom("mid: "+str(mid))
        pass

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        self.printCustom("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        # self.printCustom("N1...")
        # self.printCustom(string)
        pass


    def run(self, host, port, username, password, ebox_id):
        self.username_pw_set(username, password)
        self.connect(host, port, 60)
        topic = "CEbox_" + str(ebox_id)
        self.subscribe(topic, 0)
        self.eboxId = ebox_id
        
        self.box_initialization()
    
    
    def box_initialization(self):
        for i in range(0,NUMBER_OF_OUTLET+1):
            self.outletStatus.append(OUTLET_AVAILABLE)
            self.outletCurrent.append(0)
            self.outletPowerFactor.append(0)
            self.outletPower.append(0)
            
            self.FSMState.append(0)
            self.previousFSMState.append(-1)
            
            self.outletLastTime.append(0)
            self.outletCurrentTime.append(0)
            
            
        self.topic_intialization(self.eboxId)
        
    def topic_intialization(self, box_id):
        self.STATUS_TOPIC = "SEbox_" + str(box_id)
        self.CURRENT_TOPIC = "AEbox_" + str(box_id)
        self.VOLTAGE_TOPIC = "VEbox_" + str(box_id)
        self.POWER_TOPIC = "PEbox_" + str(box_id)
        self.POWER_FACTOR_TOPIC = "PFEbox_" + str(box_id)    
        
        
    def running(self):
        self.loop()
        time.sleep(TIME_LOOP)
        self.appPublishData()
        self.updateOutletState()
        self.displayOutletState(0)
        self.updateOutletData()
        
        
        
    def printCustom(self, message):
        print(f'[{self.eboxId}] - {message}')    
    
    
    def updateOutletStateLastTime(self, id):
        self.outletLastTime[id] = time.time()
        
        
    def isTimeElapseDuration(self, id, duration):
        self.outletCurrentTime[id] = time.time()
        if(self.outletCurrentTime[id] - self.outletLastTime[id] > duration):
            self.outletLastTime[id] = self.outletCurrentTime[id]
            return True
        return False
    
    def displayOutletState(self, id):
        if(self.FSMState[id] != self.previousFSMState[id]):
            self.printCustom(f'outelt [{id}] state = {FSMStateDict[self.FSMState[id]]}')
            self.previousFSMState[id] = self.FSMState[id]
    
    
    def updateOutletCurrent(self, id, current):
        if(id >= NUMBER_OF_OUTLET):
            return

        self.outletCurrent[id] = current
    
    def updateOutletPowerFactor(self, id, pf):
        if(id >= NUMBER_OF_OUTLET):
            return

        self.outletPowerFactor[id] = pf
    
    
    def updateOutletPower(self, id):
        if(id >= NUMBER_OF_OUTLET):
            return
        if(self.outletStatus[id] == OUTLET_CHARGING):
            self.outletPower[id] = self.outletPower[id] + self.outletCurrent[id]*self.outletVoltage*self.outletPowerFactor[id]/1000
        else: 
            self.outletPower[id] = 0
        return self.outletPower[id]
    def updatePowerTotal(self, power):
        self.powerTotal = self.powerTotal + power
        self.outletPower[NUMBER_OF_OUTLET] = self.powerTotal
    
    def updateOutletData(self):
        self.updateDataCurrentTime = time.time()
        if(self.updateDataCurrentTime - self.updateDataLastTime > 1.0):
            self.updateDataLastTime = self.updateDataCurrentTime
            self.updatePowerTotal(MCU_POWER_USAGE)
            self.outletCurrent[NUMBER_OF_OUTLET] = 0
            for id in range(NUMBER_OF_OUTLET):
                self.updatePowerTotal(self.updateOutletPower(id))
                self.outletCurrent[NUMBER_OF_OUTLET] += self.outletCurrent[id]
            pass
    def updateOutletState(self):
        for id in range(0, NUMBER_OF_OUTLET):
            if(self.FSMState[id] == FSM_START_STATE):
                if(self.outletStatus[id] == OUTLET_READY):
                    self.FSMState[id] = FSM_READY_STATE
            elif(self.FSMState[id] == FSM_READY_STATE):
                if(self.isTimeElapseDuration(id, DURATION_FROM_READY_TO_CHARGING)):
                    self.FSMState[id] = FSM_CHARGING_STATE
                    self.outletCharging(id)
            elif(self.FSMState[id] == FSM_CHARGING_STATE):
                self.FSMState[id] = FSM_WAIT_FOR_CHARGING_COMPLETE
            elif(self.FSMState[id] == FSM_WAIT_FOR_CHARGING_COMPLETE):
                if(self.isTimeElapseDuration(id, DURATION_FOR_CHARGING_COMPLETE)):
                    self.outletFullCharge(id)
                    self.FSMState[id] = FSM_CHARGING_COMPLETE
            elif(self.FSMState[id] == FSM_CHARGING_COMPLETE):
                if(self.isTimeElapseDuration(id, DURATION_AFTER_CHARGING_COMPLETE)):
                    self.outletAvailable(id)
                    self.FSMState[id] = FSM_START_STATE
                
                    
                
                
    def appPublishData(self):
        self.currentPublishTime = time.time()
        if(self.currentPublishTime - self.lastPublishTime >= PUBLISH_DURATION):
            self.lastPublishTime = self.currentPublishTime
            
            self.printCustom(f'topicIndex = {self.topicIndex}')
            
            
            if(self.topicIndex == 0):
                self.publish_ebox_statuses()
            elif(self.topicIndex == 1):
                self.publish_ebox_currents()
            elif(self.topicIndex == 2):
                self.publish_ebox_power_factors()
            elif(self.topicIndex == 3):
                self.publish_ebox_powers()
            elif(self.topicIndex == 4):
                self.publish_ebox_voltage()
            self.topicIndex = (self.topicIndex + 1)%5
    
    
    def clearOutletPower(self, id):
        if(id < NUMBER_OF_OUTLET):
            self.outletPower[id] = 0
        
    def clearTopicIndex(self):
        self.topicIndex = 0
        
    def processCommand(self, topic, payload):
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
        self.publish(self.STATUS_TOPIC,self.statuses_update(), retain=True)
    def publish_ebox_currents(self):
        # Publish message to MQTT Broker
        self.publish(self.CURRENT_TOPIC,self.currents_update(), retain=True)
    def publish_ebox_power_factors(self):
        # Publish message to MQTT Broker
        self.publish(self.POWER_FACTOR_TOPIC,self.power_factors_update(), retain=True)
    def publish_ebox_powers(self):
        # Publish message to MQTT Broker
        self.publish(self.POWER_TOPIC,self.powers_update(), retain=True)
        
    
    def publish_ebox_voltage(self):
        # Publish message to MQTT Broker
        self.publish(self.VOLTAGE_TOPIC,self.voltage_update(), retain=True)    
        
    

    def statuses_update(self):
        statusMessage = ""
        for id in range (0, NUMBER_OF_OUTLET):
            statusMessage = statusMessage +  str(id) + '-' + str(self.outletStatus[id]) + ','	
        
        statusMessage = statusMessage +  str(NUMBER_OF_OUTLET) + '-' + str(self.outletStatus[NUMBER_OF_OUTLET])
        self.printCustom(f'statusMessage = {statusMessage}')
        return statusMessage    
    
    
    
    def set_outlet_status(self, id, status):
        self.outletStatus[id] = status
        self.clearTopicIndex()
    
    def outletAvailable(self, id):
        self.printCustom(f'Outlet [{id} is available]')
        self.set_outlet_status(id, OUTLET_AVAILABLE)
        self.updateOutletCurrent(id, 0)
        self.updateOutletPowerFactor(id, 0)
        self.updateOutletPower(0)
        
        
    def outletReady(self, id):
        self.printCustom(f'Outlet [{id} is ready]')
        self.set_outlet_status(id, OUTLET_READY)
        self.updateOutletStateLastTime(id)
        
        
    def outletCharging(self, id):
        self.printCustom(f'Outlet [{id} is charging]')
        self.set_outlet_status(id, OUTLET_CHARGING)
        self.updateOutletCurrent(id, 1000)
        self.updateOutletPowerFactor(id, 50)
                
                
        
    
    def outletFullCharge(self, id):
        self.printCustom(f'Outlet [{id} is ful charge]')
        self.set_outlet_status(id, OUTLET_FULLCHARGE)
    
    
    def currents_update(self):
        currentMessage = ""
        for id in range (0, NUMBER_OF_OUTLET):
            currentMessage = currentMessage +  str(id) + '-' + str(self.outletCurrent[id]) + ','	
       
        currentMessage = currentMessage + str(NUMBER_OF_OUTLET) + '-' + str(self.outletCurrent[NUMBER_OF_OUTLET])
        self.printCustom(f'current = {currentMessage}')
        return currentMessage 

    def power_factors_update(self):
        powerFactorMessage = ""
        for id in range (0, NUMBER_OF_OUTLET):
            powerFactorMessage = powerFactorMessage +  str(id) + '-' + str(self.outletPowerFactor[id]) + ','	
        powerFactorMessage = powerFactorMessage +  str(NUMBER_OF_OUTLET) + '-' + str(self.outletPowerFactor[NUMBER_OF_OUTLET])
        self.printCustom(f'powerFactor = {powerFactorMessage}')
        return powerFactorMessage
    
    def set_outlet_power_factor(self, id, powerFactor):
        self.outletPowerFactor[id] = powerFactor
        
        
    def powers_update(self):
        powerMessage = ""
        for id in range (0, NUMBER_OF_OUTLET):
            powerMessage = powerMessage +  str(id) + '-' + str(self.outletPower[id]) + ','	
        
        powerMessage = powerMessage +  str(NUMBER_OF_OUTLET) + '-' + str(self.outletPower[NUMBER_OF_OUTLET])
        self.printCustom(f'power = {powerMessage}')
        return powerMessage
    
    def set_outlet_power(self, id, power):
        self.outletPower[id] = power
        
        
    def voltage_update(self):
        voltageMessage = "0-228"
        self.printCustom(f'voltage = {voltageMessage}')
        return voltageMessage
      
        
    