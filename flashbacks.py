import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate


def sinusoida():
    x = np.linspace(0.0, 10.0, 500)  # диапазон и число точек
    y2 = 5.0 * np.sin(1.1 * x)  # амплитуда 5.0, частота 1.1
    noise = np.random.normal(0, 1, 500)
    plt.plot(x, y2+noise)
    plt.show()

def mov_av_my(a, n):
    aver = []
    if n <= len(a):
        start_i = 0
        stop_i = n-1
        while stop_i <= len(a)-1:
            sum = 0
            i = start_i
            while i <= stop_i:
                sum = sum + a[i]
                i += 1
            aver.append(sum/n)
            start_i += 1
            stop_i += 1

    return aver

def fnch_curve():
    x = np.linspace(0.0, 10.0, 100)
    y = np.random.uniform(0, 50, 100)
    f2 = interpolate.interp1d(x, y, kind='cubic')  # вычисление кубического полинома
    xnew = np.linspace(0, 1, 1000)
    noise = np.random.normal(0, 1, 1000)
    curve_noise = f2(xnew)+noise
    #curve_noise = noise
    w = 50
    x_fnch = moving_average(xnew, w)
    y_fnch = moving_average(curve_noise, w)

    start = int(w/2)
    end = len(curve_noise)-int(w/2)+1
    print(len(curve_noise[start:end ] ))
    print(len(y_fnch ))
    raznost = curve_noise[start:end ] - y_fnch
    offset = min(raznost)
    print("offset:"+ str(offset))
    y_fnch_real = y_fnch - offset
    #plt.plot(xnew, curve_noise, x_fnch, y_fnch_real)
    #plt.plot(xnew, curve_noise, xnew[start:end], y_fnch_real, xnew[start:end],y_fnch)
    plt.plot(xnew, curve_noise)
    plt.show()