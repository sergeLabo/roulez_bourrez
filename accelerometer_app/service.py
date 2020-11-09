#!python3
# -*- coding: UTF-8 -*-

"""
service Pong pour acceleromater
"""

# #import sys
from time import sleep, time
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
        self.tempo = 0.1
        self.freq = 10
        self.real_freq = 2
        self.loop = 1
        self.status = 0
        # #self.status_msg = ""
        self.sensor_enabled = 0  # 1=android acc, 2=virtualacc
        self.num = 0
        self.t_0 = time()
        self.init_acc()
        self.virtual_acceler = None
        self.activity = -2
        self.stop = 0
        self.init_dir()
        self.init_osc()
        self.sensor_init()

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
        self.acc_x    = np.zeros((1,), dtype=int)
        self.acc_y    = np.zeros((1,), dtype=int)
        self.acc_z    = np.zeros((1,), dtype=int)
        self.acc_act  = np.zeros((1,), dtype=int)
        self.acc_time = np.zeros((1,), dtype=int)

    def sensor_init(self):
        """accelerometer est une variable globale, non reconnue par le thread"""
        print("Lancement de l'accéléromètre...")
        if self.sensor_enabled == 0:
            if ANDROID:
                # #while self.sensor_enabled == 1:
                    # #sleep(2)
                try:
                    accelerometer.enable()
                    sleep(1)
                    self.sensor_enabled = 1
                    # #self.status_msg = "Stop Accelerometer"
                    print("Android sensor enable")
                except:
                    accelerometer.disable()
                    self.sensor_enabled = 0
                    print("Android sensor doesn't work!")
                    # #self.status_msg = "Android sensor doesn't work!"
            else: # Linux
                self.status_msg = "Stop Virtual Accelerometer"
                self.sensor_enabled = 2
                self.virtual_acceler = VirtualAccelerometer()
                print("Virtual sensor enabled")

        # Display
        if self.sensor_enabled == 1: sens = "Andoid"
        elif self.sensor_enabled == 2: sens = "Virtual"
        else : sens = "No sensor"
        self.client.send_message(b'/sensor', [sens.encode('utf-8')])

    def init_osc(self):
        self.server = OSCThreadServer()
        self.server.listen('localhost', port=3001, default=True)
        self.server.timeout = 0.001
        self.server.bind(b'/activity', self.on_activity)
        self.server.bind(b'/stop', self.on_stop)
        self.server.bind(b'/sensor_enable', self.on_sensor_enable)
        self.server.bind(b'/frequency', self.on_frequency)
        self.server.bind(b'/save_npz', self.on_save_npz)

        self.client = OSCClient(b'localhost', 3003)

    def on_frequency(self, msg):
        print("Valeur de frequency reçue dans service=", msg)
        self.freq = int(msg)
        tempo = (1 / int(msg))
        self.tempo = float(tempo)
        print("    nouvelle tempo =", round(tempo, 3))
        self.init_acc()
        self.num = 0

    def on_activity(self, msg):
        print("Nouvelle valeur pour activity =", msg)
        self.activity = int(msg)
        # 1604917632133 > maxi pour osc = 2147483648
        tp = int(time()*1000) - 1604000000000
        acc_message = [0, 0, 0, self.activity, self.num, self.tempo, tp]
        # Mise à jour de l'affichage, même si acc ne tournr pas
        self.client.send_message(b'/acc', acc_message)

    def on_stop(self, msg):
        print("stop =", msg)
        accelerometer.disable()
        # Fin de boucle avec msg = 0
        self.loop = int(msg)

    def on_sensor_enable(self, msg):
        """Appelé si actionné dans main avec start et stop accelerometer"""
        print("Reçu dans on_sensor_enable:", msg)
        self.status = int(msg)

    def on_save_npz(self, msg):
        """Appelé pour enregistré les datas"""
        print("Vérification avant enregistrement du npz:")
        print("    Nombre de datas =", self.acc_x.shape)
        dtn = datetime.now()
        dt = dtn.strftime("%Y_%m_%d_%H_%M_%S")
        outfile = f"{self.my_path_directory}/acc_{dt}.npz"
        np.savez_compressed(outfile,  **{   "x": self.acc_x,
                                            "y": self.acc_y,
                                            "z": self.acc_z,
                                            "activity": self.acc_act,
                                            "t": self.acc_time})
        print("    npz enregistré:", outfile)

    def one_loop(self):
        if self.status:
            a, b, c = self.get_acc()

            if self.sensor_enabled != 0:
                if self.activity >= 0:
                    tp = int(time()*1000) - 1604000000000

                    if self.num > 0:
                        # Ajout des valeurs dans les arrays
                        self.acc_x = np.append(self.acc_x, a)
                        self.acc_y = np.append(self.acc_y, b)
                        self.acc_z = np.append(self.acc_z, c)
                        self.acc_act = np.append(self.acc_act, self.activity)
                        self.acc_time = np.append(self.acc_time, tp)
                    else:
                        self.acc_x[0] = a
                        self.acc_y[0] = b
                        self.acc_z[0] = c
                        self.acc_act[0] = self.activity
                        self.acc_time[0] = tp

                    acc_message = [ a,
                                    b,
                                    c,
                                    self.activity,
                                    self.num,
                                    self.real_freq,
                                    tp]
                    # #if self.num % 10 == 1:
                    self.client.send_message(b'/acc', acc_message)

                    if self.num % 100 == 0:
                        print("Suivi :", self.num)
                        t = time()
                        self.real_freq = int(100/(t - self.t_0))
                        self.t_0 = t
                        self.client.send_message(b'/ping', [1])

                    self.num += 1

    def get_acc(self):
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
        return a, b, c

    def run(self):
        while self.loop:
            self.one_loop()
            sleep(self.tempo)



def create_dir(my_path_directory):
    Path(my_path_directory).mkdir(mode=0o777, parents=True, exist_ok=True)


if __name__ == '__main__':

    ACCELEROMETER = AccelerometerService()
    ACCELEROMETER.run()
