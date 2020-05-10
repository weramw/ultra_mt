#!/usr/bin/env python3
import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

class UltraSound(object):
    def __init__(self, trigger_pin, echo_pin, max_echo_wait_time=1.2 * 2*4.0/343.2):
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

        trigger_start = time.time()
        pulse_start = time.time()
        pulse_stop = time.time()

        # Wait until pulse starts
        while gpio.input(self.echo_pin) == 0:
            pulse_start = time.time()
            if pulse_start - trigger_start > self.max_echo_wait_time:
                return None

        # Wait until pulse ends
        while gpio.input(self.echo_pin) == 1:
            pulse_stop = time.time()
            if pulse_stop - trigger_start > self.max_echo_wait_time:
                return None

        pulse_length = pulse_stop - pulse_start
        # sonic speed is 343.2 m/s
        # divide by 2, because forth and back
        distance = 343.2 * pulse_length/ 2
        return distance

if __name__ == '__main__':
    us1 = UltraSound(trigger_pin=27, echo_pin=17)   # gruen
    us2 = UltraSound(trigger_pin=23, echo_pin=24)   # lila
    uss = [us1, us2]
    #uss = [us2]

    try:
        while True:
            dists = []
            for ind, us in enumerate(uss):
                dist = us.get_distance()
                dists.append(f"{dist if dist is not None else 999:.2f}")
                time.sleep(0.05)
            print(f"Dists:  {', '.join([d + 'm' for d in dists])}")
            time.sleep(0.2)
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        gpio.cleanup()

