import numpy as np
from PIL import Image

imagem2 =  Image.open("udescjoinvilleiputil\projecao.jpg")

imagem = imagem2.convert('L')
img_matrix =  np.asarray(imagem)


sobel_Gx =  [-1, -2,  -1, 
              0,  0,  0,
              1,  2,  1]

sobel_Gy = [ -1, 0,  1,
             -2, 0 , 2,  
             -1, 0, 1 ]


limit = 150

pixels = []

for i in range(1, len(img_matrix)-1):
    for j in range(1, len(img_matrix[0])-1): 
        Gx = 0 
        
            
        pixel_neighbors = [
                            img_matrix[i-1][j-1], img_matrix[i-1][j], img_matrix[i-1][j+1],
                            img_matrix[i][j-1],  img_matrix[i][j], img_matrix[i][j+1],  
                            img_matrix[i+1][j-1], img_matrix[i+1][j], img_matrix[i+1][j+1]
                        ]

        
        for k in range(len(sobel_Gx)):  
            Gx += pixel_neighbors[k] * sobel_Gx[k]
    


for i in range(len(pixels)): 
    x,y = pixels[i][1]
    imagem2.putpixel((y,x), (255,0,0))


imagem2.save("Teste12.png")
