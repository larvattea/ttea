import cv2 as cv
from PIL import Image
from numpy import array
from math import atan2

capture = cv.VideoCapture(0); 

returned, img =  capture.read()
img_gray =  Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2GRAY)) 
img_gray =  img_gray.convert('L')
img_gray=  array(img_gray)

sobel_Gx =  [-2, -1, 0,
             -1,  0,  1,
              0,  1,  2,]

sobel_Gy = [ -1, -2, -1,
              0, 0 , 0,  
              1, 2,  1 ]


gradiente =  []


for i in range(1, len(img_gray)-1): 
    for j in range(1, len(img_gray[1])-1):
        Gx = 0
        Gy = 0

        pixel_neighbors = [
                            img_gray[i-1][j-1], img_gray[i-1][j], img_gray[i-1][j+1],
                            img_gray[i][j-1], img_gray[i][j], img_gray[i][j+1],  
                            img_gray[i+1][j-1], img_gray[i+1][j], img_gray[i+1][j+1]
                         ]

        for k in range(len(sobel_Gy)):  
            Gx += pixel_neighbors[k] * sobel_Gx[k]  
            Gy +=  pixel_neighbors[k] * sobel_Gy[k]
    
        
        img_gray[i][j] =  abs(Gx) + abs(Gy)

        if img_gray[i][j] < 180: 
            img_gray = 255
        
        else: 
            img_gray = 0


final_img =  Image.fromarray(img_gray)

final_img.show()
