import braille
import cv2

image = cv2.imread('images/tests/2.png', 0)
text = braille.decode(image, 30, True)
print('Decoded text: %s' % text)



