from datetime import timedelta

import backoff
import jmespath
import requests

from data.cinemas import Cinema
from data.movies import MovieVersion
from data.showtimes import Showtime
from helpers.cleaners import clean_synopsis, str_datetime_to_datetime_obj
from .constants import BASE_URL, PARTNER_KEY

# === Client to execute requests with Allociné APIs ===
class SingletonMeta(type):
    _instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = super().__call__(*args, **kwargs)
        return self._instance


class Error503(Exception):
    pass


class Client(metaclass=SingletonMeta):
    """Client to process the requests with allocine APIs.
    This is a singleton to avoid the creation of a new session for every theater.
    """

    def __init__(self, base_url):
        self.base_url = base_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; \
                                   Intel Mac OS X 10.14; rv:63.0) \
                                   Gecko/20100101 Firefox/63.0",
        }
        self.session = requests.session()
        self.session.headers.update(headers)

    @backoff.on_exception(backoff.expo, Error503, max_tries=5, max_time=30)
    def _get(self, url: str, expected_status: int = 200, *args, **kwargs):
        ret = self.session.get(url, *args, **kwargs)
        if ret.status_code != expected_status:
            if ret.status_code == 503:
                raise Error503
            raise ValueError(
                "{!r} : expected status {}, received {}".format(
                    url, expected_status, ret.status_code
                )
            )
        return ret.json()

    def get_showtimelist_by_cinema_id(
        self, allocine_cinema_id: str, page: int = 1, count: int = 10
    ):
        url = (
            f"{self.base_url}/showtimelist?partner={PARTNER_KEY}&format=json"
            f"&theaters={allocine_cinema_id}&page={page}&count={count}"
        )
        return self._get(url=url)

    def get_cinema_info_by_id(self, allocine_cinema_id: str):
        url = f"{self.base_url}/theater?partner={PARTNER_KEY}&format=json&code={allocine_cinema_id}"
        return self._get(url=url)

    def get_showtimelist_from_geocode(
        self, geocode: int, page: int = 1, count: int = 10
    ):
        url = (
            f"{self.base_url}/showtimelist?partner={PARTNER_KEY}&format=json"
            f"&geocode={geocode}&page={page}&count={count}"
        )
        return self._get(url=url)

    def get_movie_info_by_id(self, movie_id: int):
        url = f"{self.base_url}/movie?partner={PARTNER_KEY}&format=json&code={movie_id}"
        return self._get(url=url)
