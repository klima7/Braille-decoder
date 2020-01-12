
class Analyzer:
    """
    Funkcja dekoduje pojedynczy segment

    Parametry:
        segment    -  Segment postaci [POINT3, ..., POINT8]
        flags      -  Flagi znakow specjalnych

        Letters    -  Slownik liter
        Numbers    -  Slownik cyfr
        Signs      -  Slownik znakow

    Wartość zwracana:
        Odczytany znak z segmentu
    """

    @staticmethod
    def decode_segment(segment, flags, letters, numbers, signs):

        for key, value in signs.items():
            if value == segment:
                if key in ['numeric', 'capital']:
                    flags[key] = True
                elif key in ['"', 'close_quote']:
                    flags['numeric'] = False
                    return '"'

                return key

        for key, value in numbers.items():
            if value == segment and flags['numeric'] is True:
                return key

        flags['numeric'] = False
        for key, value in letters.items():
            if value == segment:
                if flags["capital"] is True:
                    flags["capital"] = False
                    return key.capitalize()
                else:
                    return key
        return '?'

    @staticmethod
    def analyse(image, segments):
        """
        Funkcja analizuje obraz i zwraca odczytany tekst

        Parametry:
            image    -  Obraz w odcieniach szarości
            segments -  Segmenty znalezione przez segmentator

        Wartość zwracana:
            Odczytany z obrazu tekst
        """

        segments = [segment[2:] for segment in segments]
        for i, segment in enumerate(segments):
            for j, position in enumerate(segment):
                segments[i][j] = image[position[1]][position[0]]

        numbers = {
            '1': [1, 0, 0, 0, 0, 0],
            '2': [1, 0, 1, 0, 0, 0],
            '3': [1, 1, 0, 0, 0, 0],
            '4': [1, 1, 0, 1, 0, 0],
            '5': [1, 0, 0, 1, 0, 0],
            '6': [1, 1, 1, 0, 0, 0],
            '7': [1, 1, 1, 1, 0, 0],
            '8': [1, 0, 1, 1, 0, 0],
            '9': [0, 1, 1, 0, 0, 0],
            '0': [0, 1, 1, 1, 0, 0]
        }

        signs = {
            'numeric': [0, 1, 0, 1, 1, 1],
            'capital': [0, 0, 0, 0, 0, 1],
            'grade_1st': [0, 0, 0, 1, 0, 1],
            'close_quote': [0, 0, 0, 1, 1, 1],
            '.': [0, 0, 1, 1, 0, 1],
            ' ': [0, 0, 0, 0, 0, 0],
            ',': [0, 0, 1, 0, 0, 0],
            "'": [0, 0, 0, 0, 1, 0],
            '-': [0, 0, 0, 0, 1, 1],
            '!': [0, 0, 1, 1, 1, 0],
            '?': [0, 0, 1, 0, 1, 1],
            ':': [0, 0, 1, 1, 0, 0],
            '"': [0, 0, 1, 1, 1, 1],
        }

        letters = {
            'a': [1, 0, 0, 0, 0, 0],
            'b': [1, 0, 1, 0, 0, 0],
            'c': [1, 1, 0, 0, 0, 0],
            'd': [1, 1, 0, 1, 0, 0],
            'e': [1, 0, 0, 1, 0, 0],
            'f': [1, 1, 1, 0, 0, 0],
            'g': [1, 1, 1, 1, 0, 0],
            'h': [1, 0, 1, 1, 0, 0],
            'i': [0, 1, 1, 0, 0, 0],
            'j': [0, 1, 1, 1, 0, 0],
            'k': [1, 0, 0, 0, 1, 0],
            'l': [1, 0, 1, 0, 1, 0],
            'm': [1, 1, 0, 0, 1, 0],
            'n': [1, 1, 0, 1, 1, 0],
            'o': [1, 0, 0, 1, 1, 0],
            'p': [1, 1, 1, 0, 1, 0],
            'q': [1, 1, 1, 1, 1, 0],
            'r': [1, 0, 1, 1, 1, 0],
            's': [0, 1, 1, 0, 1, 0],
            't': [0, 1, 1, 1, 1, 0],
            'u': [1, 0, 0, 0, 1, 1],
            'v': [1, 0, 1, 0, 1, 1],
            'w': [0, 1, 1, 1, 0, 1],
            'x': [1, 1, 0, 0, 1, 1],
            'y': [1, 1, 0, 1, 1, 1],
            'z': [1, 0, 0, 1, 1, 1],
        }

        flags = {
            "numeric": False,
            "capital": False
        }

        text = []

        for segment in segments:
            last_sign = Analyzer.decode_segment(segment, flags, letters, numbers, signs)
            if last_sign not in ['numeric', 'capital', 'grade_1st', 'close_quote']:
                text.append(last_sign)
        text = "".join(text).strip()
        return text

