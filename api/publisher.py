import paho.mqtt.client as mqtt
import json
import time

BROKER = "broker.hivemq.com"
TOPIC = "ids/data"

client = mqtt.Client()
client.connect(BROKER, 1883)

# 🔥 Sample real test rows from NSL-KDD
dataset = [
    "0,tcp,private,REJ,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,229,10,0.00,0.00,1.00,1.00,0.04,0.06,0.00,255,10,0.04,0.06,0.00,0.00,0.00,0.00,1.00,1.00,neptune,21",
    "2,tcp,ftp_data,SF,12983,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0.00,0.00,0.00,0.00,1.00,0.00,0.00,134,86,0.61,0.04,0.61,0.02,0.00,0.00,0.00,0.00,normal,21",
    "0,icmp,eco_i,SF,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,65,0.00,0.00,0.00,0.00,1.00,0.00,1.00,3,57,1.00,0.00,1.00,0.28,0.00,0.00,0.00,0.00,saint,15"
]

while True:
    for row in dataset:
        values = row.split(",")

        # ❌ remove last 2 columns (attack + level)
        features = values[:-2]

        # send as JSON list
        payload = json.dumps(features)

        client.publish(TOPIC, payload)

        print("📤 Sent:", features[:5], "...")

        time.sleep(2)