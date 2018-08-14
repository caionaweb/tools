import sys
import paho.mqtt.client
import paho.mqtt.publish

def on_connect(client, userdata, flags, rc):
	print('connected')

def main():
	paho.mqtt.publish.single(
		topic='Led/Status',
		payload=123,
		qos=1,
		hostname='192.168.20.105',
		port=1883,
		client_id='server1',
		auth={
			'username': 'caio',
			'password': 'senha'
		}
	)

if __name__ == '__main__':
	while True:
		main()
	sys.exit(0)
