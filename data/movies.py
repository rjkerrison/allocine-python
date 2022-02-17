from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional
import logging

from helpers.cleaners import strip_accents
from .nationalities import countries, nationalities

logger = logging.getLogger(__name__)


@dataclass
class Movie:
    movie_id: int
    title: str
    original_title: str
    rating: Optional[float]
    duration: Optional[timedelta]
    genres: str
    countries: List[str]
    directors: str
    actors: str
    synopsis: str
    year: int

    @property
    def duration_str(self):
        if self.duration is not None:
            return _strfdelta(self.duration, "{hours:02d}h{minutes:02d}")
        else:
            return "HH:MM"

    @property
    def duration_short_str(self) -> str:
        if self.duration is not None:
            return _strfdelta(self.duration, "{hours:d}h{minutes:02d}")
        else:
            return "NA"

    @property
    def rating_str(self):
        return "{0:.1f}".format(self.rating) if self.rating else ""

    @property
    def nationalities(self):
        """Return the nationality tuples, from the movie countries.
        Example: if self.countries = ['France'] => [('français', 'française')]
        """
        if self.countries:
            nationality_tuples = []
            for country_name in self.countries:
                normalized_country_name = strip_accents(country_name).lower()
                country_code = countries.get(normalized_country_name)

                if country_code is not None:
                    nationality_tuples.append(nationalities[country_code])
                else:
                    logger.warning(
                        f"Country {country_name!r} not found in nationalities"
                    )
                    nationality_tuples.append(
                        (f"de {country_name}", f"de {country_name}")
                    )
            return nationality_tuples
        else:
            return None

    def __str__(self):
        return f"{self.title} [{self.movie_id}] ({self.duration_str})"

    def __eq__(self, other):
        return (self.movie_id) == (other.movie_id)

    def __hash__(self):
        """This function allows us
        to do a set(list_of_Movie_objects)"""
        return hash(self.movie_id)


def _strfdelta(tdelta, fmt):
    """Format a timedelta object"""
    # Thanks to https://stackoverflow.com/questions/8906926
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


@dataclass
class MovieVersion(Movie):
    language: str
    screen_format: str

    @property
    def version(self):
        version = "VF" if self.language == "Français" else "VOST"
        if self.screen_format != "Numérique":
            version += f" {self.screen_format}"
        return version

    def get_movie(self):
        return Movie(
            movie_id=self.movie_id,
            title=self.title,
            rating=self.rating,
            duration=self.duration,
            original_title=self.original_title,
            year=self.year,
            genres=self.genres,
            countries=self.countries,
            directors=self.directors,
            actors=self.actors,
            synopsis=self.synopsis,
        )

    def __str__(self):
        movie_str = super().__str__()
        return f"{movie_str} ({self.version})"

    def __eq__(self, other):
        return (self.movie_id, self.version) == (other.movie_id, other.version)

    def __hash__(self):
        """This function allows us
        to do a set(list_of_MovieVersion_objects)"""
        return hash((self.movie_id, self.version))
