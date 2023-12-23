#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Jon Levell <levell@uk.ibm.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# All rights reserved.

# This shows a example of an MQTT publisher with the ability to use
# user name, password CA certificates based on command line arguments

import paho.mqtt.client as mqtt
import os
import ssl
import argparse
import time
import logging
import json
import pygsheets
import pandas as pd
from datetime import datetime

from dotenv import load_dotenv



load_dotenv()
host = os.getenv("MQTT_BROKER_HOST")
port = int(os.getenv("MQTT_BROKER_PORT"))

username = os.getenv("MQTT_BROKER_USERNAME")
password = os.getenv("MQTT_BROKER_PASSWORD")


parser = argparse.ArgumentParser()

parser.add_argument('-H', '--host', required=False, default="mqtt.eclipseprojects.io")
parser.add_argument('-t', '--topic', required=False, default="paho/test/opts")
parser.add_argument('-q', '--qos', required=False, type=int,default=0)
parser.add_argument('-c', '--clientid', required=False, default=None)
parser.add_argument('-u', '--username', required=False, default=None)
parser.add_argument('-d', '--disable-clean-session', action='store_true', help="disable 'clean session' (sub + msgs not cleared when client disconnects)")
parser.add_argument('-p', '--password', required=False, default=None)
parser.add_argument('-P', '--port', required=False, type=int, default=None, help='Defaults to 8883 for TLS or 1883 for non-TLS')
parser.add_argument('-N', '--nummsgs', required=False, type=int, default=1, help='send this many messages before disconnecting') 
parser.add_argument('-S', '--delay', required=False, type=float, default=1, help='number of seconds to sleep between msgs') 
parser.add_argument('-k', '--keepalive', required=False, type=int, default=60)
parser.add_argument('-s', '--use-tls', action='store_true')
parser.add_argument('--insecure', action='store_true')
parser.add_argument('-F', '--cacerts', required=False, default=None)
parser.add_argument('--tls-version', required=False, default=None, help='TLS protocol version, can be one of tlsv1.2 tlsv1.1 or tlsv1\n')
parser.add_argument('-D', '--debug', action='store_true')

args, unknown = parser.parse_known_args()

args.host = host
args.port = port
args.username = username
args.password = password

nextPackage = 0

boxValueDict = {
    "Status":"S",
    "Power": "P",
    "Ampere": "A",
    "PowerMeter":"PM"
}

boxStatusDict = {
    'init': 'init',
    'online':'online',
    'offline':'offline'
}

arrayBoxStatusDict = {}
arrayBoxPowerDict = {}
arrayBoxPowerMeterDict = {}
arrayBoxNumberOfChargingOutlet = {}
arrayBoxNumberOfStrangeOutlet = {}
arrayBoxChargingOutlets = {}
arrayBoxStrangeOutlets = {}
arrayBoxPowerMeter = {}

isConnected = 0


