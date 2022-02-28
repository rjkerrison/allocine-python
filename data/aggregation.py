
from dataclasses import dataclass
from urllib.parse import quote

from data.cinemas import Cinema
from data.showtimes import Showtime

GCAL_BASE_URL = 'https://www.google.com/calendar/render?action=TEMPLATE'

def build_querystring(**kwargs):
    return '&'.join(f'{key}={quote(kwargs[key])}' for key in kwargs)

@dataclass
class ShowtimeWithCinema:
    cinema: Cinema
    showtime: Showtime

    def toJSON(self):
        return {
            'start_time': self.showtime.date_str,
            'end_time': self.showtime.end_date_str,
            'link': self.gcal_link()
        }

    def gcal_link(self):
        qs = build_querystring(
            text = f"Cinema: {self.showtime.movie.title}",
            dates = self.showtime.start_end_utc_string,
            details = self.showtime.movie.synopsis,
            location = self.cinema.address_str,
        )
        return f'{GCAL_BASE_URL}&{qs}'