import paho.mqtt.client as mqtt

client = mqtt.Client(client_id="pub", clean_session=False)
client.connect("62.210.99.83", 1883, 60)
client.publish(topic='Led/Status', qos=1, payload="Desligado")
client.loop()
