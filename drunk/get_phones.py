#!/usr/bin/env python3

"""
Retourne la liste des téléphones en liste,
ou en dict avec leur type
"""

android = [ 'JB3156',
            'CC6740']
iphone = [  'BK7610',
            'BU4707',
            'DC6359',
            'DK3500',
            'HV0618',
            'JR8022',
            'MC7070',
            'MJ8002',
            'PC6771',
            'SA0297',
            'SF3079']

def get_android_list():

    phones = []
    for p in android:
        phones.append(p)

    return phones

def get_iphones_list():

    phones = []
    for p in iphone:
        phones.append(p)

    return phones

def get_phones_list():

    phones = []
    for p in android:
        phones.append(p)
    for p in iphone:
        phones.append(p)

    return phones


def get_phones_type():

    phones = {}
    i = 0
    for p in android:
        phones[i] = [p, "android"]
        i += 1
    for p in iphone:
        phones[i] = [p, "iphone"]
        i += 1

    return phones
