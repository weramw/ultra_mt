#!/usr/bin/env python3
import sys
import time
import numpy as np
import csv

def parse_csv(file_name):
    """ Parse a recorded csv into a dict indexed by the sensor numbers, e.g., '1'/'2'.
        The data is a list of tuples (timestamp, distance)."""
    data = {}
    cur_data = None
    with open(file_name) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("ultrasound"):  # New sensor
                sensor_name = line[len("ultrasound"):]
                data[sensor_name] = []
                cur_data = data[sensor_name]
                continue
            line_parts = line.split(",")
            assert len(line_parts) == 2
            if line_parts[0] == "time" and line_parts[1] == "distance":  # correct header
                continue
            try:
                time_stamp = float(line_parts[0])
                distance = float(line_parts[1])
                cur_data.append((time_stamp, distance))
            except ValueError:
                print(f"Could not parse data line '{line}'")
    return data

