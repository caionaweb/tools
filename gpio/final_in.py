#!/usr/bin/python
import paho.mqtt.client as paho
import os
import socket
import ssl
import json
import RPi.GPIO as GPIO
import random
import time

#valores dos BCM
pin_motor = 17
pin_led_red = 7
pin_led_green = 23

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


def on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc) )
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("LedRed/Status", 1)
    client.subscribe("LedGreen/Status", 1)
    client.subscribe("Motor/Status", 1)
    client.subscribe("All/Status", 1)

def on_message(client, userdata, msg):
#    print("topic: "+msg.topic)
    json_object = json.loads(msg.payload)
    status = json_object['message']

    if(msg.topic == "LedRed/Status"):
        print("Luz Vermelha, Status: " + status)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(pin_led_red, GPIO.OUT)
        if(status == "Ligado"):
            GPIO.output(pin_led_red, GPIO.HIGH)
        if(status == "Desligado"):
            GPIO.output(pin_led_red, GPIO.LOW)

    if(msg.topic == "LedGreen/Status"):
        print("Luz Verde, Status: " + status)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(pin_led_green, GPIO.OUT)
        if(status == "Ligado"):
            GPIO.output(pin_led_green, GPIO.HIGH)
        if(status == "Desligado"):
            GPIO.output(pin_led_green, GPIO.LOW)

    if(msg.topic == "Motor/Status"):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_motor,GPIO.OUT)
        pwm = GPIO.PWM(pin_motor,f)
        pwm.start(0)
        #angulo do servo motor
        def set_angle(angle):
            duty = deg_0_duty + (angle/180.0)* duty_range
            pwm.ChangeDutyCycle(duty)
        print("Motor, Status: " + status)
        if(status == "Ligado"):
            #fazer async aqui
            for x in range(0, 10):
           # while status == "Ligado":
                #angulo random para testes
                angle = random.randint(1,180)
                set_angle(angle)
                time.sleep(1)
               # mqttc.loop_forever()
           # GPIO.cleanup(pin_motor)                
        if(status == "Desligado"):
            GPIO.cleanup(pin_motor)


mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
#mqttc.on_log = on_log

awshost = "a3ieienozmkv8m.iot.us-west-2.amazonaws.com"
awsport = 8883
clientId = "myThingName"
thingName = "myThingName"
caPath = "./ca.pem.crt"
certPath = "./certificate.pem"
keyPath = "./private_key.pem"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_forever()
