#!python3

"""
keras avec des array input_shape=(50,)
le npz est créé automatiquement si besoin
git reset --hard origin/master
"""

# #import os
# ## Désactivation du GPU
# #os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import numpy as np
import random
from datetime import datetime
from tensorflow.keras import Sequential, layers, utils


def main_only_one():

    kwargs = {  "PAQUET": 50,
                "gliss": 1,  # paquets glissants
                "epochs": 3,
                "utils_to_categorical": 1,  # ne marche plus si 0 !
                "loss": 'categorical_crossentropy',  # 'binary_crossentropy'
                "optimizer": 'adam',  # 'SGD',
                "metrics": 'accuracy'}

    resp = ""
    ka = KerasActivity(**kwargs)
    test_acc = ka.one_training()
    print("\n", test_acc, "\n")

class KerasActivity:

    def __init__(self, **kwargs):

        self.kwargs = kwargs
        self.PAQUET = kwargs.get('PAQUET', None)
        self.gliss = kwargs.get('gliss', None)
        self.epochs = kwargs.get('epochs', None)
        self.utils_to_categorical = kwargs.get('utils_to_categorical', None)
        self.loss = kwargs.get('loss', None)
        self.optimizer = kwargs.get('optimizer', None)
        self.metrics = kwargs.get('metrics', None)

        self.model = None

    def one_training(self):

        infile = (f'./npz_final/keras_{self.PAQUET}_{self.gliss}.npz')
        print(f"\nInit ...")
        data = np.load(infile, allow_pickle=True)

        print(f"Chargement de       {infile}")
        train, test, trainlabel, testlabel = self.get_datas(data)
        print(f"Vérification des shapes: {train.shape} {test.shape} {trainlabel.shape} {testlabel.shape}")

        self.build_the_model()
        self.compile_the_model()
        self.training_the_model(train, trainlabel)
        test_acc = self.testing_the_model(test, testlabel)

        return test_acc

    def get_datas(self, data):

        train = data["train"]
        test = data["test"]

        if self.utils_to_categorical:
            trainlabel = utils.to_categorical(data["trainlabel"], 7)
            testlabel  = utils.to_categorical(data["testlabel"], 7)
        else:
            trainlabel = data["trainlabel"]
            testlabel  = data["testlabel"]

        return train, test, trainlabel, testlabel

    def build_the_model(self):
        print("Build the model ...")

        # Choix du model
        self.model = Sequential()

        # Input layer
        self.model.add(layers.Dense(units=4, input_shape=(self.PAQUET,)))
        self.model.add(layers.Flatten())

        # Hidden layer
        self.model.add(layers.Dense(8, activation='relu'))
        self.model.add(layers.Dense(64, activation='relu'))

        # Output
        self.model.add(layers.Dense(7, activation='softmax'))

        print(self.model.summary())

    def compile_the_model(self):
        """ optimizer='sgd' stochastic gradient descent"""

        print("Compile the model ...")
        self.model.compile(loss=self.loss,
                            optimizer=self.optimizer,
                            metrics=[self.metrics])

    def training_the_model(self, train, trainlabel):

        print("Training the model ...")
        self.model.fit(train, trainlabel, epochs=self.epochs)

    def testing_the_model(self, test, testlabel):

        print("Testing ......")
        test_loss, test_acc = self.model.evaluate(test, testlabel)

        return test_acc


if __name__ == "__main__":

    main_only_one()
