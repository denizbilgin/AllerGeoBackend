from typing import AnyStr, TYPE_CHECKING
from math import radians, sin, cos, sqrt, atan2


def turkish_lowercase(text: AnyStr) -> AnyStr:
    """
    Turkish lowercase function that basically converts the letters I and İ to lowercase.
    :param text: Text to be written in lowercase
    :return: Turkish lowercased text
    """
    translation_table = str.maketrans(
        "Iİ",
        "ıi"
    )
    return text.translate(translation_table).lower()


def turkish_capitalize(text: str, apply_each_word: bool = True) -> str:
    """
    Turkish capitalize function that capitalizes the first letter
    of the given text using Turkish uppercase and lowercase rules.
    :param apply_each_word: If True, capitalizes each word in the text
    :param text: Text to be capitalized
    :return: Turkish capitalized text
    """
    if not text:
        return text
    text = text.strip()

    if apply_each_word:
        words = text.split()
        capitalized_words = [
            turkish_uppercase(word[0]) + turkish_lowercase(word[1:]) for word in words
        ]
        return " ".join(capitalized_words)

    return turkish_uppercase(text[0]) + turkish_lowercase(text[1:])


def turkish_uppercase(text: AnyStr) -> AnyStr:
    """
    Turkish uppercase function that basically converts the letters ı and i to uppercase.
    :param text: Text to be written in uppercase
    :return: Turkish uppercased text
    """
    translation_table = str.maketrans(
        "ıi",
        "Iİ"
    )
    return text.translate(translation_table).upper()


def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0

    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = sin(d_lat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def is_inside_turkey(lat, lon):
    return 36.0 <= lat <= 42.0 and 26.0 <= lon <= 45.0