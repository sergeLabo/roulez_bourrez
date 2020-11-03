#!python3

import os, sys
from datetime import datetime
from pathlib import Path

import numpy as np
# #from numpy.linalg import norm  # all_norm = norm(, 2)
import matplotlib.pyplot as plt

def main():

    kwargs = {  "PAQUET": 50,
                "gliss": 10
             }

    fd = FormattingData(**kwargs)


class FormattingData:

    def __init__(self, **kwargs):

        self.PAQUET = kwargs.get('PAQUET', None)
        self.gliss = kwargs.get('gliss', None)

        normes, all_a = self.get_datas()
        self.plot(normes, all_a)

    def get_datas(self):
        """Les datas sont regroupées par tuple de (norme, activité)"""

        all_x = all_y = all_z = all_a = None
        all_npz = Path("./accelerometer").glob('**/*.npz')
        # Lecture dans l'ordre d'enregistrement
        for npz in sorted(all_npz):
            print(f"Fichier lu {npz}")
            data = np.load(npz)
            if all_x is not None:
                all_x = np.hstack((all_x, data["x"]))
                all_y = np.hstack((all_y, data["y"]))
                all_z = np.hstack((all_z, data["z"]))
                all_a = np.hstack((all_a, data["activity"]))
            else:
                all_x = data["x"]
                all_y = data["y"]
                all_z = data["z"]
                all_a = data["activity"]
        print(f"Shape de toutes les datas: {all_x.shape}")

        normes = []
        for i in range(all_x.shape[0]):
            normes.append(int((all_x[i]**2 + all_y[i]**2 + all_z[i]**2 )**0.5))

        return normes, all_a

    def plot(self, acc, all_a):
        # Pour créer l'axe des x
        x_values = [a for a in range(len(all_a))]

        fig, ax1 = plt.subplots(1, 1, figsize=(10,10), facecolor='#cccccc')
        ax1.set_facecolor('#eafff5')
        ax1.set_title("Activity", size=24, color='magenta')

        color = 'tab:green'
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Accélération', color=color)
        a = ax1.scatter(x_values, acc,
                        marker = 'X',
                        linewidth=0.05,
                        color='green',
                        label="Accélération")
        ax1.tick_params(axis='y', labelcolor=color)

        # instantiate a second axes that shares the same x-axis
        ax2 = ax1.twinx()
        # we already handled the x-label with ax1
        ax2.set_ylabel('Activity', color='tab:red')
        ax2.tick_params(axis='y', labelcolor=color)

        b = ax2.plot(x_values, all_a,
                    linestyle="-",
                    linewidth=1.5,
                    color='red',
                    label="Activity")

        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        ax1.legend(loc="upper center")
        ax2.legend(loc="upper right")

        plt.show()


if __name__ == "__main__":
    main()
