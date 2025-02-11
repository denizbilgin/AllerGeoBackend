from typing import AnyStr, Optional, Dict, List, TYPE_CHECKING
from difflib import SequenceMatcher
from django.utils.text import slugify
import os
from googletrans import Translator
if TYPE_CHECKING:
    from places.models import District


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


def similarity_ratio(string1: AnyStr, string2: AnyStr) -> float:
    return SequenceMatcher(None, string1, string2).ratio()


def find_similar_place(place_name: AnyStr, similarity_threshold: float = 0.3) -> Optional[AnyStr]:
    districts = District.objects.all()
    similar_names: Dict[float, AnyStr] = {}

    def add_similar_name(name: AnyStr, score: float) -> None:
        if len(place_name) == len(name) and score > similarity_threshold:
            similar_names[score] = name

    for district in districts:
        city_similarity_score = similarity_ratio(place_name, district.city.name)
        add_similar_name(district.city.name, city_similarity_score)

        district_name_last_part = district.name.split(" ")[-1]
        district_similarity_score = similarity_ratio(place_name, district_name_last_part)
        add_similar_name(district_name_last_part, district_similarity_score)
    if not similar_names:
        return None
    return similar_names[max(similar_names.keys())]


def define_user_photo_path(instance, filename: str) -> AnyStr:
    name_slug = slugify(f"{instance.first_name}_{instance.last_name}")
    extension = os.path.splitext(filename)[1]
    photo_path = f"{instance.id}_{name_slug}{extension}"
    return f"profile_photos/{photo_path}"


async def translate_to_turkish(common_names: Dict[AnyStr, AnyStr], languages_priority: List[AnyStr] = ["fra", "eng", "deu"]) -> AnyStr:
    translator = Translator()
    for lang in languages_priority:
        if lang in common_names.keys():
            text_to_translate = common_names[lang]
            translation = await translator.translate(text=text_to_translate, src=lang[:-1], dest="tr")
            return translation.text

    if common_names:
        text_to_translate = next(iter(common_names.values()))
        translation = await translator.translate(text_to_translate, src='auto', dest='tr')
        return translation.text

    return "No translation available."
