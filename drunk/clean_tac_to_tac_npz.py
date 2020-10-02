#!/usr/bin/env python3


import csv
import numpy as np
from datetime import datetime


from get_phones import get_phones_list

"""
Crée un fichier avec les TAC par telephone
"""


def get_tac(phone):
    tac = './data/clean_tac/' + phone + '_clean_TAC.csv'


    print(f"\n\nTAC du téléphone {phone}:")
    with open(tac, newline='') as csvfile:
        reader_tac = csv.DictReader(csvfile)
        tac_data = []
        for row in reader_tac:
            # OrderedDict([('timestamp', '14938'), ('TAC_Reading', '-0.059154')])
            tac = float(row['TAC_Reading'])
            ts = int(row['timestamp'])
            tac_data.append([ts, tac])

    tac_data = sorted(tac_data, key=lambda x: x[0])

    return tac_data

def save_tac(phone):

    tac_data = get_tac(phone)
    t = []
    tac = []
    for item in tac_data:
        dt = datetime.fromtimestamp(item[0]).strftime("le %d à %H:%M")
        print(dt, item[1])
        t.append(item[0])
        tac.append(item[1])

    outfile = './tac_npz/' + phone + '.npz'

    np.savez_compressed(outfile, **{"time":  np.asarray(t),
                                    "tac": np.asarray(tac)})

    print('Fichier compressé =', outfile)

def main():

    # Tac des phones
    phones = get_phones_list()
    for phone in phones:
        save_tac(phone)


if __name__ == "__main__":
    main()
