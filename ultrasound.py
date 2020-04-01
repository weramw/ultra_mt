#!/usr/bin/env python3
import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

class UltraSound(object):
    def __init__(self, trigger_pin, echo_pin, max_echo_wait_time=1.2 * 8/343.2):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_echo_wait_time = max_echo_wait_time
        gpio.setup(self.trigger_pin, gpio.OUT)
        gpio.setup(self.echo_pin, gpio.IN)

    def get_distance(self):
        # Send 10us pulse
        gpio.output(self.trigger_pin, True)
        time.sleep(10e-6)
        gpio.output(self.trigger_pin, False)

        pulse_start = time.time()
        pulse_stop = time.time()

        # TODO inf loop if no echo
        # Wait until pulse starts
        while gpio.input(self.echo_pin) == 0:
            pulse_start = time.time()
        # Wait until pulse ends
        while gpio.input(self.echo_pin) == 1:
            pulse_stop = time.time()

        pulse_length = pulse_stop - pulse_start
        # sonic speed is 343.2 m/s
        # divide by 2, because forth and back
        distance = 343.2 * pulse_length/ 2
        return distance

if __name__ == '__main__':
    us1 = UltraSound(trigger_pin=27, echo_pin=17)
    #us2 = UltraSound(trigger_pin=24, echo_pin=23)
    #uss = [us1, us2]
    uss = [us1]

    try:
        while True:
            for ind, us in enumerate(uss):
                dist = us.get_distance()
                print("US %d: %.2f m" % (ind,dist))
                time.sleep(0.5)
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        gpio.cleanup()

