import paho.mqtt.client as mqtt
import json
import time
import pandas as pd

BROKER = "broker.hivemq.com"
TOPIC = "ids/data"

client = mqtt.Client()
client.connect(BROKER, 1883)

print("🚀 Dataset Publisher Running...")

# Load dataset
df = pd.read_csv("../data/KDDTrain+_20Percent.txt", header=None)

while True:
    # Pick random row
    row = df.sample(1).values[0]

    payload = {
        "duration": str(row[0]),
        "protocol_type": row[1],
        "service": row[2],
        "flag": row[3],
        "src_bytes": str(row[4]),
        "dst_bytes": str(row[5])
    }

    client.publish(TOPIC, json.dumps(payload))

    print("📤 Sent:", payload)

    time.sleep(2)