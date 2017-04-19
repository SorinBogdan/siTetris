from time import sleep
import os
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN, pull_up_down=GPIO.PUD_UP)


while True:
    if GPIO.input(4) == False:
        print("apasat")
    else:
        print("neapasat")
    sleep(0.1)
