#!/usr/bin/env python3
import sys
import RPi.GPIO as gpio
import time
import numpy as np
import csv
from ultrasound import UltraSound

def save_csv(file_name, data):
    with open(file_name, 'w', newline='') as out_file:
        data_writer = csv.writer(out_file)
        for i, sensor in enumerate(data):
            data_writer.writerow([f"ultrasound{i + 1}"])
            data_writer.writerow(["time", "distance"])
            for entry in sensor:
                data_writer.writerow(entry)

def save_np(file_name, data):
    file_name = file_name[:-4] # np.save attaches '.npy' again
    np_data = np.array(data)
    np.save(file_name, np_data)

gpio.setmode(gpio.BCM)

if __name__ == '__main__':
    out_file_name = sys.argv[1]
    if not (out_file_name.endswith(".csv") or
            out_file_name.endswith(".npy")):
            print(f"Usage: {sys.argv[0]} <outfile.csv/np>")
            sys.exit(1)

    us1 = UltraSound(trigger_pin=17, echo_pin=27)
    us2 = UltraSound(trigger_pin=23, echo_pin=24)
    uss = [us1,us2]

    data = [[] for _ in range(len(uss))]

    try:
        while True:
            dists = []
            for ind, us in enumerate(uss):
                dist = us.get_distance()
                t = time.time()
                data[ind].append((t, dist))
                dists.append(f"{dist if dist is not None else 999:.2f}")
                time.sleep(0.02)
            print(f"Dists:  {',    '.join([d + 'm' for d in dists])}")
            time.sleep(0.07)
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        gpio.cleanup()

    if out_file_name.endswith(".csv"):
        save_csv(out_file_name, data)
    elif out_file_name.endswith(".npy"):
        save_np(out_file_name, data)

