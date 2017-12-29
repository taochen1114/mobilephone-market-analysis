#coding=utf-8
# 練習使用 bass diffusion model 做 regression
# 練習 multiprocess 的用法
import math 
import os 
import time
# import keras
# from keras.layers import Input,Dense,Activation,Reshape,Flatten,Dropout
# from keras.models import Sequential,Model
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

if __name__=='__main__':
    # NCCU = [0.0019, 0.0041, 0.0096, 0.0185, 0.0257, 0.0276, 0.0362, 0.0451, 0.0686, 0.2156, 0.5224, 0.8024, 0.9724, 1.083, 1.1441, 1.0031, 0.9737, 1.016, 1.058, 1.103]
    N = [0.0019, 0.0041, 0.0096, 0.0185, 0.0257, 0.0276, 0.0362, 0.0451, 0.0686, 0.2156, 0.5224, 0.8024, 0.9724, 1.083, 1.1441, 1.0031, 0.9737, 1.016, 1.058]
    delta_N = [0.0019, 0.0022, 0.0055, 0.0089, 0.0072, 0.0019, 0.0086, 0.0089, 0.0235, 0.147, 0.3068, 0.28, 0.17, 0.1106, 0.0611, -0.141, -0.0294, 0.0423, 0.042]

    # 調整
    # N = [0.002145,0.004542,0.009893,0.019413,0.0265,0.0328,0.0525,0.0667,0.1146,0.2156,0.5224,0.6324,0.726056,0.80259,0.840813,0.8331,0.8537,0.906,0.948]
    # delta_N = [0.002145, 0.002397, 0.005351, 0.00952, 0.007087, 0.0063, 0.0197, 0.0142, 0.0479, 0.101, 0.3068, 0.11, 0.093656, 0.076534, 0.038223, -0.007713, 0.0206, 0.0523, 0.042]

    # 亼N=mp+(q-p)Ni-1-(q/m)Ni-1^2
    # i = 1
    # delta_N[i] = m*p + (q-p)*N[i-1]-(q/m)*N[i-1]*N[i-1]
    # a1 = 0
    # a2 = 0
    # a3 = 0
    # delta_N[i] = a1 + a2 * N[i-1] - a3 * N[i-1] * N[i-1]

    Y = delta_N[1:]
    print(Y)
    print(len(Y))
    X = N[:-1]
    print(X)
    print(len(X))
    X_train = []
    y_train = []
    for y in Y:
        y_train.append([y])
    for x in X:
        X_train.append([x])
    print('X_train',X_train)
    print('y_trainy',y_train)
    

    quadratic_featurizer = PolynomialFeatures(degree=2)
    X_train_quadratic = quadratic_featurizer.fit_transform(X_train)
    # X_test_quadratic = quadratic_featurizer.transform(X_test)
    regressor_quadratic = LinearRegression()
    regressor_quadratic.fit(X_train_quadratic, y_train)
    # plt.plot(X_train, y_train, 'k.')
    # plt.plot(regressor_quadratic.predict(X_train),'r-')
    # xx_quadratic = quadratic_featurizer.transform(y_train.reshape(xx.shape[0], 1))
    # plt.plot(y_train, regressor_quadratic.predict(xx_quadratic), 'r-')
    # plt.show()

    print(X_train_quadratic)
    # print('二次回归 r-squared', regressor_quadratic.score(X_test_quadratic, y_test))
    print('a, b, c :',regressor_quadratic.get_params())
    print('r-squared', regressor_quadratic.score(X_train_quadratic, y_train))

