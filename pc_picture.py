import paho.mqtt.client as mqtt
import base64

BROKER = "192.168.1.7"
PORT = 1883
TOPIC_DEFAULT = "esp32cam/status"
TOPIC = "esp32cam/picture"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC)
        client.subscribe(TOPIC_DEFAULT)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print("Message received on topic ")
    print(f"{msg.topic}")
    if msg.topic == TOPIC:
        try:
            with open("received_image.jpg", "wb") as image_file:
                image_file.write(msg.payload)
            print("Image saved as 'received_image.jpg'")
        except Exception as e:
            print(f"Failed to save image: {e}")
    else:
        print("Default mesage got.")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker...")
client.connect(BROKER, PORT, 60)

try:
    print(f"Listening for messages on topic '{TOPIC}'...")
    client.loop_forever()
except KeyboardInterrupt:
    print("\nDisconnecting from broker...")
    client.disconnect()
