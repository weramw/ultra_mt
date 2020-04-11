#!/usr/bin/env python3
import ultrasound
import time
import sys
import RPi.GPIO as gpio

import matplotlib.pyplot as plt
import matplotlib.animation as animation

us1 = ultrasound.UltraSound(trigger_pin=27, echo_pin=17)
us2 = ultrasound.UltraSound(trigger_pin=23, echo_pin=24)
uss = [us1, us2]

fig = plt.figure()
axis = fig.add_subplot(1,1,1)

xs = []
ys = []
max_data = 100

def plot_update(i):
    global xs
    global ys
    global max_data

    dists = []
    for ind, us in enumerate(uss):
        dist = us.get_distance()
        dists.append(dist if dist is not None else 999)
        time.sleep(0.05)
    dist = dists[0]

    now = time.time()
    xs.append(now)
    ys.append(dist)
    xs = xs[-max_data:]
    ys = ys[-max_data:]

    axis.clear()
    axis.plot(xs, ys)

if __name__ == '__main__':
    #uss = [us2]

    anim = animation.FuncAnimation(fig, plot_update, interval=100)
    plt.show()
    gpio.cleanup()
    sys.exit(0)

