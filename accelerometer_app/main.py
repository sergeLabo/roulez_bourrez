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
from datetime import datetime
from runpy import run_path
from threading import Thread

import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.graph import Graph, MeshLinePlot


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


class OSC:
    """Ne fait que envoyer avec self.client
    et recevoir avec self.server, en com avec service.py
    """

    def __init__(self):
        self.sensor = "Recherche d'un capteur ..."
        # a, b, c, activity, num, tempo
        self.display_list = [0, 0, 0, -2, 0, 1, 0]
        self.histo = []
        self.server = OSCThreadServer()
        self.server.listen(address=b'localhost',port=3003, default=True)
        self.server.bind(b'/acc', self.on_acc)
        self.server.bind(b'/sensor', self.on_sensor)
        self.client = OSCClient(b'localhost', 3001)
        self.t_init = 0

    def on_sensor(self, sens):
        """Vlaleur possible: Andoid Virtual No sensor"""
        self.sensor = sens.decode('utf-8')

    def on_acc(self, *args):
        self.display_list = args
        a, b, c, t = (  self.display_list[0],
                        self.display_list[1],
                        self.display_list[2],
                        self.display_list[6])

        norme = int((a**2 + b**2 + c**2)**0.5)
        # 920736845
        # 36845
        if self.t_init:
            tx = (t - self.t_init)/100
        else:
            self.t_init = t
            tx = 0
        print(tx)
        # liste de couple (x, y)
        self.histo.append((tx, norme))
        if len(self.histo) > 100:
            del self.histo[0]


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Screen2(Screen):

    graph_id = ObjectProperty()
    titre = StringProperty("Capteur")
    # Affichage sur le bouton au dessus du graphique
    period = StringProperty("Période")

    def __init__(self, **kwargs):
        """self.graph ne peut pas être initié ici.
        Il doit être dans une autre méthode et appelé plus tard.
        """

        super().__init__(**kwargs)
        self.app = App.get_running_app()

        self.unit_x = "tutu"
        self.unit_y = "tata"
        self.graph = None
        self.y_major = 1
        self.titre = "Accelerometer"
        self.reset = None
        self.xlabel = ""

        # Initialisation de la courbe avec sa couleur
        # mode='points',
        self.curve_plot = MeshLinePlot(mode='points', color=[1, 0, 0, 1])
        # #self.curve_plot.mode = 'triangle_strip'
        self.curve_plot.points = [(0, 0)]*101

        # Appel tous les 2 secondes
        Clock.schedule_interval(self.update, 2)

    def graph_init(self):
        """Initialisation de self.graph.
        plot initié avec 100 couples [(x, y), ...]
        """

        print("Initialisation du graph")
        # ## Si existe je détruits
        if self.graph:
            self.ids.graph_id.remove_widget(self.graph)
            print("self.graph détruit")

        if self.y_major:  # int
            if len(self.app.osc.histo) > 5:
                self.create_graph()
            else:
                self.reset = 1

    def create_graph(self):
        """Création du graph seul et pas d'ajout au widget"""

        print("Appel de la création du graph ..")
        self.unit_x = "minutes"

        # Paramètres du graph en x
        self.xmin = 0
        self.xmax = 1000
        self.x_ticks_major = 3600
        self.x_ticks_minor = 600

        # Paramètres du graph en y
        self.ymin = 0
        self.ymax = self.y_major
        self.ylabel = self.unit_y
        self.y_ticks_major = self.y_major/10
        self.y_ticks_minor = 0  #5

        # Je crée ou recrée
        self.graph = Graph( background_color=(0.8, 0.8, 0.8, 1),
                            border_color=(0, 0.1, 0.1, 1),
                            xlabel=self.xlabel,
                            ylabel=self.ylabel,
                            x_ticks_minor=self.x_ticks_minor,
                            x_ticks_major=self.x_ticks_major,
                            y_ticks_major=self.y_ticks_major,
                            x_grid_label=True,
                            y_grid_label=True,
                            padding=10,
                            view_pos = (10, -10),
                            x_grid=True,
                            y_grid=True,
                            xmin=self.xmin,
                            xmax=self.xmax,
                            ymin=self.ymin,
                            ymax=self.ymax,
                            tick_color=(1, 0, 1, 1),
                            label_options={'color': (0.2, 0.2, 0.2, 1)})

        self.graph.add_plot(self.curve_plot)
        self.ids.graph_id.add_widget(self.graph)

    def update(self, dt):
        if self.reset:
            self.reset = None
            self.y_major = 0
            self.graph_init()
        else:
            if not self.graph:
                self.graph_init()

        # Reset des points
        self.curve_plot.points = []

        # Echelle des y
        y_major = self.get_y_major()
        if y_major != self.y_major:
            self.y_major = y_major
            # reset du graph
            # #self.graph_init()

        # Apply value to plot
        for h in self.app.osc.histo:
            self.curve_plot.points.append([h[0], h[1]])

        # #self.curve_plot.update()

    def get_y_major(self):
        """Le maxi de l'echelle des y"""

        # Recherche du maxi
        maxi = 0
        for couple in self.app.osc.histo:
            # #print(couple)
            if couple[1] > maxi:
                maxi = couple[1]

        # Définition de l'échelle sur y soit 0 à y_major
        if 1 <= maxi < 10:
            a = 1
        elif 10 <= maxi < 100:
            a = 10
        elif 100 <= maxi < 1000:
            a = 100
        elif 1000 <= maxi < 10000:
            a = 1000
        elif 10000 <= maxi < 100000:
            a = 10000
        else:
            a = 1
        # 756 --> 800 int(756/100) + 1 * 1000
        if maxi < 0:
            y_major = 1
        else:
            y_major = (int(maxi*1.1/a) + 1) * a

        # #print("maxi:", maxi, "y_major", y_major)
        return y_major


