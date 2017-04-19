from time import sleep
import os
import RPi.GPIO as GPIO

BTN_LEFT    = 26
BTN_RIGHT   = 13
BTN_ROTATE  = 19
BTN_NOBUTTON= 0

def initButtons():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BTN_LEFT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_RIGHT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_ROTATE,GPIO.IN, pull_up_down=GPIO.PUD_UP)

def getPressedButton():
    if GPIO.input(BTN_LEFT)==False:
        return BTN_LEFT
    elif GPIO.input(BTN_RIGHT)==False:
        return BTN_RIGHT
    elif GPIO.input(BTN_ROTATE)==False:
        return BTN_ROTATE
    else:
        return BTN_NOBUTTON

def main():
    initButtons()
    while True:
        print(getPressedButton())
        sleep(0.1)
        
if __name__ == '__main__':
    main()
