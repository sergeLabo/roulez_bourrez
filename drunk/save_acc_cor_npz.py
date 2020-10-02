#!/usr/bin/env python3


import numpy as np
from get_phones import get_phones_list, get_phones_type
import os


def get_acc_cor(phone):
    print("\n\n\n\n", phone)
    phone_data = np.load('./phones_npz/' + phone + '.npz')

    t = phone_data['time']  # array
    x = phone_data['x']  # array
    y = phone_data['y']  # array
    z = phone_data['z']  # array

    a = []
    for it in t:
        a.append(it)
    a = sorted(a)
    print(a[-1])

    # Vérification des shape des array
    shap = t.shape
    if x.shape != shap: print("Erreur shape")
    if y.shape != shap: print("Erreur shape")
    if z.shape != shap: print("Erreur shape")
    # Par lecture des csv et création des npz, les erreurs de shape sont impossibles

    # Calcul des moyenne par axe
    x_average = np.average(x)
    x_std = np.std(x)
    print(f"       x: Moyenne = {round(x_average, 6)} Ecart type = {round(x_std, 6)}")

    y_average = np.average(y)
    y_std = np.std(y)
    print(f"       y: Moyenne = {round(y_average, 6)} Ecart type = {round(y_std, 6)}")

    z_average = np.average(z)
    z_std = np.std(z)
    print(f"       z: Moyenne = {round(z_average, 6)} Ecart type = {round(z_std, 6)}")

    acc_sum = 0
    n = 0
    for i in range(len(x)):
        if is_valable(x[i]) and is_valable(y[i]) and is_valable(z[i]):
            acc_sum += (x[i]**2 + y[i]**2 + z[i]**2 )**0.5
            n += 1
    acc = acc_sum / n
    print(f"    Accélération moyenne = {round(acc, 6)}")

    t_cor, x_cor, y_cor, z_cor = delete_unusual(t, x, y, z)
    # Calcul des moyenne par axe corrigée
    print("\n\n    Correction")
    x_cor_average = np.average(x_cor)
    x_cor_std = np.std(x_cor)
    print(f"      x: Moyenne = {round(x_cor_average, 6)} Ecart type = {round(x_cor_std, 6)}")
    y_cor_average = np.average(y_cor)
    y_cor_std = np.std(y_cor)
    print(f"      y: Moyenne = {round(y_cor_average, 6)} Ecart type = {round(y_cor_std, 6)}")
    z_cor_average = np.average(z_cor)
    z_cor_std = np.std(z_cor)
    print(f"      z: Moyenne = {round(z_cor_average, 6)} Ecart type = {round(z_cor_std, 6)}")

    acc_cor_sum = 0
    for i in range(len(x_cor)):
        acc_cor_sum += (x_cor[i]**2 + y_cor[i]**2 + z_cor[i]**2 )**0.5
    acc_cor = acc_cor_sum / i
    print(f"      Accélération moyenne = {round(acc_cor, 6)}")

    t = np.array(t_cor)
    x = np.array(x_cor)
    y = np.array(y_cor)
    z = np.array(z_cor)

    return t, x, y, z

def save_phone_data_to_phone_npz(phone):

    t, x, y, z = get_acc_cor(phone)
    outfile = './phones_cor_npz/' + phone + '.npz'
    np.savez_compressed(outfile, **{"time":  np.asarray(t),
                                    "x": np.asarray(x),
                                    "y": np.asarray(y),
                                    "z": np.asarray(z)})
    print('    Fichier compressé =', outfile)

def is_valable(a):
    """Supression des valeurs très petite ou très grande"""

    if a < 10000  and not a < -10000:
        return True
    else:
        return False

def delete_unusual(t, x, y, z):
    """Suppression des valeurs anormales
            Acc très grande ou très petite
            TimeStamp à 0
    """

    print("\n\n    Suppression des valeurs anormales")
    t_cor, x_cor, y_cor, z_cor = [], [], [], []
    n = 0
    for i in range(len(x)):
        if is_valable(x[i]) and is_valable(y[i]) and is_valable(z[i])\
        and t[i] > 10000:
            t_cor.append(t[i])
            x_cor.append(x[i])
            y_cor.append(y[i])
            z_cor.append(z[i])
        else:
            n += 1
    print(f"      Nombre de valeurs totale = {i}")
    print(f"      Nombre de valeurs exclue = {n}")

    return t_cor, x_cor, y_cor, z_cor

def main():
    # Tac des phones
    phones = get_phones_list()
    for phone in phones:
        save_phone_data_to_phone_npz(phone)




if __name__ == "__main__":
    main()
