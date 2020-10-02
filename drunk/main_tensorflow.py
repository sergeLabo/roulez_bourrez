#!/usr/bin/env python3

import numpy as np
from tensorflow import keras
from get_phones import get_phones_list

epochs = 3

def main(phone):

    train_data, train_label, test_data, test_label = get_train_test_datas()
    model = build_the_model()
    model = compile_the_model(model)
    model = training_the_model(model, train_data, train_label, epochs)

def get_train_test_datas():

    datas = np.load('./datas.npz')
    train_data = datas['train_data']
    train_label = datas['train_label']
    test_data = datas['test_data']
    test_label = datas['test_label']

    return train_data, train_label, test_data, test_label

def build_the_model():
    print("\n\n\nBuild the model ...")

    input1 = keras.layers.Input(shape=(400, 3))

    x1 = keras.layers.Dense(128, activation='relu')(input1)
    x2 = keras.layers.Dense(128, activation='relu')(input1)
    added = keras.layers.add([x1, x2])

    out = keras.layers.Dense(1, activation='sigmoid')(added)
    model = keras.models.Model(inputs=[input1], outputs=out)

    print("Build done.")
    return model

def compile_the_model(model):
    print("\n\n\nCompile the model ...")

    model.compile(  optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy'] )

    print("Compile done.")
    return model

def training_the_model(model, train_data, train_label, epochs):
    print("\n\n\nTraining the model ...")

    model.fit(train_data, train_label, epochs=epochs)

    print("Training done.")
    return model


if __name__ == "__main__":

    main('JB3156')
