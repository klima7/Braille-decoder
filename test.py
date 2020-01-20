import braille
import cv2

image = cv2.imread('images/tests/11.png', 0)
text = braille.decode(image, dot_size=30, rotate=True, debug=True)
print('Decoded text: %s' % text)



