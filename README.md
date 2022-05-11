# Viessmann integration with InfluxDB and Domoticz
Small utility to get Viessmann boiler data via Viessmann API Gateway.

# Requirements
```
1. Viessmann boiler with network (i.e. wifi) interface/gateway
2. Viessmann boiler installation ID
3. Viessmann boiler gateway serial number
4. Viessmann boiler serial number
5. Viessman developer portal cliend ID
6. Viessmann authorization refresh token
7. Python 3, required modules:
   urllib3
   paho-mqtt
   influxdb-client
Boiler installation ID, gateway SN and boiler SN can be found on boiler itself (look for some kind of sticker on it) or in Viessman mobile app (Settings->Devices).
To get developer portal client ID register on https://developer.viessmann.com and create client profile/device.
To get authorization refresh token use get_refresh_token.sh (please read manual inside it, before using !)
```
# Configuration
Edit the config.cfg and enter the following data:
```
[Viessmann]
Installation_ID=                # Boiler installation ID
Gateway_SN=                     # Boiler's network gateway SN
Device_ID=0                     # Boiler device ID - if You have one device it wil be 0
Boiler_SN=                      # Boiler SN
Client_ID=                      # Viessmann api client id
Refresh_Token=                  # Viessmann apl refresh authorization token

[InfluxDB]
influxdb=0                      # set to 1 to export data to InfluxDB
influxdb_host=                  # InfluxDB host (i.e. 127.0.0.1)
influxdb_port=8086              # InfluxDB port
influxdb_user=                  # InfluxDB user with permisions to read/write from/to dbname
influxdb_password=              # User password
influxdb_dbname=                # Database name (needs to be created upfront manually)

[General]
verbose=1                       # Print verbose data to console (i.e. full Viessmann api response)
terminal_output=0               # Pring boiler data to console

[MQTT]
mqtt=0                          # 0: disabled, 1: enabled. Enable for Domoticz support
mqtt_server=                    # MQTT server IP address
mqtt_port=1883                  # MQTT server tcp port
mqtt_topic=                     # MQTT topic name for basic output
mqtt_username=                  # MQTT access username
mqtt_passwd=                    # MQTT user password
mqtt_tls=0                      # Set to 1 to enable TLS support
mqtt_tls_insecure=True          # Set to False to enable strict server's certificate hostname matching
mqtt_tls_version=2              # 1 or 2
mqtt_cacert=                    # CA certificate path/filename

# Language version
Currently utility reports in polish, but if You want any other language, please change "Name" values in params.json

# Run
```
bash:/python3 viessmann.py (or ./viessmann.py)
CWU - zużycie energii: 0 kWh
Zużycie gazu - ogrzewanie podłogowe: 0 m3
Temperatura zewnętrzna: 24.6 ºC
Temperatura CWU: 49.7 ºC
Całkowite zużycie gazu: 0.4 m3
Zużycie gazu - CWU: 0.4 m3
Temperatura wody na zasilaniu: 58.9 ºC
Temperatura na zasilaniu ogrzewawania podłogowego: 21.6 ºC
Całkowite zużycie energii: 0 kWh
Ogrzewanie - zużycie energii: 0 kWh

# Known issues
You tell me :)

# Contrib
Feel free to suggest :) If You want to rewrite or/add change anything - please fork Your own project.

# Domoticz support
```
1. Install Mosquitto MQTT server
2. Add MQTT Client Gateway with LAN interface in Domoticz Hardware
3. Add virutal devices in Domoticz, write down their idx numbers.
4. Input Domoticz devices idx in params.json for each parameter You want to be reported to Domoticz
5. Configure MQTT parameters in config.cfg (use Topic In Prefix configured in Domoticz)
```

# InfluxDB support
```
1. Create database in InfluxDB
2. Configure InfluxDB parameters in config.cfg
3. All parameters defined in params.json will be written to InfluxDB
```
Enjoy :)
