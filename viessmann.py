#!/usr/bin/python3
#
# Script to get data from Viessmann API Server and store it in InfluxDB and/or send it to Domoticz (via MQTT)
# 
# Requires:
#    1. Viessmann developer's portal access (to get API key)
#    2. Boiler gateway (wifi module) SN, device ID, boiler SN
#    3. Access refresh code - to be obtained only via http browser
#    4. Refresh token (use get_refresh_token.sh to obtain)
# In order to obtain required data - please read manual: https://developer.viessmann.com/en/doc/getting-started
#
# Author: Michalux
# Version: 3.0
#

import time
import configparser
import urllib3
from urllib.parse import urlencode
import json
import os.path
import sys
import datetime
from datetime import datetime
from influxdb import InfluxDBClient
import paho.mqtt.client as paho

# Refresh access token
def Refresh_Token(clid, reftkn):
    data = {
             'grant_type': 'refresh_token',
             'client_id': clid,
             'refresh_token': reftkn
           }
    encoded_data = urlencode(data)
    header.add("Content-Type", "application/x-www-form-urlencoded")
    URL="https://iam.viessmann.com/idp/v2/token?"
    token_resp = http.request('POST', URL+encoded_data, headers=header)
    header.discard("Content-Type")
    tokend = json.loads(token_resp.data)
    try:
        new_token = tokend["access_token"]
    except:
        print("Problem getting new token:")
        print(json.dumps(tokend, indent=4, sort_keys=False, ensure_ascii=False))
        sys.exit(1)
    return new_token

# Prepare data to write do InfluxDB
def PrepareInfluxData(IfData, fieldname, fieldvalue):
    IfData[0]["fields"][fieldname] = float(fieldvalue)
    return IfData

def Write2InfluxDB(IfData):
    ifclient.write_points(IfData)

def PrepareDomoticzData(DData, idx, svalue):
  if isinstance(svalue, str):
    DData.append('{ "idx": '+str(idx)+', "svalue": '+ svalue +' }')
  else:
    DData.append('{ "idx": '+str(idx)+', "svalue": "'+ str(svalue) +'" }')
  return DData

os.chdir(os.path.dirname(sys.argv[0]))

# CONFIG
configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

INSTID=configParser.get('Viessmann', 'Installation_ID')
GWSN=configParser.get('Viessmann', 'Gateway_SN')
DEVICEID=configParser.get('Viessmann', 'Device_ID')
BOILERSN=configParser.get('Viessmann', 'Boiler_SN')
CLIENT_ID=configParser.get('Viessmann', 'Client_ID')
REFRESH_TOKEN=configParser.get('Viessmann', 'Refresh_Token')
INFLUXDB = configParser.get("InfluxDB", "influxdb")
IFHOST = configParser.get("InfluxDB", "influxdb_host")
IFPORT = configParser.get("InfluxDB", "influxdb_port")
IFUSER = configParser.get("InfluxDB", "influxdb_user")
IFPASS = configParser.get("InfluxDB", "influxdb_password")
IFDB = configParser.get("InfluxDB", "influxdb_dbname")
verbose = configParser.get("General", "verbose")
termout = configParser.get("General", "terminal_output")
mqtt=int(configParser.get('MQTT', 'mqtt'))
mqtt_server=configParser.get('MQTT', 'mqtt_server')
mqtt_port=int(configParser.get('MQTT', 'mqtt_port'))
mqtt_topic=configParser.get('MQTT', 'mqtt_topic')
mqtt_username=configParser.get('MQTT', 'mqtt_username')
mqtt_passwd=configParser.get('MQTT', 'mqtt_passwd')
mqtt_tls=configParser.get('MQTT', 'mqtt_tls')
mqtt_tls_insecure=configParser.get('MQTT', 'mqtt_tls_insecure')
mqtt_tls_ver=int(configParser.get('MQTT', 'mqtt_tls_version'))
mqtt_cacert=configParser.get('MQTT', 'mqtt_cacert')
DomoticzData=[]

# Get parameter's definitions to monitor
with open("./params.json") as paramfile:
    params=json.loads(paramfile.read())

