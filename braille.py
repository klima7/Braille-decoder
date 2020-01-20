from segmentator import Segmentator, SegmentationException
from analyzer import Analyzer


def decode(image, dot_size=100, rotate=False, debug=False):
    """
    Funkcja dekoduje tekst zakodowany w postaci kodu Braille'a

    Paremetry:
        image        - Obraz w odcieniach szarości
        dot_size     - Rozmiar kropki
        rotate       - Czy obraz ma być wypoziomowany automatycznie, czy poziomowanie nie musi być wykonywane
        debug        - Czy mają być wyświetlanie wyniki poszczególnych etapów

    Wartość zwracana
        Odczytany tekst w postaci napisu
    """

    try:
        thresh, segments = Segmentator.segment(image, dot_size, rotate, debug)
        text = Analyzer.analyse(thresh, segments)
        return text
    except SegmentationException:
        return "ERROR: Unable to decode text"





