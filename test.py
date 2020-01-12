import braille
import cv2

image = cv2.imread('images/computer/15.png', 0)
text = braille.decode(image, 37, True)
print('Decoded text: %s' % text)



