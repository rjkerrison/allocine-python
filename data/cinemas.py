from dataclasses import dataclass
from datetime import date
from typing import List

from .memberships import MemberCard
from .movies import MovieVersion
from .showtimes import Showtime, build_program_str, get_showtimes_of_a_day


@dataclass
class Cinema:
    allocine_id: str
    name: str
    showtimes: List[Showtime]
    address: str
    zipcode: str
    city: str
    member_cards: List[MemberCard]

    def toJSON(self):
        return {
            'allocine_id': self.allocine_id,
            'name': self.name,
            'address': self.address,
            'zipcode': self.zipcode,
            'city': self.city,
            'member_cards': self.member_cards
        }

    @property
    def address_str(self):
        address_str = f"{self.address}, " if self.address else ""
        address_str += f"{self.zipcode} {self.city}"
        return address_str

    def get_showtimes_of_a_movie(self, movie_version: MovieVersion, date: date = None):
        movie_showtimes = [
            showtime for showtime in self.showtimes if showtime.movie == movie_version
        ]
        if date:
            return [showtime for showtime in movie_showtimes if showtime.date == date]
        else:
            return movie_showtimes

    def get_showtimes_of_a_day(self, date: date):
        return get_showtimes_of_a_day(showtimes=self.showtimes, date=date)

    def get_movies_available_for_a_day(self, date: date):
        """Returns a list of movies available on a specified day"""
        movies = [showtime.movie for showtime in self.get_showtimes_of_a_day(date)]
        return list(set(movies))

    def get_showtimes_per_movie_version(self):
        movies = {}
        for showtime in self.showtimes:
            if movies.get(showtime.movie) is None:
                movies[showtime.movie] = []
            movies[showtime.movie].append(showtime)
        return movies

    def get_showtimes_per_movie(self):
        movies = {}
        for showtime in self.showtimes:
            movie = showtime.movie.get_movie()  # Without language nor screen_format
            if movies.get(movie) is None:
                movies[movie] = []
            movies[movie].append(showtime)
        return movies

    def get_program_per_movie(self):
        program_per_movie = {}
        for movie, showtimes in self.get_showtimes_per_movie().items():
            program_per_movie[movie] = build_program_str(showtimes=showtimes)
        return program_per_movie

    def filter_showtimes(self, date_min: date = None, date_max: date = None):
        if date_min:
            self.showtimes = [s for s in self.showtimes if s.date >= date_min]
        if date_max:
            self.showtimes = [s for s in self.showtimes if s.date <= date_max]

    def __eq__(self, other):
        return (self.allocine_id) == (other.allocine_id)

    def __hash__(self):
        """This function allows us to do a set(list_of_Theaters_objects)"""
        return hash(self.allocine_id)