logging.basicConfig(filename='app22.csv', filemode='a', format='%(asctime)s, %(message)s' , datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


import csv
 
filename ="boxes.csv"
 
# opening the file using "with"
# statement
boxes = []
with open(filename, 'r') as data:
  for line in csv.DictReader(data):
      boxes.append(line)
      
for box in boxes:
    print(box["BoxID"])
    print(box["BoxName"])
    print(box["PowerMeter"])


def initBoxStatus():
    print('Init Box Status!')
    for box in boxes:    
        arrayBoxStatusDict['S'+ box["BoxID"]] = boxStatusDict['init']
        arrayBoxPowerDict['P'+box["BoxID"]] = -1
        arrayBoxPowerMeterDict['PM'+box['BoxID']] = -1
 

def subscribeOneTopic(topic):
    mqttc.subscribe(topic, 0)
def unsubsribeOneTopic(topic):
    mqttc.unsubscribe(topic)
    
def subscribeAllTopics():
    for box in boxes:    
        topic = "S" + box["BoxID"]
        print(topic)
        subscribeOneTopic(topic)
        topic = "P" + box["BoxID"]
        print(topic)
        subscribeOneTopic(topic)
        
        # if(box["PowerMeter"] == '1'):
        #     topic = "PM" + box["BoxID"]
        #     print(topic)
        #     subscribeOneTopic(topic)

def subscribeAllStatusTopics():
    for box in boxes:    
        topic = "S" + box["BoxID"]
        print(topic)
        subscribeOneTopic(topic)

def unsubsribedAllStatusTopics():
    for box in boxes:    
        topic = "S" + box["BoxID"]
        print(topic)
        unsubsribeOneTopic(topic)
def subscribedAllPowerTopics():
    for box in boxes:    
        topic = "P" + box["BoxID"]
        print(topic)
        subscribeOneTopic(topic)
def unsubscribedAllPowerTopics():
    for box in boxes:    
        topic = "P" + box["BoxID"]
        print(topic)
        unsubsribeOneTopic(topic)



def checkBoxesStatus(msg):
    if('SEbox' in msg.topic):
        boxID = msg.topic.split(sep = "_")[-1]
        tempPayload = str(msg.payload.decode('utf-8'))
        boxStatus = tempPayload.split(sep=",")
        print(boxStatus[-1])
        if(boxStatus[-1] == '10-0'):
            # print('online')
            arrayBoxStatusDict[msg.topic] = boxStatusDict['online']
        else:
            # print('offline')
            arrayBoxStatusDict[msg.topic] = boxStatusDict['offline']
        arrayBoxNumberOfChargingOutlet[msg.topic] = 0
        arrayBoxChargingOutlets[msg.topic] = ""
        arrayBoxNumberOfStrangeOutlet[msg.topic] = 0
        arrayBoxStrangeOutlets[msg.topic] = ""
        
        for outletStatus in boxStatus:
            if(outletStatus.split(sep="-")[-1] == '2'):
                arrayBoxNumberOfChargingOutlet[msg.topic] += 1
                arrayBoxChargingOutlets[msg.topic] += outletStatus.split(sep="-")[0] + ","
            elif(outletStatus.split(sep="-")[-1] == '1' or outletStatus.split(sep="-")[-1] == '6' or outletStatus.split(sep="-")[-1] == '7' or outletStatus.split(sep="-")[-1] == '12'):
                arrayBoxNumberOfStrangeOutlet[msg.topic] += 1
                arrayBoxStrangeOutlets[msg.topic] += outletStatus.split(sep="-")[0] + "-" + outletStatus.split(sep="-")[-1] +  ","
                
        # print(f'arrayBoxNumberOfChargingOutlet[msg.topic] = {arrayBoxNumberOfChargingOutlet[msg.topic]}')
        # print(f'arrayBoxChargingOutlets[msg.topic] = {arrayBoxChargingOutlets[msg.topic]}')
        unsubsribeOneTopic(msg.topic)    
    
def isAllBoxStatusChecked():
    for box in boxes:  
        if(arrayBoxStatusDict['S'+box["BoxID"]] == boxStatusDict['init']):
            return False
    print(arrayBoxStatusDict)
    return True

def checkBoxesPowerConsumption(msg):
    if('PEbox' in msg.topic):
        print("receive PEbox data")
        boxID = msg.topic.split(sep = "_")[-1]
        tempPayload = str(msg.payload.decode('utf-8'))
        powerConsumption = tempPayload.split(sep=',')[-1].split(sep='-')[-1]
        arrayBoxPowerDict[msg.topic] = powerConsumption
        if(msg.topic == "PEbox_0089"):
            print("dslsjldfjslfkjsdf")
            print(tempPayload)
            print(powerConsumption)
            print("0298340238403928")
            
        unsubsribeOneTopic(msg.topic)   
def isAllBoxPowerChecked():
    for box in boxes: 
        if(arrayBoxPowerDict['P' + box["BoxID"]] == -1):
            return False
    print(arrayBoxPowerDict)
    return True

def checkBoxesPowerMeter(msg):
    if('PMEbox' in msg.topic):
        print("receive PMEbox data")
        boxID = msg.topic.split(sep = "_")[-1]
        tempPayload = str(msg.payload.decode('utf-8'))
        powerConsumption = tempPayload.split(sep=',')[-1]
        arrayBoxPowerDict[msg.topic] = powerConsumption
        unsubsribeOneTopic(msg.topic) 

def writeDataToGoogleSpreadSheet():
    try:
        gc = pygsheets.authorize(service_file='./creds1.json')

        # Create empty dataframe
        data = []
        for box in boxes:
            data.append({'BoxID':box["BoxID"],
                         'BoxName':box['BoxName'],
                         'Status': arrayBoxStatusDict['S' + box['BoxID']], 
                         'Number of chargers': arrayBoxNumberOfChargingOutlet['S' + box['BoxID']],
                         'Charging Outlets': arrayBoxChargingOutlets['S' + box['BoxID']],
                         'Power Consumption':arrayBoxPowerDict['P' + box['BoxID']], 
                         'Power Consumption kWh':round(float(arrayBoxPowerDict['P' + box['BoxID']])/(3600*1000),2), 
                         'Updated time': datetime.now(),
                         "Number of Issued Outlets": arrayBoxNumberOfStrangeOutlet['S' + box['BoxID']],
                         "Issued outlets": arrayBoxStrangeOutlets['S' + box['BoxID']]
                         })
        df = pd.DataFrame(data)
        print(df)
        print('Start update spreadsheet!')
        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        sh = gc.open('Ebox Data Gathering')

        #select the first sheet 
        wks = sh[1]

        #update the first sheet with df, starting at cell B2. 
        wks.set_dataframe(df,(1,1))
        # wks.append_table(value = df)
        
        print('Done update spreadsheet!')
    except:
        print('cannot update data to google spreadsheet')
        print('try another round')
    

def writeDataToGoogleSpreadSheet1():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
        ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("./creds1.json", scopes) #access the json key you downloaded earlier 
    file = gspread.authorize(credentials) # authenticate the JSON key with gspread
    sheet = file.open('Ebox Data Gathering') #open sheet
    sheet = sheet.sheet1 #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    
    sheet.update_cell(1, 1, 'BoxID') #updates row 1 on column 1
    sheet.update_cell(1, 2, 'BoxName') #updates row 1 on column 2
    sheet.update_cell(1, 3, 'Status') #updates row 1 on column 2
    sheet.update_cell(1, 4, 'PowerConsumption') #updates row 1 on column 2
    
    row = 2
    print('Start update google spreadsheet!')
    for box in boxes:
        print(f'box["BoxID"] = {box["BoxID"]}')
        print(f'box["BoxName"] = {box["BoxName"]}')
        sheet.update_cell(row,1, str(box["BoxID"]))
        sheet.update_cell(row,2, box['BoxName'])
        sheet.update_cell(row,3, arrayBoxStatusDict['S' + box['BoxID']])
        sheet.update_cell(row,4, arrayBoxPowerDict['P' + box['BoxID']])
        row = row + 1
    
    print('Done update google spreadsheet!')

def on_connect(mqttc, obj, flags, rc):
    print("connect rc: " + str(rc))


def on_message(mqttc, obj, msg):
    tempData = msg.topic + ", " + str(msg.qos) + ", " + str(msg.payload) 
    print(tempData)
    logging.info(tempData)
    checkBoxesStatus(msg)
    checkBoxesPowerConsumption(msg)


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print("nguyen" + string)

usetls = args.use_tls

if args.cacerts:
    usetls = True

port = args.port    
if port is None:
    if usetls:
        port = 8883
    else:
        port = 1883

mqttc = mqtt.Client(args.clientid,clean_session = not args.disable_clean_session)

if usetls:
    if args.tls_version == "tlsv1.2":
       tlsVersion = ssl.PROTOCOL_TLSv1_2
    elif args.tls_version == "tlsv1.1":
       tlsVersion = ssl.PROTOCOL_TLSv1_1
    elif args.tls_version == "tlsv1":
       tlsVersion = ssl.PROTOCOL_TLSv1
    elif args.tls_version is None:
       tlsVersion = None
    else:
       print ("Unknown TLS version - ignoring")
       tlsVersion = None

    if not args.insecure:
        cert_required = ssl.CERT_REQUIRED
    else:
        cert_required = ssl.CERT_NONE
        
    mqttc.tls_set(ca_certs=args.cacerts, certfile=None, keyfile=None, cert_reqs=cert_required, tls_version=tlsVersion)

    if args.insecure:
        mqttc.tls_insecure_set(True)

if args.username or args.password:
    mqttc.username_pw_set(args.username, args.password)

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

if args.debug:
    mqttc.on_log = on_log

print("Connecting to "+args.host+" port: "+str(port))
mqttc.connect(args.host, port, args.keepalive)








args.nummsgs = 10
args.delay = 2
# args.topic = "UEbox_0001"
# subscribeAllStatusTopics()
# subscribedAllPowerTopics()

count = 0
fsmState = 0
initBoxStatus()
mqttc.loop_start()
i = 0
while(i < 3):
    time.sleep(1)
    i = i + 1
    print(i)
while True:
    print(f'fsmState = {fsmState} count = {count}')
    if(fsmState == 0):
        subscribeAllTopics()
        fsmState = 1
        count = 0
    elif(fsmState == 1):
        count = count + 1
        if(isAllBoxStatusChecked() or count > 30):
            fsmState = 2
            count = 0
    elif(fsmState == 2):
        
        fsmState = 3
    elif(fsmState == 3):
        count = count + 1
        if(isAllBoxPowerChecked() or count > 30):
            fsmState = 4
    elif(fsmState == 4):
        print('all done')
        fsmState = 0
        i = 0
        writeDataToGoogleSpreadSheet()
        while(i < 60*15):
            time.sleep(1)
            i = i + 1
            if(i%60 == 0):
                print(i)
        initBoxStatus()
    time.sleep(args.delay)

print(str(countForPayload) + ":" + payload)
file.close()
infot = mqttc.publish(args.topic, payload, qos=args.qos)
infot.wait_for_publish()
time.sleep(args.delay)
# for x in range (0, args.nummsgs):
#     msg_txt = '{"msgnum": "'+str(x)+'"}'
#     print("Publishing: "+msg_txt)
#     infot = mqttc.publish(args.topic, msg_txt, qos=args.qos)
#     infot.wait_for_publish()

#     time.sleep(args.delay)

