import numpy as np
import cv2

a = np.array([
    [[255, 0, 0],
     [255, 255, 255],
     [255, 255, 255],
     [287, 41, 160]],

    [[255, 255, 255],
     [255, 255, 255],
     [255, 255, 255],
     [255, 255, 255]],

    [[255, 255, 255],
     [0, 0, 0],
     [47, 255, 173],
     [255, 255, 255]]
])

cv2.imwrite('image.png', a)