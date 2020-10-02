#!/usr/bin/env python3

import os
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from get_phones import get_phones_list


def get_train():
    train_acc = np.zeros((1, 400, 3))
    train_label = np.zeros((1, ))
    for phone in get_phones():
        train_acc_array, train_label_array = get_train_acc_array_train_label_array(phone)
        train_acc = np.concatenate((train_acc, train_acc_array), axis=0)
        train_label = np.concatenate((train_label, train_label_array), axis=0)
        print("Shape", train_acc.shape, train_label.shape)

    return train_acc, train_label

def get_train_acc_array_train_label_array(phone):

    phone_data = np.load('./phones_cor_npz/' + phone + '.npz')

    t = phone_data['time']
    x = phone_data['x']
    y = phone_data['y']
    z = phone_data['z']
    print("Nombre de data:", t.shape[0], x.shape[0], y.shape[0], z.shape[0])

    paquet = 0
    nums = 0
    combien_de_paquet = int(len(t)/400) # que des paquets de 400
    train_acc_array = np.zeros((combien_de_paquet, 400, 3))
    train_label_array = np.zeros((combien_de_paquet, ))
    print(f"Nombre de paquets possible = {combien_de_paquet}")
    for i in range(combien_de_paquet*400):
        if paquet < 400:
            train_acc_array[nums, paquet, 0] = x[i]
            train_acc_array[nums, paquet, 1] = y[i]
            train_acc_array[nums, paquet, 2] = z[i]
            paquet += 1
        else:
            paquet = 0
            nums += 1
            train_label_array[nums] = 0.0

    # train_acc_array.shape = (2944, 400, 3)

    return train_acc_array, train_label_array

def save_data_npz(train_data, train_label, test_data, test_label):

    outfile = './datas.npz'
    np.savez_compressed(outfile, **{'train_data':  train_data,
                                    'train_label': train_label,
                                    'test_data':   test_data,
                                    'test_label':   test_label})
    print('Fichier compressé =', outfile)

def get_acc_tac(phone):
    # acc
    phone_acc = np.load('./phones_cor_npz/' + phone + '.npz')
    t_acc = phone_acc['time']
    x_acc = phone_acc['x']
    y_acc = phone_acc['y']
    z_acc = phone_acc['z']  # array
    acc_debut = datetime.fromtimestamp(t_acc[0]).strftime("le %d à %H:%M")
    acc_fin = datetime.fromtimestamp(t_acc[-1]).strftime("le %d à %H:%M")
    print("Valeurs d'accélération:")
    print(f"    Debut {acc_debut}\n    Fin {acc_fin}")
    # tac
    phone_tac = np.load('./tac_npz/' + phone + '.npz')
    t_tac = phone_tac['time']
    tac = phone_tac['tac']
    tac_debut = t_tac[0]
    dt_debut = datetime.fromtimestamp(tac_debut).strftime("le %d à %H:%M")
    tac_fin = t_tac[-1]
    dt_fin = datetime.fromtimestamp(tac_fin).strftime("le %d à %H:%M")

    print("Enregistrement des TAC:")
    print(f"    Debut {dt_debut}\n    Fin {dt_fin}")

    return t_acc, x_acc, y_acc, z_acc, t_tac, tac, acc_debut, acc_fin, tac_debut, tac_fin

def plot(phone):
    """
    Phone: CC6740
        Valeurs d'accélération: Debut le 02 à 17:56
                                  Fin le 03 à 18:34
        Enregistrement des TAC: Debut le 02 à 13:10
                                  Fin le 03 à 13:09

    Parcours des t_acc, x_acc, y_acc, z_acc
    si t_acc > tac_fin:
        j'ajoute les valeurs avec tac = 0.0
    sinon:
        je recherche les acc des 10 secondes (soit paquet) avant la mesure de tac
    """

    t_acc, x_acc, y_acc, z_acc, t_tac, tac, acc_debut, acc_fin, tac_debut, tac_fin = get_acc_tac(phone)

    # #scan_null_acc(t_acc, x_acc, y_acc, z_acc)
    # #plot_acc(phone, t_acc, x_acc, y_acc, z_acc)
    # #plot_tac(phone, t_tac, tac)
    plot_acc_tac(phone, t_acc, x_acc, y_acc, z_acc, t_tac, tac)

def scan_null_acc(t_acc, x_acc, y_acc, z_acc):
    acc = []
    for i in range(len(t_acc)):
        v = (x_acc[i]**2 + y_acc[i]**2 + z_acc[i]**2 )**0.5
        acc.append(v)
        print(v)

