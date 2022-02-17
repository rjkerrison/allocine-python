from dataclasses import dataclass
from datetime import date
from typing import List

from helpers.schedules import Schedule, build_weekly_schedule_str
from .movies import MovieVersion


@dataclass
class Showtime(Schedule):
    movie: MovieVersion

    def __str__(self):
        return f"{self.date_str} : {self.movie}"


def get_showtimes_of_a_day(showtimes: List[Showtime], *, date: date):
    return [showtime for showtime in showtimes if showtime.date == date]


# == Utils ==
def get_available_dates(showtimes: List[Showtime]):
    dates = [s.date for s in showtimes]
    return sorted(list(set(dates)))


def group_showtimes_per_schedule(showtimes: List[Showtime]):
    showtimes_per_date = {}
    available_dates = get_available_dates(showtimes=showtimes)
    for available_date in available_dates:
        showtimes_per_date[available_date] = get_showtimes_of_a_day(
            showtimes=showtimes, date=available_date
        )

    grouped_showtimes = {}
    for available_date in available_dates:
        hours = [s.hour_short_str for s in showtimes_per_date[available_date]]
        hours_str = ", ".join(hours)
        if grouped_showtimes.get(hours_str) is None:
            grouped_showtimes[hours_str] = []
        grouped_showtimes[hours_str].append(available_date)
    return grouped_showtimes


def build_program_str(showtimes: List[Showtime]):
    schedules = [Schedule(s.date_time) for s in showtimes]
    return build_weekly_schedule_str(schedules)
