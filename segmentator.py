import numpy as np
import matplotlib.pyplot as plt
import cv2
import skimage.morphology as morph
from scipy.signal import find_peaks


# Błąd segmentacji
class SegmentationException(Exception):
    pass


# Klasa odpowiedzialna za segmentacje - znalezienie poszczególnych znaków
class Segmentator:
    __debug = True
    __dot_size = 30
    __margin_factor = 1.3

    # Zwraca liczbę ustawionych pikseli na danej wysokości obrazka
    @staticmethod
    def __get_collide_count_v(img, height):
        count = 0
        for x in range(img.shape[1]):
            if img[height][x] == True:
                count += 1
        return count

    # Zwraca liczbe ustawionych pikseli na danej szerokości obrazka
    @staticmethod
    def __get_collide_count_h(img, width):
        count = 0
        for y in range(img.shape[0]):
            if img[y][width] == True:
                count += 1
        return count

    # Zwracą średnią różnicę pomiędzy kolejnymy liczbami na liście
    @staticmethod
    def __get_avg_distance_between(l):
        sum = 0
        last = l[0]
        for elem in l[1:]:
            sum += elem - last
            last = elem
        return sum / (len(l) - 1)

    # Filtr średniej ruchomej o rozmiarze okienka size
    @staticmethod
    def __avg_filter(list, size):
        return np.convolve(np.array(list), np.ones((size*2+1,)) / (size*2+1), mode='same').tolist()

    # Zwraca listę z indeksami znalezionych poziomich linii
    @staticmethod
    def __get_horizontal_lines(img):
        collisions = []
        for y in range(0, img.shape[0]):
            collisions.append(Segmentator.__get_collide_count_v(img, y))
        collisions = Segmentator.__avg_filter(collisions, int(Segmentator.__dot_size/2))
        # Rysuj wykres
        if Segmentator.__debug:
            plt.step(np.arange(len(collisions)), collisions)
            plt.title('Vertical scan result')
            plt.show()
        temp = find_peaks(collisions)
        vertical_maxs = temp[0].tolist()
        return vertical_maxs

    # Zwrac listę z indeksami znalezionych pionowych lini
    @staticmethod
    def __get_vertical_lines(img):
        collisions = []
        for x in range(0, img.shape[1]):
            collisions.append(Segmentator.__get_collide_count_h(img, x))
        collisions = Segmentator.__avg_filter(collisions, int(Segmentator.__dot_size/2))
        # Rysuj wykres
        if Segmentator.__debug:
            plt.step(np.arange(len(collisions)), collisions)
            plt.title('Horizontal scan result')
            plt.show()
        temp = find_peaks(collisions)
        horizontal_maxs = temp[0].tolist()
        return horizontal_maxs

    # Zwraca przerwe w poziomie pomiędzy kropkami tega samego znaku i pomiędzy sąsiednimi blokami 2x3
    @staticmethod
    def __get_small_big_space_vertical(lines):
        distances = [lines[i + 1] - lines[i] for i in range(len(lines) - 1)]
        mini = min(distances)
        maxi = max(distances)
        if maxi - mini > 0.1 * mini:
            distances = [lines[i + 1] - lines[i] for i in range(len(lines) - 1)]
            mini = min(distances)
            distances = list(filter(lambda x: mini * 1.2 < x, distances))
            space = min(distances)
            return mini, space
        else:
            return int(mini / 3), int(mini * 2 / 3)

    # Dodaje brakujące linie pionowe
    @staticmethod
    def __add_missing_vertical_lines(lines):
        small_space, big_space = Segmentator.__get_small_big_space_vertical(lines)

        # Dodaje pierwszą w razie konieczności
        if len(lines) > 1 and lines[1] - lines[0] < big_space * Segmentator.__margin_factor and not lines[1] - lines[
            0] < small_space * Segmentator.__margin_factor:
            new_line = lines[0] - small_space
            lines.insert(0, new_line)

        # Dodaje wszystkie środkowe
        i = 0
        while i < len(lines):
            if i + 1 < len(lines) and lines[i + 1] - lines[i] > small_space * Segmentator.__margin_factor:
                new_line = lines[i] + small_space
                lines.insert(i + 1, new_line)
            i += 1
            if i + 1 < len(lines) and lines[i + 1] - lines[i] > big_space * Segmentator.__margin_factor:
                new_line = lines[i] + big_space
                lines.insert(i + 1, new_line)
            i += 1

        # Dodaje końcową w razie konieczności
        if len(lines) > 1 and lines[-1] - lines[-2] > small_space * Segmentator.__margin_factor:
            new_line = lines[-1] + small_space
            lines.append(new_line)

        return lines

    # Znajduje odległość pomiędzy kolejnymi poziomymi liniami, a jak nie nie uda to zwraca orbitralną liczbę
    @staticmethod
    def __get_space_horizontal(lines):
        distances = [lines[i + 1] - lines[i] for i in range(len(lines) - 1)]
        if len(distances) > 0:
            return min(distances)
        else:
            return 10

    # Dodaje brakująca poziome linie
    @staticmethod
    def __add_missing_horizontal_lines(lines):
        space = Segmentator.__get_space_horizontal(lines)
        i = 0
        combo = 1
        while i < len(lines):
            if combo < 3 and (i == len(lines) - 1 or lines[i + 1] - lines[i] > space * Segmentator.__margin_factor):
                new_line = lines[i] + space
                lines.insert(i + 1, new_line)
            combo += 1
            i += 1
        return lines

    # Zamienia linie przechodzące przez kropki na prostokąty zawierające bloki
    @staticmethod
    def __cvt_lines_to_rects(horizontal, vertical):

        # Znajduje pionowe składowe
        def get_segments_vertical(lines):
            segments = []
            avg = Segmentator.__get_avg_distance_between(lines)
            margin = int(avg / 2)
            if len(lines) % 2 != 0:
                raise SegmentationException()

            i = 0
            while i < len(lines):
                l1 = lines[i]
                l2 = lines[i + 1]
                segment = (l1 - margin, l2 + margin)
                segments.append(segment)
                i += 2
            return segments

        # Znajduje poziome składowe
        def get_segments_horizontal(lines):
            segments = []
            avg = Segmentator.__get_avg_distance_between(lines)
            margin = int(avg / 3)
            if len(lines) % 3 != 0:
                raise SegmentationException()

            i = 0
            while i < len(lines):
                l1 = lines[i]
                l3 = lines[i + 2]
                segment = (l1 - margin, l3 + margin)
                segments.append(segment)
                i += 3
            return segments

        # Znajduje składowe poziome, pionowe i je łączy
        rects = []
        h_segments = get_segments_horizontal(horizontal)
        v_segments = get_segments_vertical(vertical)

        for h in h_segments:
            for v in v_segments:
                rect = [(v[0], h[0]), (v[1], h[1])]
                rects.append(rect)
        return rects

    # Dodaje współrzędne kropek do prostokątów
    @staticmethod
    def __add_dots(rectangles, horizontal, vertical):
        all_dots = []
        for h in horizontal:
            for v in vertical:
                all_dots.append((v, h))

        for rectangle in rectangles:
            temp = []
            for dot in all_dots:
                if rectangle[0][0] < dot[0] < rectangle[1][0] and rectangle[0][1] < dot[1] < rectangle[1][1]:
                    temp.append(dot)
            temp = sorted(temp, key=lambda k: [k[1], k[0]])
            rectangle.extend(temp)

    @staticmethod
    def segment(image, dot_size=30, debug=False):
        """
        Funkcja znajdująca segmenty, czyli poszczególne znaki na obrazie

        Parametry:
            image       -  Obraz w odcieniach szarości
            smoothing   -  Moc wygładzania, wymagane dla zdjęć wykonywanych aparatem (połowa średnicy kropki zwykle dobrze się sprawdza, średnicy=80 -> wygładzanie=40)
            dot_size    -  Średnica kropki, wymagana dla dopasowania mocy wygładzania i rozmiaru elementu strukturyzującego

        Wyjątki:
            Funkcja może zgłosić wyjątek klasy Exception gdy segmentacja obrazu się nie powiedzie

        Wartość zwracana:
            Zwracana jest lista znalezionych zegmentów, postaci [SEG, SEG, SEG, SEG, SEG...]
            Każdy segment SEG jest listą ośmiu punktów [POINT1, POINT2, POINT3, POINT4, POINT5, POINT6, POINT7, POINT8]
            POINT1 i POINT2 to współrzędne lewego-górnego i prawego-dolnego wierzchołka prostokątka zawierającego znaleziony znak
            POINT3, POINT4, POINT5, POINT6, POINT7, POINT8 - To współrzędne sześciu kropek wewnątrz znaku, uporządkowane wierszami:

            Rysunek pomocniczy:

                POINT1
                        POINT3 POINT4
                        POINT5 POINT6
                        POINT7 POINT8
                                        POINT2
        """

        # Ustawienie żądanych parametrów
        Segmentator.__dot_size = dot_size
        Segmentator.__debug = debug

        try:
            # Wyświetlenie obrazu początkowego
            if Segmentator.__debug:
                plt.imshow(image, 'gray')
                plt.title('Input Image')
                plt.show()

            cimg = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            # Negatyw
            image = 255-image

            # Progowanie adaptacyjne
            tresh = cv2.adaptiveThreshold(image, 0.8, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 2*Segmentator.__dot_size+1, 0)

            # Operacje morfologiczne
            struct_size = int(dot_size/3) if dot_size/3 < 15 else 15
            tresh = morph.binary_opening(tresh, morph.disk(struct_size))
            tresh = morph.binary_closing(tresh, morph.disk(struct_size))

            # Wyświetlenie wyniku
            if Segmentator.__debug:
                plt.imshow(tresh, 'gray')
                plt.title('Image segmentation result')
                plt.show()

            # Znalezienie widocznych linii
            horizontal_lines = Segmentator.__get_horizontal_lines(tresh)
            vertical_lines = Segmentator.__get_vertical_lines(tresh)

            # Dodanie brakujących linii
            vertical_lines = Segmentator.__add_missing_vertical_lines(vertical_lines)
            horizontal_lines = Segmentator.__add_missing_horizontal_lines(horizontal_lines)

            # Znalezienie segmentów
            segments = Segmentator.__cvt_lines_to_rects(horizontal_lines, vertical_lines)
            Segmentator.__add_dots(segments, horizontal_lines, vertical_lines)

            # Wyświetlenie wyniku segmentacji
            if Segmentator.__debug:
                for seg in segments:
                    cimg = cv2.rectangle(cimg, seg[0], seg[1], (0, 0, 255), int(dot_size/4))
                    for dot in seg[2:]:
                        cimg = cv2.circle(cimg, dot, int(dot_size/3), (255, 0, 0), -1)
                plt.title('Found characters')
                plt.imshow(cimg)
                plt.show()

        except:
            raise SegmentationException

        # Zwrócenie wyniku
        return tresh, segments
