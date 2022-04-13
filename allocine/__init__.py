# -*- coding: utf-8 -*-

"""Top-level package for Allociné."""

from datetime import timedelta

import jmespath

from allocine.client import Client
from data.cinemas import Cinema
from data.movies import MovieVersion
from data.showtimes import Showtime
from helpers.cleaners import clean_synopsis, str_datetime_to_datetime_obj
from .constants import BASE_URL

# === Main class ===
class Allocine:
    def __init__(self, base_url=BASE_URL):
        self.__client = Client(base_url=base_url)
        self.__movie_store = (
            {}
        )  # Dict to store the movie info (and avoid useless requests)

    def get_cinema(self, allocine_cinema_id: str):
        ret = self.__client.get_showtimelist_by_cinema_id(
            allocine_cinema_id=allocine_cinema_id
        )
        if jmespath.search("feed.totalResults", ret) == 0:
            raise ValueError(
                f"Cinema not found. Is allocine_cinema_id {allocine_cinema_id!r} correct?"
            )

        cinemas = self.__get_cinemas_from_raw_showtimelist(raw_showtimelist=ret)
        if len(cinemas) != 1:
            raise ValueError("Expecting 1 cinema but received {}".format(len(cinemas)))

        return cinemas[0]

    def __get_cinemas_from_raw_showtimelist(
        self, raw_showtimelist: dict, distance_max_inclusive: int = 0
    ):
        cinemas = []
        for cinema_showtime in jmespath.search(
            "feed.theaterShowtimes", raw_showtimelist
        ):
            raw_cinema = jmespath.search("place.theater", cinema_showtime)

            if raw_cinema.get("distance") is not None:
                # distance is not present when theater ids were used for search
                if raw_cinema.get("distance") > distance_max_inclusive:
                    # Skip cinemas that are above the max distance specified
                    continue

            raw_showtimes = jmespath.search("movieShowtimes", cinema_showtime)
            showtimes = self.__parse_showtimes(raw_showtimes=raw_showtimes)
            raw_cinema_info = self.__client.get_cinema_info_by_id(
                raw_cinema.get("code")
            )
            member_cards = jmespath.search("theater.memberCard", raw_cinema_info)

            cinema = Cinema(
                allocine_id=raw_cinema.get("code"),
                name=raw_cinema.get("name"),
                address=raw_cinema.get("address"),
                zipcode=raw_cinema.get("postalCode"),
                city=raw_cinema.get("city"),
                member_cards=member_cards,
                showtimes=showtimes,
            )
            cinemas.append(cinema)
        return cinemas

    def get_cinema_ids(self, geocode: int):
        codes = []
        page = 1
        while page < 2:  # let's not loop forever
            ret = self.__client.get_showtimelist_from_geocode(
                geocode=geocode, page=page
            )
            page += 1

            total_results = jmespath.search("feed.totalResults", ret)
            if total_results == 0:
                raise ValueError(f"Theater not found. Is geocode {geocode!r} correct?")

            cinemas = jmespath.search("feed.theaterShowtimes", ret)
            if cinemas is None:
                break
            for cinema in cinemas:
                info = jmespath.search("place.theater", cinema)
                code = info.get("code")
                name = info.get("name")
                print(f"{code} - {name}")
                codes.append(code)

        return codes

    def search_cinemas(self, geocode: int):
        cinemas = []
        page = 1
        while page < 3:  # let's not loop forever
            ret = self.__client.get_showtimelist_from_geocode(
                geocode=geocode, page=page
            )

            total_results = jmespath.search("feed.totalResults", ret)
            if total_results == 0:
                raise ValueError(f"Theater not found. Is geocode {geocode!r} correct?")

            cinemas_to_parse = jmespath.search("feed.theaterShowtimes", ret)

            if cinemas_to_parse:
                cinemas += self.__get_cinemas_from_raw_showtimelist(
                    raw_showtimelist=ret, distance_max_inclusive=0
                )
                page += 1
            else:
                break

        return cinemas

    def __parse_showtimes(self, raw_showtimes: dict):
        showtimes = []
        for s in raw_showtimes:
            raw_movie = jmespath.search("onShow.movie", s)
            language = jmespath.search('version."$"', s)
            screen_format = jmespath.search('screenFormat."$"', s)
            duration = raw_movie.get("runtime")
            duration_obj = timedelta(seconds=duration) if duration else None

            rating = jmespath.search("statistics.userRating", raw_movie)
            poster = jmespath.search("poster.href", raw_movie)
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                rating = None

            movie_id = raw_movie.get("code")
            movie_info = self.get_movie_info(movie_id)
            countries = jmespath.search('nationality[]."$"', movie_info)
            year = movie_info.get("productionYear")
            if year:
                year = int(year)
            movie = MovieVersion(
                movie_id=movie_id,
                title=raw_movie.get("title"),
                rating=rating,
                language=language,
                screen_format=screen_format,
                synopsis=clean_synopsis(movie_info.get("synopsis")),
                original_title=movie_info.get("originalTitle"),
                year=year,
                countries=countries,
                genres=", ".join(jmespath.search('genre[]."$"', movie_info)),
                directors=jmespath.search("castingShort.directors", movie_info),
                actors=jmespath.search("castingShort.actors", movie_info),
                duration=duration_obj,
                poster=poster
            )
            for showtimes_of_day in s.get("scr") or []:
                if showtimes_of_day is None:
                    continue
                day = showtimes_of_day.get("d")
                time = showtimes_of_day.get("t")
                if time is None:
                    # Sometimes films have no set time on a given date.
                    continue
                for one_showtime in time:
                    datetime_str = "{}T{}:00".format(day, one_showtime.get("$"))
                    datetime_obj = str_datetime_to_datetime_obj(datetime_str)
                    showtime = Showtime(
                        date_time=datetime_obj,
                        end_time=datetime_obj + duration_obj + timedelta(seconds=900)
                        if duration_obj is not None
                        else None,
                        movie=movie,
                    )
                    showtimes.append(showtime)
        return showtimes

    def get_movie_info(self, movie_id: int):
        movie_info = self.__movie_store.get(movie_id)
        if movie_info is None:
            movie_info = self.__client.get_movie_info_by_id(movie_id).get("movie")
            self.__movie_store[movie_id] = movie_info
        return movie_info


