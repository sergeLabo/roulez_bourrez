#!python3

import os, sys
from time import mktime
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

        normes, all_a, all_t = self.get_datas()
        self.plot(normes, all_a, all_t)

    def get_datas(self):
        """Les datas sont regroupées par tuple de (norme, activité)"""

        all_x = all_y = all_z = all_a = None
        all_npz = Path("./accelerometer").glob('**/*.npz')
        # Lecture dans l'ordre d'enregistrement
        for npz in sorted(all_npz):
            print(f"Fichier lu {npz}")
            data = np.load(npz)
            # #if all_x is not None:
                # #all_x = np.hstack((all_x, data["x"]))
                # #all_y = np.hstack((all_y, data["y"]))
                # #all_z = np.hstack((all_z, data["z"]))
                # #all_a = np.hstack((all_a, data["activity"]))
                # #all_t = np.hstack((all_t, data["t"]))
            # #else:
            all_x = data["x"]
            all_y = data["y"]
            all_z = data["z"]
            all_a = data["activity"]
            all_t = data["t"]
            print(all_t)
        print(f"Shape de toutes les datas: {all_x.shape}")

        normes = []
        for i in range(all_x.shape[0]):
            normes.append(int((all_x[i]**2 + all_y[i]**2 + all_z[i]**2 )**0.5))

        return normes, all_a, all_t

    def plot(self, acc, all_a, all_t):
        # Pour créer l'axe des x
        # #x_values = [a for a in range(len(all_a))]  #[30000:30100]))]
        x_values = []
        for i in range(len(all_t)):
            # 667.3380000591278 1604738667.422
            it = all_t[i]/1000
            # Suppression de time() = 0
            if it <  1000:
                it = all_t[i+1]/1000
            dt = datetime.fromtimestamp(it)
            x_values.append(dt)

        x_values = x_values
        y_values = acc

        fig, ax1 = plt.subplots(1, 1, figsize=(20,10), facecolor='#cccccc')
        ax1.set_facecolor('#eafff5')
        ax1.set_title("Activity", size=24, color='magenta')

        color = 'tab:green'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Accélération', color=color)
        a = ax1.scatter(x_values, y_values,
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

        # Définition de l'échelle des x
        mini = x_values[0]
        maxi = x_values[-1]
        ax1.set_xlim(mini, maxi)
        ax2.set_xlim(mini, maxi)

        duree = int((maxi - mini).total_seconds())
        print("Durée du test =", duree)
        print("Fréquence =", 6480/181)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        ax1.legend(loc="upper center")
        ax2.legend(loc="upper right")

        plt.show()


if __name__ == "__main__":
    main()
