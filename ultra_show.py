#!/usr/bin/env python3
import ultra_sound
import time
import sys
import RPi.GPIO as gpio
import math

import matplotlib.pyplot as plt
import matplotlib.animation as animation

us1 = ultra_sound.UltraSound(trigger_pin=17, echo_pin=27)
us2 = ultra_sound.UltraSound(trigger_pin=23, echo_pin=24)
uss = [us1, us2]

fig = plt.figure()
axis = fig.add_subplot(1,1,1, projection='polar')

xs = []
ys = []
max_data = 100

def plot_series(dists):
    global xs
    global ys
    global max_data

    now = time.time()
    xs.append(now)
    ys.append(dists)
    xs = xs[-max_data:]
    ys = ys[-max_data:]

    axis.clear()
    axis.plot(xs, ys)
    axis.set_ylim(0, 5.0)

def plot_polar(dists):
    theta = [0, math.pi/2]
    radii = dists
    width = [30*math.pi/180., 30*math.pi/180.]
    #colors = plt.cm.viridis(radii / 10.)
    
    #ax = plt.subplot(111, projection='polar')
    #ax.bar(theta, radii, width=width, bottom=0.0, color=colors, alpha=0.5)

    axis.clear()
    axis.bar(theta, radii, width=width, bottom=0.0, alpha=0.5)
    axis.set_ylim(0, 3.0)

def plot_update(i):
    dists = []
    for ind, us in enumerate(uss):
        dist = us.get_distance()
        dists.append(dist if dist is not None else 9.99)
        time.sleep(0.05)
    plot_polar(dists)

if __name__ == '__main__':
    #uss = [us2]

    anim = animation.FuncAnimation(fig, plot_update, interval=50)
    plt.show()
    gpio.cleanup()
    sys.exit(0)

