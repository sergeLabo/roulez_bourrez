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
print("Android =", ANDROID)


class VirtualAccelerometer:
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def random_acc(self):
        self.x = randint(999, 9999)
        self.y = randint(999, 9999)
        self.z = randint(999, 9999)


class AccelerometerService:

    def __init__(self):
        self.tempo = 0.02
        self.save_number = 500
        self.loop = 1
        self.status = 0
        self.status_msg = ""
        self.sensor_enabled = 0  # 1=android acc, 2=virtualacc
        self.num = 0
        self.init_acc()
        self.virtual_acceler = None
        self.activity = -2
        self.stop = 0
        self.init_dir()
        self.init_osc()
        self.sensor_init()

    def init_osc(self):
        """Le serveur peut envoyer
        mais impossible d'avoir 2 serveurs sur le même port.
        """
        self.server = OSCThreadServer()
        self.server.listen('localhost', port=3001, default=True)
        self.server.bind(b'/activity', self.on_activity)
        self.server.bind(b'/stop', self.on_stop)
        self.server.bind(b'/sensor_enable', self.on_sensor_enable)
        self.server.bind(b'/frequency', self.on_frequency)
        self.server.bind(b'/save_number', self.on_save_number)
        self.client = OSCClient(b'localhost', 3003)

    def on_save_number(self, msg):
        print("Nouvelle valeur pour save_number =", msg)
        self.save_number = int(msg)
        self.init_acc()
        self.num = 0

    def on_frequency(self, msg):
        print("Nouvelle valeur pour frequency =", msg)
        self.tempo = 1/int(msg)
        print(self.tempo)
        self.init_acc()
        self.num = 0

    def on_activity(self, msg):
        print("Nouvelle valeur pour activity =", msg)
        self.activity = int(msg)

    def on_stop(self, msg):
        print("stop =", msg)
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
        self.acc_x = np.zeros((self.save_number,), dtype=int)
        self.acc_y = np.zeros((self.save_number,), dtype=int)
        self.acc_z = np.zeros((self.save_number,), dtype=int)
        self.acc_act = np.zeros((self.save_number,), dtype=int)

    def sensor_init(self):
        """accelerometer est une variable globale, non reconnue par le thread"""
        print("Lancement de l'accéléromètre...")
        if self.sensor_enabled == 0:
            if ANDROID:
                try:
                    accelerometer.enable()
                    sleep(1)
                    self.sensor_enabled = 1
                    self.status_msg = "Stop Accelerometer"
                    print("Android sensor enable")
                except:
                    accelerometer.disable()
                    self.sensor_enabled = 0
                    print("Android sensor doesn't work!")
                    self.status_msg = "Android sensor doesn't work!"
            else: # Linux
                self.status_msg = "Stop Virtual Accelerometer"
                self.sensor_enabled = 2
                self.virtual_acceler = VirtualAccelerometer()
                print("Virtual sensor enabled")

        # Display
        if self.sensor_enabled == 1: sens = "Andoid sensor enable"
        elif self.sensor_enabled == 2: sens = "Virtual sensor enabled"
        else : sens = "No sensor"
        self.client.send_message(b'/sensor', [sens.encode('utf-8')])

    def on_sensor_enable(self, msg):
        """Appelé si actionné dans main avec start et stop accelerometer"""
        self.status = int(msg)

    def get_acceleration(self):
        if self.status:
            a, b, c = 0,0,0
            if self.sensor_enabled == 1:
                val = accelerometer.acceleration[:3]
                if not val == (None, None, None):
                    a = int(val[0]*1000)
                    b = int(val[1]*1000)
                    c = int(val[2]*1000)
            elif self.sensor_enabled == 2:
                self.virtual_acceler.random_acc()
                a = self.virtual_acceler.x
                b = self.virtual_acceler.y
                c = self.virtual_acceler.z
            else:
                sleep(1)
                print("Aucun accéléromètre activé !")

            if self.sensor_enabled != 0:
                # Set dans les arrays
                self.acc_x[self.num] = a
                self.acc_y[self.num] = b
                self.acc_z[self.num] = c
                self.acc_act[self.num] = self.activity

                acc_message = [a, b, c, self.activity, self.num]
                self.client.send_message(b'/acc', acc_message)

                self.num += 1
                # Fin d'un fichier
                if self.num >= self.save_number:
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
            sleep(self.tempo - 0.0016)


def create_dir(my_path_directory):
    Path(my_path_directory).mkdir(mode=0o777, parents=True, exist_ok=True)


if __name__ == '__main__':

    ACCELEROMETER = AccelerometerService()
    ACCELEROMETER.run()