def plot_acc_tac(phone, t_acc, x_acc, y_acc, z_acc, t_tac, tac):
    acc = []
    for i in range(len(x_acc)):
        acc.append((x_acc[i]**2 + y_acc[i]**2 + z_acc[i]**2 )**0.5)

    dt_acc = []
    for it in t_acc:
        dt_acc.append(datetime.fromtimestamp(it))  # .strftime("le %d à %H:%M")
    dt_tac = []
    for it in t_tac:
        dt_tac.append(datetime.fromtimestamp(it))

    fig, ax1 = plt.subplots(1, 1, figsize=(10,10), facecolor='#cccccc')
    ax1.set_facecolor('#eafff5')
    ax1.set_title("Roulez Bourrez " + phone , size=24, color='magenta')

    color = 'tab:green'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Accélération', color=color)
    a = ax1.scatter(dt_acc, acc,
                    marker = 'X',
                    # #linestyle="-",
                    linewidth=0.05,
                    color='green',
                    label="Accélération")
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx() # instantiate a second axes that shares the same x-axis
    color = 'tab:red'
    ax2.set_ylabel('Alcoolémie', color=color)  # we already handled the x-label with ax1
    ax2.tick_params(axis='y', labelcolor=color)

    b = ax2.plot(dt_tac, tac,
                linestyle="-",
                linewidth=1.5,
                color='red',
                label="Alcoolémie")

    # Définition de l'échelle des x
    mini = min(dt_acc[0], dt_tac[0])
    maxi = max(dt_acc[-1], dt_tac[-1])
    ax2.set_xlim(mini, maxi)
    ax2.set_xlim(mini, maxi)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    ax1.legend(loc="upper center")
    ax2.legend(loc="upper right")

    fig.savefig("./courbe/acc_tac_" + phone + "_scatter.png")
    plt.show()

def plot_acc(phone, t_acc, x_acc, y_acc, z_acc):
    print(f"Shape des array:")
    print(f"    timestamp: {t_acc.shape}")
    print(f"    x: {x_acc.shape}")
    print(f"    y: {y_acc.shape}")
    print(f"    z: {z_acc.shape}")
    # #for i in range(len(t_acc)):
        # #dt = datetime.fromtimestamp(t_acc[i]).strftime("Acc le %d à %H:%M")
        # #if i % 14400 == 0:
            # #print(dt)

    acc = []
    for i in range(len(x_acc)):
        acc.append((x_acc[i]**2 + y_acc[i]**2 + z_acc[i]**2 )**0.5)

    fig, ax = plt.subplots(1, 1, figsize=(30,10), facecolor='#cccccc')

    a = ax.plot(t_acc, acc,
                linestyle="-",
                linewidth=1.5,
                color='green',
                label="Accélération")

    ax.legend(loc="upper right", title="Mouvement du téléphone")
    fig.savefig("./courbe/acc_" + phone + ".png")
    plt.show()

def plot_tac(phone, t_tac, tac):

    fig, ax = plt.subplots(1, 1, figsize=(10,10), facecolor='#cccccc')

    a = ax.plot(t_tac, tac,
                linestyle="-",
                linewidth=1.5,
                color='green',
                label="Alcoolémie")

    ax.legend(loc="upper right", title="TAC")
    fig.savefig("./courbe/tac_" + phone + ".png")
    plt.show()

def main():
    # #get_learning_npz("BK7610", 400)
    # Tac des phones
    phones = get_phones_list()
    for phone in phones:
        print(f"\n\nPhone: {phone}")
        plot(phone)


if __name__ == "__main__":
    main()

def bazard():
    """
    # #for item in t_acc:
        # #if float(item) > tac_debut:
            # #n += 1
        # #else: break
    # #print("fin", len(t_acc), n)
    # #os._exit(0)

    # #acc_debut = []
    # #label_debut = []
    # #for i in range(len(t_acc)):
        # ## tac = 0.0
        # #if t_acc < tac_debut:

        # ## tac des tac.csv
        # #elif tac_debut < t_acc < tac_fin:


        # ## tac = 0.0
        # #elif tac_fin < t_acc :


    # #p = 0
    # #nums = 0
    # #combien_de_p = int(len(t)/400) # que des ps de 400
    # #acc_array = np.zeros((combien_de_p, 400, 3))
    # #label_array = np.zeros((combien_de_p, ))
    # #print(f"Nombre de ps possible = {combien_de_p}")
    # #for i in range(combien_de_p*400):
        # #if p < 400:
            # #acc_array[nums, p, 0] = x[i]
            # #acc_array[nums, p, 1] = y[i]
            # #acc_array[nums, p, 2] = z[i]
            # #p += 1
        # #else:
            # #p = 0
            # #nums += 1
            # #label_array[nums] = 0.0

    # acc_array.shape = (2944, 400, 3)
    """
    pass
