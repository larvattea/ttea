import cv2 as cv


img = cv.imread("udescjoinvilleiputil\projecao1.jpg")
img_gray =  cv.cvtColor(img, cv.COLOR_BGR2GRAY)

canny_edges = cv.Canny(img_gray, threshold1= 300, threshold2=400)




cv.imwrite("teste.png", canny_edges)
cv.waitKey(0)