# Initialise InfluxDB support
if INFLUXDB == "1":
    timestamputc = str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    ifclient = InfluxDBClient(IFHOST, IFPORT, IFUSER, IFPASS, IFDB)
    InfluxData = [{"measurement": "BoilerData", "time": timestamputc, "fields": {}}]

# Initialise HTTP Manager
http = urllib3.PoolManager()
header = urllib3._collections.HTTPHeaderDict()

TIMESTAMP = time.time()

if os.path.isfile('token.json') and os.path.getsize('token.json')>2000:     # Check if token file exists and is big enough
    with open('token.json') as token_file:
        token_data = json.load(token_file)
        TOKEN_TIMESTAMP = token_data["Timestamp"]
        TOKEN = token_data["Token"]
        token_file.close()
else:
    TOKEN_TIMESTAMP=TIMESTAMP-3700                                          # Enforce refreshed token generation (token lifetime = 3600s)

if (TOKEN_TIMESTAMP+3500) < TIMESTAMP:
    if verbose=="1":
        print("** Old token has expired, requesting a new one **")
    TOKEN = Refresh_Token(CLIENT_ID, REFRESH_TOKEN)                         # Get new, refreshed token
    tdata = {
             "Timestamp" : TIMESTAMP,
             "Token": TOKEN
            }
    with open('token.json', 'w') as token_file:
        json.dump(tdata, token_file)                                        # Write new, refreshed token to a file
        token_file.close()

# Get data from Viessmann API Server
header.add("Authorization", "Bearer "+TOKEN)
URL='https://api.viessmann.com/iot/v1/equipment/installations/'+INSTID+'/gateways/'+GWSN+'/devices/'+DEVICEID+'/features/'
apiresponse = http.request('GET', URL, headers=header)
response = json.loads(apiresponse.data)

if "viErrorId" in response:
        print("** Error getting boiler data: **")
        print(json.dumps(response, indent=4, sort_keys=False, ensure_ascii=False))
        sys.exit(1)

if verbose=="1":
    print("** Viessmann API server response: **")
    print(json.dumps(response, indent=4, sort_keys=False, ensure_ascii=False))

# Parse Viessmann response
for visdata in response["data"]:
    for param in params:
        if params[param]["Feature"] == visdata["feature"]:
            if isinstance(visdata["properties"][params[param]["Key"]]["value"], list):
                params[param]["Value"] = visdata["properties"][params[param]["Key"]]["value"][0]
                if termout=="1":
                    print(params[param]["Name"]+":",params[param]["Value"], params[param]["Unit"])
            else:
                params[param]["Value"] = visdata["properties"][params[param]["Key"]]["value"]
                if termout=="1":
                    print(params[param]["Name"]+":",params[param]["Value"], params[param]["Unit"])
            if (mqtt==1 and params[param]["DomoticzIdx"]!=0):
              PrepareDomoticzData(DomoticzData, params[param]["DomoticzIdx"], params[param]["Value"])
            if INFLUXDB=="1":
              PrepareInfluxData(InfluxData, param, params[param]["Value"])

# Write data to Influx Database
if INFLUXDB=="1":
    Write2InfluxDB(InfluxData)
    if verbose=="1":
        print("** Data written to InfluxDB: **")
        print(json.dumps(InfluxData, indent=4, sort_keys=False, ensure_ascii=False))

# Write data to MQTT
if mqtt==1:
  # Initialise MQTT connection
  client=paho.Client("ViessmannMonitor")
  if mqtt_tls=="1":
    client.tls_set(mqtt_cacert,tls_version=mqtt_tls_ver)
    client.tls_insecure_set(mqtt_tls_insecure)
  client.username_pw_set(username=mqtt_username, password=mqtt_passwd)
  client.connect(mqtt_server, mqtt_port)
  # Send data to MQTT/Domoticz
  client.loop_start()
  for mqtt_data in DomoticzData:
    result=client.publish(mqtt_topic, mqtt_data, retain=True)
    result.wait_for_publish()
    if not result.is_published:
      print("Error publishing data for Domoticz to MQTT")
  client.loop_stop()
  client.disconnect()
