from datetime import datetime
import re
import unicodedata

from allocine.constants import DEFAULT_DATE_FORMAT


def str_datetime_to_datetime_obj(datetime_str, date_format=DEFAULT_DATE_FORMAT):
    return datetime.strptime(datetime_str, date_format)


def _cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def clean_synopsis(raw_synopsis):
    if raw_synopsis is None:
        return None

    synopsis = _cleanhtml(raw_synopsis)  # Remove HTML tags (ex: <span>)
    synopsis = synopsis.replace("\xa0", " ")
    return unicodedata.normalize("NFKD", synopsis)


def strip_accents(s):
    # https://stackoverflow.com/a/518232/8748757
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )
