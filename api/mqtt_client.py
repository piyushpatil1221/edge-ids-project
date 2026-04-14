import paho.mqtt.client as mqtt
import requests
import json

BROKER = "broker.hivemq.com"
TOPIC = "ids/data"

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        print("\n📩 Received:", data)

        response = requests.post(
            "http://127.0.0.1:5000/predict",
            json={"data": data}
        )

        result = response.json()

        if "message" in result:
            print("🤖 Prediction:", result["message"])
        else:
            print("❌ API Error:", result)

    except Exception as e:
        print("❌ MQTT Error:", e)

client = mqtt.Client()
client.connect(BROKER, 1883)
client.subscribe(TOPIC)
client.on_message = on_message

print("🚀 MQTT Client Running...")
client.loop_forever()