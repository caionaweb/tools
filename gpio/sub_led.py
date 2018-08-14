import RPi.GPIO as GPIO
import time
import sys
import paho.mqtt.client
pin_led = 18

def on_connect(client, userdata, flags, rc):
	print('connected (%s)' % client._client_id.decode())
	client.subscribe(topic='Led/Status', qos=2)

def on_message(client, userdata, message):
	print('------------------------------')
	print('Topico: ' + message.topic.decode())
	print('Status: ' + message.payload.decode())
	status = message.payload.decode()
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(pin_led, GPIO.OUT)
	
	if(status == "Ligado"):
		GPIO.output(pin_led, GPIO.HIGH)
	if(status == "Desligado"):
		GPIO.output(pin_led, GPIO.LOW)
		

def main():
	client = paho.mqtt.client.Client(client_id='client3', clean_session=False)
	client.on_connect = on_connect
	client.on_message = on_message
	client.username_pw_set('caio', 'senha')
	client.connect(host='192.168.20.105', port=1883)
	client.loop_forever()

if __name__ == '__main__':
	main()
	sys.exit(0)
