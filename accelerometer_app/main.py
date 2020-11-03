#!python3
# -*- coding: UTF-8 -*-

"""
Bug avec debian 10
    xclip and xsel - FileNotFoundError: [Errno 2]
résolu avec
    sudo apt install xclip

Compilation possible avec java 8 et non avec 11
sudo update-alternatives --config java
java -version
export JAVA_HOME=/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64

Le service s'appelle Pong

Ne pas oublier d'autoriser les droits d'écriture dans Paramètres/Applications
sur Android.
"""

import os
from time import sleep
from runpy import run_path
from threading import Thread

import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import NumericProperty

from plyer import utils

from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer

print("Platform =", utils.platform)
ANDROID = utils.platform._platform_android  # retourne True ou False
print("Android =", ANDROID)
if not ANDROID:
    from kivy.core.window import Window
    # Simulation de l'écran de mon tél: 1280*720
    k = 1.0
    WS = (int(720*k), int(1280*k))
    Window.size = WS
    os.environ['JAVA_HOME'] = '/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64'

from jnius import autoclass

"""
SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.kivy.accelerometer',
    servicename=u'ServicePong')

Structure = package.domain.package.name.ServiceToto
avec de buildozer.spec
package.domain = org.kivy
package.name = accelerometer
soit
org.kivy.accelerometer.ServicePong
"""

SERVICE_NAME = 'org.kivy.accelerometer.ServicePong'
print("SERVICE_NAME:", SERVICE_NAME)


class Accelerometer(BoxLayout):

    activity = NumericProperty(-1)

    def __init__(self, app):

        super().__init__()
        self.app = app
        self.root = self.app.get_running_app()
        self.freq = self.root.frequency
        self.save_number = self.root.save_number
        self.sensor_status = 0
        Clock.schedule_interval(self.update_display, 1/self.freq)
        Clock.schedule_once(self.client_once, 1)

    def client_once(self, dt):
        # Envoi des arguments à service.py
        self.root.client.send_message(b'/frequency', [self.freq])
        self.root.client.send_message(b'/save_number', [self.save_number])

    def on_sensor_enable(self):
        """Envoi au service de l'info sensor enable or not"""

        if self.sensor_status == 0:
            self.sensor_status = 1
            self.ids.acceleromer_status.text = "Stop Accelerometer"
        elif self.sensor_status == 1:
            self.sensor_status = 0
            self.ids.acceleromer_status.text = "Start Accelerometer"
        print("Envoi de sensor_status:", self.sensor_status)
        self.root.client.send_message(b'/sensor_enable', [self.sensor_status])

    def on_activity(self, act):
        self.root.client.send_message(b'/activity', [act])

    def update_display(self, dt):
        a, b, c, activity, num = (  self.root.display_list[0],
                                    self.root.display_list[1],
                                    self.root.display_list[2],
                                    self.root.display_list[3],
                                    self.root.display_list[4])
        self.ids.x_label.text = "X: " + str(a)
        self.ids.y_label.text = "Y: " + str(b)
        self.ids.z_label.text = "Z: " + str(c)
        self.ids.activity_label.text = "Activité: " + str(activity)
        self.ids.number.text = "Indice de boucle: " + str(num)
        self.ids.file_saved.text = self.root.file
        self.ids.activ_sensor.text = f"Capteur actif: {self.root.sensor}"

    def do_quit(self):
        self.app.get_running_app().do_quit()


class AccelerometerApp(App):

    def build(self):
        self.frequency = int(self.config.get('accelerometer', 'frequency'))
        self.save_number = int(self.config.get('accelerometer', 'save_number'))

        return Accelerometer(App)

    def on_start(self):
        self.display_list = [0]*5
        self.file = ""
        self.sensor = ""
        self.service = None

        self.server = OSCThreadServer()
        self.server.listen(address=b'localhost',port=3003, default=True)
        self.server.bind(b'/acc', self.on_message)
        self.server.bind(b'/file', self.on_file)
        self.server.bind(b'/sensor', self.on_sensor)
        self.client = OSCClient(b'localhost', 3001)

        self.start_service()

    def start_service(self):
        if ANDROID:
            self.service = autoclass(SERVICE_NAME)
            self.m_activity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            argument = ''
            self.service.start(self.m_activity, argument)
        else:
            # Equivaut à:
            # run_path('./service.py', {'run_name': '__main__'}, daemon=True)
            self.service = Thread(  target=run_path,
                                    args=('service.py',),
                                    kwargs={'run_name': '__main__'},
                                    daemon=True)
            self.service.start()
            print("Thread lancé.")

    def on_sensor(self, sens):
        self.sensor = sens.decode('utf-8')

    def on_file(self, f):
        # acc_2020_11_01_14_26_46/acc_2020_11_01_14_29_53.npz
        self.file = f.decode('utf-8')[-51:]

    def on_message(self, *args):
        self.display_list = args

    def build_config(self, config):
        config.setdefaults('accelerometer',
                            {'frequency': 50,
                             'save_number': 3000})

        config.setdefaults('kivy',
                            { 'log_level': 'debug',
                              'log_name': 'accelerometer_%y-%m-%d_%_.txt',
                              'log_dir': '/sdcard',
                              'log_enable': '1'})

        config.setdefaults('postproc',
                            { 'double_tap_time': 250,
                              'double_tap_distance': 20})

    def build_settings(self, settings):
        data = """[
                    {"type": "title", "title":"Configuration de l'accéléromètre"},

                    {"type": "numeric",
                      "title": "Fréquence",
                      "desc": "de 1 à 50",
                      "section": "accelerometer", "key": "frequency"},

                    {"type": "numeric",
                      "title": "Nombre de valeurs par fichier",
                      "desc": "de 500 à 9000",
                      "section": "accelerometer", "key": "save_number"}

                   ]"""

        # self.config est le config de build_config
        settings.add_json_panel('Accelerometer', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        if config is self.config:  # du joli python rigoureux
            token = (section, key)

            # Frequency
            if token == ('accelerometer', 'frequency'):
                value = int(value)
                print("Nouvelle Fréquence:", value)
                if value < 1: value = 1
                if value >= 50: value = 50
                self.frequency = value
                self.client.send_message(b'/frequency', [value])
                # Save in ini
                self.config.set('accelerometer', 'frequency', value)

            # Enregistrement tous les
            if token == ('accelerometer', 'save_number'):
                value = int(value)
                print("Nouveau nombre d'enregistrement par fichier:", value)
                if value < 500: value = 500
                if value >= 9000: value = 9000
                self.save_number = value
                self.client.send_message(b'/save_number', [value])
                # Save in ini
                self.config.set('accelerometer', 'save_number', value)

    def on_pause(self):
        print("on_pause")
        return True

    def on_resume(self):
        print("on_resume")

    def do_quit(self):
        if ANDROID:
            self.service.stop(self.m_activity)
            self.service = None
        else:
            self.client.send_message(b'/stop', [1])
            sleep(1)

        AccelerometerApp.get_running_app().stop()


if __name__ == '__main__':
    AccelerometerApp().run()
