#!/usr/bin/env python3
import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

GPIO_TRIGGER = 27
GPIO_ECHO = 17
# 23 echo, 24 trigger

gpio.setup(GPIO_TRIGGER, gpio.OUT)
gpio.setup(GPIO_ECHO, gpio.IN)

class UltraSound(object):
    def __init__(self, trigger_pin, echo_pin, max_echo_wait_time=1.2 * 8/343.2):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_echo_wait_time = max_echo_wait_time

def distance():
    #print("Sending Pulse")
    # Send 10us pulse
    gpio.output(GPIO_TRIGGER, True)
    time.sleep(10e-6)
    gpio.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    #print("Waiting for echo")
    # TODO inf loop if no echo
    # Push StartTime until pulse starts
    while gpio.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    # Push StopTime until pulse ends
    while gpio.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = 343.2 * TimeElapsed / 2

    return distance

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print("%.2f m" % dist)
            time.sleep(0.5)
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        gpio.cleanup()
