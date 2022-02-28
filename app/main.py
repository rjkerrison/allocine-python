from dataclasses import dataclass
import json
from typing import List
from allocine import Allocine
from prettytable import PrettyTable, UNICODE, FRAME, ALL
from datetime import date, timedelta, datetime

from data.aggregation import ShowtimeWithCinema
from data.cinemas import Cinema
from data.movies import MovieVersion

def extract_field_names(dict_list):
    """Returns a sorted list of field names from a dictionary list
    > extract_field_names([{'a': 1, 'b': 2}, {'a': 3, 'c': 4}])
    ['a', 'b', 'c']
    """
    field_names = []
    for row_dict in dict_list:
        field_names += row_dict.keys()
    field_names = list(set(field_names))  # Removes duplicates
    return sorted(field_names)  # sort it in ascending order

@dataclass
class FilmShowtimesGroup:
    film: MovieVersion
    showtimes: List[ShowtimeWithCinema]

@dataclass
class DayFilmShowtimes:
    day: str
    showings: List[FilmShowtimesGroup]

def dumper(obj):
    try:
        return obj.toJSON()
    except Exception as f:
        print('Exception for toJSON', f, type(obj))
        return obj.__dict__

def display_cinema_json(cinema, showings: List[DayFilmShowtimes]):
    log = json.dumps({
        'cinema': cinema,
        'showings': showings
    }, default=dumper, indent=2)
    return log

def get_all_days_seance_data(cinema: Cinema, days: List[str], is_showtime_eligible) -> List[DayFilmShowtimes]:
    return [DayFilmShowtimes(
        day=datetime.strptime(day, "%d/%m/%Y").strftime("%Y-%m-%d"),
        showings=get_seance_data(
            cinema=cinema,
            jour=day,
            is_showtime_eligible=is_showtime_eligible
        )
    ) for day in days]

def parse_hour_as_datetime(jour, time):
    if time is None:
        return None
    date_str = f'{jour.strftime("%d/%m/%Y")} {time}'
    return datetime.strptime(date_str, "%d/%m/%Y %H:%M")

def check_cinema_late_eligibility_rules(cinema, card):
    return check_card_eligibility(cinema, card)

def check_card_eligibility(cinema, card):
    if card is not None and cinema.member_cards is not None:
        if card == "UGC":
            if 106002 not in (x["code"] for x in cinema.member_cards):
                log_v(
                    f"SKIPPING {cinema.name} because it does not accept UGC Illimité.\n"
                )
                return False
    return True


def check_showtime_eligibility(showtime, jour, earliest_time, latest_time):
    start = parse_hour_as_datetime(jour, earliest_time)
    end = parse_hour_as_datetime(jour, latest_time)

    return (start is None or showtime.date_time > start) and (
        end is None or showtime.end_time is None or showtime.end_time < end
    )

def display_cinema(cinema, seance_data_all_days: List[DayFilmShowtimes], entrelignes):
    tables = []
    result = ""

    for seance_data in seance_data_all_days:
        seances = display_seances(seance_data.showings)

        if len(seances) > 0:
            tables += [seance_data.day, get_showtime_table(seances, entrelignes)]

    if len(tables) > 0:
        result += (f"{cinema.name} - {cinema.id}") + "\n"
        log_v(f"https://allocine.fr/seance/salle_gen_csalle={cinema.id}.html")
        result += (f"{cinema.address}, {cinema.zipcode}, {cinema.city}") + "\n"
        log_v("\n".join((f'✔️  {x.get("label")}' for x in cinema.member_cards)))
        for table in tables:
            result += (table) + "\n"

        return result

    else:
        print(f"{cinema.name} - {cinema.id} has no eligible showings.")


def get_seance_data(cinema, jour, is_showtime_eligible) -> List[FilmShowtimesGroup]:
    date_obj = datetime.strptime(jour, "%d/%m/%Y").date()
    available_films = get_available_films(cinema, date_obj)

    return [
        FilmShowtimesGroup(
            film=film,
            showtimes=list(get_eligible_showtimes(cinema, film, date_obj, is_showtime_eligible))
        ) for film in available_films
    ]

