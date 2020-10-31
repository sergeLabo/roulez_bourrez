#!python3
# -*- coding: UTF-8 -*-

"""
service Pong pour acceleromater
"""

import sys
from time import sleep
from datetime import datetime
from random import randint
from pathlib import Path

import numpy as np

from plyer import accelerometer, storagepath, utils

from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer

print("Platform =", utils.platform)
ANDROID = utils.platform._platform_android

ACTIVITY = 3

class VirtualAccelerometer:
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def random_acc(self):
        self.x = randint(999, 9999)
        self.y = randint(999, 9999)
        self.z = randint(999, 9999)


class Accelerometer:

    def __init__(self):

        self.loop = 1
        self.status = 0
        self.sensor_enabled = False
        self.virtual_sensor_enabled = False
        self.num = 0
        self.init_acc()
        self.virtual_acceler = None
        self.activity = -2
        self.stop = 0
        self.init_dir()
        self.init_osc()

    def init_osc(self):
        """Le serveur peut envoyer
        mais impossible d'avoir 2 serveurs sur le même port.
        """
        self.server = OSCThreadServer()
        self.server.listen('localhost', port=3001, default=True)
        self.server.bind(b'/activity', self.on_activity)
        self.server.bind(b'/stop', self.on_stop)
        self.server.bind(b'/sensor_status', self.on_status)
        self.client = OSCClient(b'localhost', 3003)

    def on_activity(self, msg):
        print("activity", msg)
        self.activity = int(msg)

    def on_stop(self, msg):
        print("stop", msg)
        self.loop = int(msg)

    def init_dir(self):
        # Création du dossier d'enregistrement
        if ANDROID:
            extern = storagepath.get_documents_dir()
        else:
            extern = "."
        dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.my_path_directory = f"{extern}/accelerometer/acc_{dt}"
        print(f"Documents Storage = {extern}")
        print(f"Dossier d'enregistrement des datas = {self.my_path_directory}")
        create_dir(self.my_path_directory)

    def init_acc(self):
        self.acc_x = np.zeros((500,), dtype=int)
        self.acc_y = np.zeros((500,), dtype=int)
        self.acc_z = np.zeros((500,), dtype=int)
        self.acc_act = np.zeros((500,), dtype=int)

    def on_status(self, msg):
        """Appelé si actionné dans main"""

        self.status = int(msg)
        # Si status = 1, je tourne; si = 0 je bloque
        if self.status:
            if not self.sensor_enabled and not self.virtual_sensor_enabled:
                if ANDROID:
                    try:
                        accelerometer.enable()
                        self.sensor_enabled = True
                        self.status = "Stop Accelerometer"
                        print("Andoid sensor enable")
                    except:
                        accelerometer.disable()
                        self.sensor_enabled = False
                else:
                    self.status = "Stop Virtual Accelerometer"
                    self.virtual_sensor_enabled = True
                    self.virtual_acceler = VirtualAccelerometer()
                    print("Virtual sensor enabled")
            else:
                # Stop de la capture
                accelerometer.disable()
                self.sensor_enabled = False
                self.virtual_sensor_enabled = False
                self.ids.status_button.text = "Start Accelerometer"
        else:
            self.sensor_enabled = False
            self.virtual_sensor_enabled = False

        # Display
        if self.sensor_enabled: sens = "Andoid sensor enable"
        elif self.virtual_sensor_enabled: sens = "Virtual sensor enabled"
        else : sens = "No sensor"
        self.client.send_message(b'/sensor', [sens.encode('utf-8')])

    def get_acceleration(self):
        a = b = c = 0

        if self.sensor_enabled:
            val = accelerometer.acceleration[:3]
            if not val == (None, None, None):
                a = int(val[0]*1000)
                b = int(val[1]*1000)
                c = int(val[2]*1000)
        elif self.virtual_sensor_enabled:
            self.virtual_acceler.random_acc()
            a = self.virtual_acceler.x
            b = self.virtual_acceler.y
            c = self.virtual_acceler.z
        else:
            self.sensor_enabled = self.virtual_sensor_enabled = False
            sleep(1)
            print("Aucun accéléromètre activé !")

        if self.sensor_enabled or self.virtual_sensor_enabled:
            # Set dans les arrays
            self.acc_x[self.num] = a
            self.acc_y[self.num] = b
            self.acc_z[self.num] = c
            self.acc_act[self.num] = self.activity

            acc_message = [a, b, c, self.activity, self.num]
            self.client.send_message(b'/acc', acc_message)

            self.num += 1
            # Fin d'un fichier
            if self.num >= 500:
                if self.activity >= 0:
                    dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                    outfile = f"{self.my_path_directory}/acc_{dt}.npz"
                    np.savez_compressed(outfile,  **{"x": self.acc_x,
                                                    "y": self.acc_y,
                                                    "z": self.acc_z,
                                                    "activity": self.acc_act})
                    print(f"Enregistrement de: {outfile}")
                    self.client.send_message(b'/file', [outfile.encode('utf-8')])
                else:
                    a = "Pas d'activité définie"
                    self.client.send_message(b'/file', [a.encode('utf-8')])
                self.num = 0
                self.init_acc()

    def run(self):
        while self.loop:
            self.get_acceleration()
            sleep(0.02)


def create_dir(my_path_directory):
    Path(my_path_directory).mkdir(mode=0o777, parents=True, exist_ok=True)


if __name__ == '__main__':

    ACCELEROMETER = Accelerometer()
    ACCELEROMETER.run()
