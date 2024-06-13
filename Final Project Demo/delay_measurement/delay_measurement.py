import time
from function import *
import paho.mqtt.client as mqtt
import serial

# Variabel MQTT
client = mqtt.Client()

mqttBroker = "broker.mqtt-dashboard.com"
port = 1883

# Setting MQTT
client.connect(mqttBroker, port)
array = [0, 165, 15, 150, 30, 135, 45, 120, 60, 105, 75, 90]
# array = [15]
code = 'mqt'

# membuat komunikasi pyserial dengan python
ser = serial.Serial('/dev/cu.usbserial-1410', 9600) # serial.Serial(port, baundrate)

time.sleep(1)

for i in array:
    angle = [i, 90, 90, 90]
    local_time = time.localtime(time.time())
    print("Waktu lokal saat ini:", time.strftime("%Y-%m-%d %H:%M:%S", local_time))
    if code == "mqtt":
        client.publish("dajjal123", arrToString(angle))
    else:
        ser.write(arrToString(angle).encode('utf-8'))
    time.sleep(0.1)
