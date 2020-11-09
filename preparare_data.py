#!python3

import os, sys
from datetime import datetime
from pathlib import Path
import random

import numpy as np
import matplotlib.pyplot as plt


def main():

    kwargs = {  "PAQUET": 100,
                "gliss": 2
             }

    fd = FormattingData(**kwargs)


class FormattingData:

    def __init__(self, **kwargs):

        create_dir('./npz_final/')

        self.PAQUET = kwargs.get('PAQUET', None)
        self.gliss = kwargs.get('gliss', None)

        # En array
        self.norme_act = self.get_datas()
        paquets, labels = self.get_paquets_labels()
        train, test, trainlabel, testlabel = self.get_train_test_trainlabel_testlabel(paquets, labels)
        self.save_npz(train, test, trainlabel, testlabel)

    def get_datas(self):
        """Les datas sont regroupées par tuple de (norme, activité, time)"""

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
                all_t = np.hstack((all_t, data["t"]))
            else:
                all_x = data["x"]
                all_y = data["y"]
                all_z = data["z"]
                all_a = data["activity"]
                all_t = data["t"]
        print(f"Shape de toutes les datas: {all_x.shape}")

        norme_act = []
        for i in range(all_x.shape[0]):
            norme = int((all_x[i]**2 + all_y[i]**2 + all_z[i]**2 )**0.5)
            act = all_a[i]
            temps = all_t[i]
            norme_act.append([norme, act, temps])

        return norme_act

    def get_paquets_labels(self):
        """groupes = [
                        [norme1, norme2, ...]  activité=0
                        [norme1, norme2, ...]  activité=1
                        ....
                                            ]
        paquets = train et test             = [ paquet1, paquet2, ...]
        labels =  train_label et test_label = [ 0,       3,       ...]
        """

        # activité 0   1   2   3
        groupes = [[], [], [], []]
        for norm, act in self.norme_act:
            groupes[act].append(norm)

        paquets, labels = [], []
        for i in range(len(groupes)):
            print(f"Activité: {i} Nombre de datas dans le groupe: {len(groupes[i])}")
            # nombre de paquets possible
            nb_possible = int((len(groupes[i]) - self.PAQUET)/self.gliss)
            print(f"Nombre de paquets possibles: {nb_possible}")
            if nb_possible > 0:
                for p in range(nb_possible):
                    # si i=0, activité=0, les datas sont groupe[0]
                    debut = p * self.gliss
                    fin   = debut + self.PAQUET
                    # #print(p, nb_possible, debut, fin, len(groupes[i]))
                    paquets.append(groupes[i][debut:fin])
                    labels.append(i)
        # #for j in range(len(paquets)):
            # #print(paquets[j], labels[j])
        return paquets, labels

    def get_train_test_trainlabel_testlabel(self, paquets, labels):
        """Le shuffle se fait en conservant la correspondance entre l'indice
        du paquet(50,) et son label.Je convertit en array à la fin"""

        par_couple = {}
        p = 0
        for p in range(len(paquets)):
            par_couple[p] = (paquets[p], labels[p])

        train, test, trainlabel, testlabel = [], [], [], []
        # Nombre de paquets pour le training
        n_train = int(len(paquets)*0.8)

        # liste de nombre au hasard qui seront les indices
        hasard = [x for x in range(len(par_couple))]
        random.shuffle(hasard)

        for item in hasard[:n_train]:
            train.append(par_couple[item][0])
            trainlabel.append(par_couple[item][1])
        for item in hasard[n_train:]:
            test.append(par_couple[item][0])
            testlabel.append(par_couple[item][1])

        # Conversion en array
        train = np.array(train)
        test = np.array(test)
        trainlabel = np.array(trainlabel)
        testlabel = np.array(testlabel)

        return train, test, trainlabel, testlabel

    def save_npz(self, train, test, trainlabel, testlabel):

        print((f"Vérification des shapes avant enregistrement: {train.shape}"
              f"{test.shape} {trainlabel.shape} {testlabel.shape}"))


        outfile = (f'./npz_final/keras_{self.PAQUET}_{self.gliss}.npz')
        print('Fichier compressé =', outfile)
        np.savez_compressed(outfile, **{"train": train,
                                        "test": test,
                                        "trainlabel": trainlabel,
                                        "testlabel":  testlabel})


def create_dir(my_path_directory):
    Path(my_path_directory).mkdir(mode=0o777, parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
