#!python3
# -*- coding: UTF-8 -*-

"""
Compilation possible avec java 8 et non avec 11
sudo update-alternatives --config java
java -version

export JAVA_HOME=/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64

Le service s'appelle Pong
"""

import os
from time import sleep

import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import NumericProperty

from plyer import utils

from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer


# Dans buildozer.spec
# services = Pong:service.py
SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.kivy.accelbasic',
    servicename=u'Pong')

print("Platform =", utils.platform)
ANDROID = utils.platform._platform_android
if not ANDROID:
    from kivy.core.window import Window
    # Simulation de l'écran de mon tél: 1280*720
    k = 1.0
    WS = (int(720*k), int(1280*k))
    Window.size = WS
    os.environ['JAVA_HOME'] = '/usr/lib/jvm/adoptopenjdk-8-hotspot-amd64'

from jnius import autoclass


class AccelerometerTest(BoxLayout):

    activity = NumericProperty(-1)

    def __init__(self, app):

        super().__init__()
        self.app = app
        freq = 50
        self.sensor_status = 0
        Clock.schedule_interval(self.update_display, 1/freq)

    def on_sensor_status(self):
        """Envoi au service de l'info sensor enable or not"""

        r = self.app.get_running_app()
        if self.sensor_status == 0:
            self.sensor_status = 1
            self.ids.acceleromer_status.text = "Stop Accelerometer"
        elif self.sensor_status == 1:
            self.sensor_status = 0
            self.ids.acceleromer_status.text = "Start Accelerometer"
        print("Envoi de sensor_status", self.sensor_status)
        r.client.send_message(b'/sensor_status', [self.sensor_status])

    def on_activity(self, act):
        r = self.app.get_running_app()
        r.client.send_message(b'/activity', [act])

    def update_display(self, dt):
        root = self.app.get_running_app()
        a, b, c, activity, num =    (root.display_list[0],
                                    root.display_list[1],
                                    root.display_list[2],
                                    root.display_list[3],
                                    root.display_list[4])
        self.ids.x_label.text = "X: " + str(a)
        self.ids.y_label.text = "Y: " + str(b)
        self.ids.z_label.text = "Z: " + str(c)
        self.ids.activity_label.text = "Activité: " + str(activity)
        self.ids.number.text = "Indice de boucle: " + str(num)
        self.ids.file_saved.text = root.file
        self.ids.activ_sensor.text = f"Capteur actif: {root.sensor}"

    def do_quit(self):
        self.app.get_running_app().do_quit()


class AccelerometerTestApp(App):

    def build(self):
        self.display_list = [0]*5
        self.file = ""
        self.sensor = ""
        self.service = None

        self.server = OSCThreadServer()
        self.server.listen( address=b'localhost',
                            port=3003,
                            default=True)
        self.server.bind(b'/acc', self.on_message)
        self.server.bind(b'/file', self.on_file)
        self.server.bind(b'/sensor', self.on_sensor)
        self.client = OSCClient(b'localhost', 3001)

        self.start_service()
        return AccelerometerTest(App)

    def start_service(self):
        if ANDROID:
            #SERVICE_NAME = f"{'org.kivy.accelbasic'}.Service{'Pong'}"
            self.service = autoclass(SERVICE_NAME)
            m_activity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            argument = ''
            self.service.start(m_activity, argument)
        else:
            from runpy import run_path
            from threading import Thread
            # Equivaut à:
            # run_path('./service.py', {'run_name': '__main__'}, daemon=True)
            self.service = Thread(  target=run_path,
                                    args=('./service.py',),
                                    kwargs={'run_name': '__main__'},
                                    daemon=True)
            self.service.start()
            print("Thread lancé.")

    def on_sensor(self, sens):
        self.sensor = sens.decode('utf-8')

    def on_file(self, f):
        self.file = f.decode('utf-8')

    def on_message(self, *args):
        self.display_list = args

    def stop_service(self):
        if ANDROID:  # android
            self.service.stop()
            self.service = None
        else:  # linux
            self.client.send_message(b'/stop', [1])
            sleep(1)

    def on_pause(self):
        print("on_pause")
        return True

    def on_resume(self):
        print("on_resume")

    def do_quit(self):
        self.stop_service()
        AccelerometerTestApp.get_running_app().stop()


if __name__ == '__main__':
    AccelerometerTestApp().run()
