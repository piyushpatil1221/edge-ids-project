import paho.mqtt.client as mqtt
import json
import random
import time

BROKER = "broker.hivemq.com"
TOPIC = "ids/data"

client = mqtt.Client()
client.connect(BROKER, 1883)

while True:
    # Generate random data (100 features approx)
    data = [random.randint(0, 100) for _ in range(120)]

    client.publish(TOPIC, json.dumps(data))
    print("📤 Sent:", data[:5], "...")

    time.sleep(2)