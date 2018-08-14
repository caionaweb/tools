#!/usr/bin/python
import paho.mqtt.client as paho
import os
import socket
import ssl
from time import sleep
import Adafruit_DHT
import RPi.GPIO as GPIO
from random import uniform
import random
import json
import logging
logging.basicConfig(level=logging.INFO)

#valores dos BCM
pin_led_red = 7
pin_led_green = 23
pin_sensor_luz = 4
pin_umi_temp = 25
pin_motor = 17

sensor_umi = Adafruit_DHT.DHT11

resposta = ""


#variaveis para acionamento do motor
deg_0_pulse   = 0.5 
deg_180_pulse = 2.5
f = 50.0
#calculos para acionamento geral do motor
period = 1000/f
k      = 100/period
deg_0_duty = deg_0_pulse*k
pulse_range = deg_180_pulse - deg_0_pulse
duty_range = pulse_range * k


class PubSub(object):

    def __init__(self, listener = False, topic = "default"):
        self.connect = False
        self.listener = listener
        self.topic = topic
        self.logger = logging.getLogger(repr(self))

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True
        
        if self.listener:
            self.mqttc.subscribe(self.topic)

  #      self.logger.debug("{0}".format(rc))
#        print("{0}".format(rc)) #send mensagem

    def comando(valor):
        vai = valor

    def __on_message(self, client, userdata, msg):
  #      self.logger.info("{0}, {1} - {2}".format(userdata, msg.topic, msg.payload))
        json_object = json.loads(msg.payload)
        global resposta
        resposta = json_object['message']
  #  def __on_log(self, client, userdata, level, buf):
  #      self.logger.debug("{0}, {1}, {2}, {3}".format(client, userdata, level, buf))
  #      print("") #escrita do log no console

    def bootstrap_mqtt(self):

        self.mqttc = paho.Client()
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.__on_message
   #     self.mqttc.on_log = self.__on_log

        awshost = "a3ieienozmkv8m.iot.us-west-2.amazonaws.com"
        awsport = 8883

        caPath = "./ca.pem.crt"
        certPath = "./certificate.pem"
        keyPath = "./private_key.pem"

        self.mqttc.tls_set(caPath, 
            certfile=certPath, 
            keyfile=keyPath, 
            cert_reqs=ssl.CERT_REQUIRED, 
            tls_version=ssl.PROTOCOL_TLSv1_2, 
            ciphers=None)

        result_of_connection = self.mqttc.connect(awshost, awsport, keepalive=120)

        if result_of_connection == 0:
            self.connect = True

        return self

    def start(self):
        self.mqttc.loop_start()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(pin_led_red, GPIO.OUT)
        GPIO.setup(pin_led_green, GPIO.OUT)
        GPIO.output(pin_led_green, GPIO.HIGH)

        while True:
            sleep(2)
    
            umid, temp = Adafruit_DHT.read_retry(sensor_umi, pin_umi_temp)

            if(temp >= 30):
                #liga led vermelho
                GPIO.output(pin_led_red, GPIO.HIGH)
                #liga motor
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(pin_motor,GPIO.OUT)
                pwm = GPIO.PWM(pin_motor,f)
                pwm.start(0)
                #angulo do servo motor
                def set_angle(angle):
                    duty = deg_0_duty + (angle/180.0)* duty_range
                    pwm.ChangeDutyCycle(duty)
                #fazer async aqui
                for x in range(0, 2):
                    #angulo random para testes
                    angle = random.randint(1,180)
                    set_angle(angle)
                    sleep(1)
            else:
                GPIO.output(pin_led_red, GPIO.LOW)
                GPIO.cleanup(pin_motor)
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin_sensor_luz,GPIO.IN)

            if GPIO.input(pin_sensor_luz) == 0:
                lumi =  'Claro'
            if GPIO.input(pin_sensor_luz) == 1:
                lumi = 'Escuro'

            if self.connect == True:
                self.mqttc.publish("Temperatura/Atual", json.dumps({"message": temp}), qos=1)
		self.mqttc.publish("Umidade/Atual", json.dumps({"message": umid}), qos=1)
                self.mqttc.publish("Luminosidade/Atual", json.dumps({"message": lumi}), qos=1)
                print(temp)
                print(umid)
                print(lumi)
            else:
                self.logger.debug("Attempting to connect.")

if __name__ == '__main__':
    
    PubSub(listener = True, topic = "chat-evets").bootstrap_mqtt().start()
