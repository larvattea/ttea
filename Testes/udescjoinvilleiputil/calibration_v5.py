import cv2 as cv
import numpy as np

gray = cv.cvtColor(cv.VideoCapture(0).read()[1], cv.COLOR_BGR2GRAY)

grad_x = cv.Sobel(gray, cv.CV_32F, 1, 0, ksize=3)
grad_y = cv.Sobel(gray, cv.CV_32F, 0, 1, ksize=3)

magnitude = 0.5 * np.abs(grad_x) + 0.5 * np.abs(grad_y)

_, edges = cv.threshold(magnitude, 180, 255, cv.THRESH_BINARY)

cv.imshow("Edges", edges.astype(np.uint8))
cv.waitKey(0)
cv.destroyAllWindows()
