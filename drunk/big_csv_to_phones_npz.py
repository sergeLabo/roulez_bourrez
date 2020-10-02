#!/usr/bin/env python3

"""
Crée les fichiers npz par téléphone avec les accélérations
"""

import os
import csv
import numpy as np
from datetime import datetime

def csv_to_dict(csv_file):
    data = {}

    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)

        for row in reader:
            t = int(row['time']) / 1000  # fait un float
            x = float(row['x'])
            y = float(row['y'])
            z = float(row['z'])
            if row['pid'] in data:
                data[row['pid']].append([t, x, y, z])
            else:
                data[row['pid']] = []
                data[row['pid']].append([t, x, y, z])

    data = sort_data(data)
    return data

def sort_data(data):
    data_sorted = {}

    for phone, phone_data_list in data.items():
        # list de [t, x, y, z]
        data_sorted[phone] = sorted(data[phone], key=lambda x: x[0])

    return data_sorted


def save_phone_data_to_phone_npz(phone, phone_data_list):
    """
    data = {'SF3079': [[0,1], ...], 'SH1234': [[0,1], ...]
    nombre de ligne = nombre d'enregistrements
    ligne = 123456 0.123
    """

    times = []
    xs, ys, zs = [], [],[]
    for item in phone_data_list:
        times.append(item[0])
        xs.append(item[1])
        ys.append(item[2])
        zs.append(item[3])

    outfile = './phones_npz/' + phone + '.npz'
    np.savez_compressed(outfile, **{"time":  np.asarray(times),
                                    "x": np.asarray(xs),
                                    "y": np.asarray(ys),
                                    "z": np.asarray(zs)})
    print('Fichier compressé =', outfile)

def main():

    # Data des phones
    data = csv_to_dict('./data/all_accelerometer_data_pids_13.csv')
    for phone, phone_data_list in data.items():
        print("Phone:", phone)
        save_phone_data_to_phone_npz(phone, phone_data_list)
        os._exit(0)

if __name__ == "__main__":
    main()