def get_available_films(cinema, date_obj):
    return cinema.get_movies_available_for_a_day(date=date_obj)

def get_eligible_showtimes(cinema, film, date_obj, is_showtime_eligible) -> List[ShowtimeWithCinema]:
    showtimes = cinema.get_showtimes_of_a_movie(
            movie_version=film, date=date_obj
        )
    for showtime in showtimes:
        if is_showtime_eligible(showtime, date_obj):
            yield ShowtimeWithCinema(cinema=cinema, showtime=showtime)

def display_seances(film_showtimes_groups: List[FilmShowtimesGroup]) -> List[dict[str, str]]:
    seances = []

    for film_showtimes_group in film_showtimes_groups:
        movie = film_showtimes_group.film
        title = movie.title
        if len(title) >= 31:  # On tronque les titres trop longs
            title = title[:31] + "..."

        # '*1_film' pour être sûr que cela soit la 1ère colonne
        movie_row = {
            "*1_film": "{} ({}) - {}".format(
                title, movie.version, movie.duration_str
            )
        }

        movie_row["*2_note"] = "{}*".format(movie.rating_str)

        for showtime in film_showtimes_group.showtimes:
            hour = showtime.showtime.hour_str.split(":")[0]  # 11:15 => 11
            movie_row[hour] = f"{showtime.showtime.hour_str}"

        if len(movie_row) > 2:
            seances.append(movie_row)
        else:
            log_v(f"Skipping {title} due to no eligible showings. ")

    return seances


def get_showtime_table(seances, entrelignes):
    table = PrettyTable()
    table.set_style(UNICODE)
    table.header = False

    if entrelignes is True:
        table.hrules = ALL
    else:
        table.hrules = FRAME

    table.field_names = extract_field_names(seances)

    for seances_film in seances:
        row = []
        for field_name in table.field_names:
            row.append(seances_film.get(field_name, ""))
        table.add_row(row)

    table.align["*1_film"] = "l"
    table.sortby = "*1_film"
    return str(table)


log_level = "SHH"


def log_v(message):
    if log_level == "VERBOSE":
        print(message)


def get_showings(
    id_cinema,
    entrelignes=False,
    jour=None,
    semaine=None,
    card=None,
    earliest_time=None,
    latest_time=None,
    link=False,
    format=None
):
    """
    Les séances de votre cinéma dans le terminal, avec
    ID_CINEMA : identifiant du cinéma sur Allociné,
    ex: C0159 pour l’UGC Ciné Cité Les Halles. Se trouve dans l’url :
    https://allocine.fr/seance/salle_gen_csalle=<ID_CINEMA>.html
    """
    today = date.today()
    allocine = Allocine()

    jours = []
    if semaine is False:
        if jour is None:
            jours.append(today.strftime("%d/%m/%Y"))
        elif jour[0] == "+":
            delta_jours = int(jour[1:])
            jour_obj = today + timedelta(days=delta_jours)
            jours.append(jour_obj.strftime("%d/%m/%Y"))
        else:
            jours.append(jour)
    else:
        for delta in range(0, 7):
            jour_obj = today + timedelta(days=delta)
            jours.append(jour_obj.strftime("%d/%m/%Y"))

    if id_cinema is None:
        codes = allocine.get_cinema_ids(83165)
    else:
        codes = id_cinema.split(",")

    is_showtime_eligible = lambda showtime, jour: check_showtime_eligibility(
        showtime, jour, earliest_time, latest_time
    )

    for code in codes:
        cinema = allocine.get_cinema(cinema_id=code)
        if check_cinema_late_eligibility_rules(cinema, card):
            all_days_seance_data = get_all_days_seance_data(cinema, jours, is_showtime_eligible)

            if format == "json":
                yield display_cinema_json(cinema, all_days_seance_data)
            else:
                yield display_cinema(cinema, all_days_seance_data, entrelignes)

