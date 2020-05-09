# -*- coding: utf-8 -*-
# @Time    : 2018/4/2 10:14
# @Author  : Jiahui Zhang
# @Email   : zjiahui96@gmail.com
# @File    : pocs.py
# @Software: PyCharm

import numpy as np
from PIL import Image
from image_pretreatment import *
import scipy.ndimage
import cv2


######################
# 凸集反投影算法(POCS) #
######################
def pocs(images, delta_est, factor):
    img = images[0]
    img1 = generateimage(img)

    # 对灰度图进行POCS算法处理
    temp = zoomzero(img1, factor)   #将LR图像补零插值
    y = np.zeros(temp.shape)
    coord = temp.nonzero()     #找出非零元素的坐标
    y[coord] = temp[coord]     #将非零元素投影到构造的初始估计HR图像处

    for i in range(1, len(images)):
        tempimage = generateimage(images[i])
        temp = zoomzero(tempimage, factor)

        temp = roll(temp, int(round(factor * delta_est[i, 1])), 1)
        temp = roll(temp, int(round(factor * delta_est[i, 0])), 0)

        coord = temp.nonzero()
        y[coord] = temp[coord]

    y_prev = y

    max_iter = 100
    iter = 1
    E = zeros([1000, 2])

    blur = np.matrix([[0.25, 0, 1, 0, 0.25], [0, 1, 2, 1, 0], [1, 2, 4, 2, 1], [0, 1, 2, 1, 0], [0.25, 0, 1, 0, 0.25]])
    blur = blur / sum(blur)

    # 进行迭代
    while iter < max_iter:
        y = cv2.filter2D(y, -1, blur)
        for i in range(len(images) - 1, -1, -1):
            tempimage = generateimage(images[i])
            temp = zoomzero(tempimage, factor)

            temp = roll(temp, int(round(factor * delta_est[i, 1])), 1)
            temp = roll(temp, int(round(factor * delta_est[i, 0])), 0)

            coord = temp.nonzero()
            y[coord] = temp[coord]

        delta = linalg.norm(y_prev - y) / linalg.norm(y)
        E[iter][0] = iter
        E[iter][1] = delta
        if iter > 3:
            if abs(E[iter - 4, 1] - delta) < 1e-5:
                break
        y_prev = y
        iter = iter + 1

    imagesize = y.shape
    height = imagesize[0]
    width = imagesize[1]

    for i in range(height):
        for j in range(width):
            y[i][j] = y[i][j] * 255

    temp_result = zeros((height, width), 'uint8')
    for i in range(height):
        for j in range(width):
            temp_result[i][j] = y[i][j]

    result = Image.fromarray(temp_result, mode='L')

    print("the " + str(iter) + " accuracy is: " + str(1 - round(delta, 7)))

    return result