class Screen1(Screen):
    """Ecran d'affichage des datas envoyées par service.py
    et reçues dans self.app.osc
    """

    activity = NumericProperty(-1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

        self.sensor_status = 0
        # Delay de boucle
        Clock.schedule_once(self.client_once, 1)

    def client_once(self, dt):
        Clock.schedule_interval(self.update_display, 1)

    def on_sensor_enable(self):
        """Envoi au service de l'info sensor enable or not"""

        if self.sensor_status == 0:
            self.sensor_status = 1
            self.ids.acceleromer_status.text = "Stop Accelerometer"
            self.freq = self.app.frequency  # vient de *.ini
            self.app.osc.client.send_message(b'/frequency', [self.freq])
            print("Envoi de /freq :", self.freq)

        elif self.sensor_status == 1:
            self.sensor_status = 0
            self.ids.acceleromer_status.text = "Start Accelerometer"

        print("Envoi de sensor_status:", self.sensor_status)
        self.app.osc.client.send_message(b'/sensor_enable', [self.sensor_status])

    def on_activity(self, act):
        self.app.osc.client.send_message(b'/activity', [act])

    def update_display(self, dt):

        a, b, c, activity, num, real_freq, t = (self.app.osc.display_list[0],
                                                self.app.osc.display_list[1],
                                                self.app.osc.display_list[2],
                                                self.app.osc.display_list[3],
                                                self.app.osc.display_list[4],
                                                self.app.osc.display_list[5],
                                                self.app.osc.display_list[6])
        if activity == 0:
            activity_str = "Application réduite"
        elif activity == 1:
            activity_str = "Application plein ecran\nCouvercle rabattu"
        elif activity == 2:
            activity_str = "Application plein ecran\nCouvercle ouvert"
        elif activity == 3:
            activity_str = "Application plein ecran\nCouvercle rabattu\nen mouvement"
        else:
            activity_str = "\nVous devez sélectionner une activité !"

        self.ids.x_y_z.text = "X: " + str(a) + "   Y: " + str(b) + "   Z: " + str(c)
        self.ids.activity_label.text = "Activité:\n" + activity_str
        self.ids.number.text = "Cycle numéro: " + str(num)
        self.ids.th_freq.text = f"Fréquence à obtenir = 10"
        self.ids.real_freq.text = f"Fréquence réelle = {real_freq}"
        self.ids.activ_sensor.text = f"Capteur actif: {self.app.osc.sensor}"

    def go_to_plot(self):
        pass

    def do_save_npz(self):
        self.root.client.send_message(b'/save_npz', [1])
        self.ids.save_npz.text = "Datas enregistrées"

    def reset_save_npz_button(self, dt):
        self.ids.save_npz.text = "Enregistrement des datas"

    def do_quit(self):
        self.root.do_quit()


class Accelerometer(BoxLayout):

    def __init__(self, app, **kwargs):

        super().__init__(**kwargs)
        self.app = app

        self.service = None
        self.app.osc = OSC()
        self.start_service()

    def start_service(self):
        if ANDROID:
            # SERVICE_NAME = 'org.kivy.accelerometer.ServicePong'
            self.service = autoclass(SERVICE_NAME)
            self.m_activity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            argument = 'android:hardwareAccelerated="true"'
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


class AccelerometerApp(App):

    def build(self):
        return Accelerometer(self)

    def on_start(self):
        self.frequency = int(self.config.get('accelerometer', 'frequency'))

    def build_config(self, config):
        config.setdefaults('accelerometer',
                            {'frequency': 50})

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
                      "desc": "de 1 à 100",
                      "section": "accelerometer", "key": "frequency"}
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
                if value >= 100: value = 100
                self.frequency = value
                self.osc.client.send_message(b'/frequency', [value])
                # Save in ini
                self.config.set('accelerometer', 'frequency', value)

    def on_pause(self):
        # Pour que l'application passe en pause si réduite, et continue si réactivée
        print("on_pause return True")
        return True

    def on_resume(self):
        # Pour que l'application passe en pause si fermée, et continue si réactivée
        print("on_resume return True")
        return True

    def do_quit(self):
        if ANDROID:
            self.service.stop(self.m_activity)
            self.service = None
        else:
            self.client.send_message(b'/stop', [1])
            sleep(1)

        AccelerometerApp.get_running_app().stop()


def get_datetime(date):
    """de int(time()*1000), retourne datetime"""
    return datetime.fromtimestamp((date + 1604000000000)/1000)

if __name__ == '__main__':
    AccelerometerApp().run()

"""'apply_property', 'ask_draw', 'bind', 'color', 'create_drawings',
        'create_property', 'dispatch', 'dispatch_children', 'dispatch_generic',
        'draw', 'events', 'fbind', 'funbind', 'funcx', 'funcy', 'get_drawings',
        'get_group', 'get_property_observers', 'get_px_bounds', 'getter',
        'is_event_type', 'iterate_points', 'mode', 'on_clear_plot', 'params',
        'plot_mesh', 'points', 'properties', 'property', 'proxy_ref',
        'register_event_type', 'set_mesh_size', 'setter', 'uid', 'unbind',
        'unbind_uid', 'unproject', 'unregister_event_types', 'update', 'x_axis',
        'x_px', 'y_axis', 'y_px'
        """
