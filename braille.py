from segmentator import *
from analyzer import Analyzer
import cv2

path = 'images/real/1.png'
dot_size = 100

try:
    image = cv2.imread(path, 0)
    segments = Segmentator.segment(image, dot_size, True)
    text = Analyzer.analyse(image, segments)
    print('Decoded text: %s' % text)
except SegmentationException:
    print('Unable to segment image')




