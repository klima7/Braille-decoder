from segmentator import *
from analyzer import Analyzer
import cv2

path = 'images/real/1.png'
dot_size = 100


image = cv2.imread(path, 0)
thresh, segments = Segmentator.segment(image, dot_size, True)
text = Analyzer.analyse(thresh, segments)
print('Decoded text: %s' % text)





