#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CLI tool for allocine"""
import click
from allocine import Allocine
from prettytable import PrettyTable, UNICODE, FRAME, ALL
from datetime import date, timedelta, datetime

# Usage : seances.py --help


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


@click.command()
@click.argument("id_cinema", type=str, required=False)
@click.option(
    "--jour",
    "-j",
    type=str,
    help="jour des séances souhaitées \
(au format DD/MM/YYYY ou +1 pour demain), par défaut : aujourd’hui",
)
@click.option(
    "--semaine",
    "-s",
    is_flag=True,
    help="affiche les séance pour les 7 prochains jours",
)
@click.option(
    "--entrelignes",
    "-e",
    is_flag=True,
    help="ajoute une ligne entre chaque film pour améliorer la lisibilité",
)
@click.option(
    "--card",
    "-c",
    type=str,
    help="check for a specific card pass, e.g. UGC Illimité",
)
@click.option(
    "--earliest-time",
    "-f",
    type=str,
    help="filter to only shows starting after a given time",
)
@click.option(
    "--latest-time",
    "-t",
    type=str,
    help="filter to only shows ending before a given time",
)
def main(
    id_cinema,
    entrelignes,
    jour=None,
    semaine=None,
    card=None,
    earliest_time=None,
    latest_time=None,
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
            display_cinema(cinema, jours, entrelignes, is_showtime_eligible)


def parse_hour_as_datetime(jour, time):
    if time is None:
        return None
    date_str = f'{jour.strftime("%d/%m/%Y")} {time}'
    return datetime.strptime(date_str, "%d/%m/%Y %H:%M")


def check_cinema_late_eligibility_rules(cinema, card):
    return check_card_eligibility(cinema, card)


def check_card_eligibility(cinema, card):
    if card is not None:
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


def display_cinema(cinema, jours, entrelignes, is_showtime_eligible):
    tables = []

    for jour in jours:
        seances = get_seances(
            cinema=cinema, jour=jour, is_showtime_eligible=is_showtime_eligible
        )

        if len(seances) > 0:
            tables += [jour, get_showtime_table(seances, entrelignes)]

    if len(tables) > 0:
        print(f"{cinema.name} - {cinema.id}")
        log_v(f"https://allocine.fr/seance/salle_gen_csalle={cinema.id}.html")
        print(f"{cinema.address}, {cinema.zipcode}, {cinema.city}")
        log_v("\n".join((f'✔️  {x.get("label")}' for x in cinema.member_cards)))
        for table in tables:
            print(table)

    else:
        log_v(f"{cinema.name} - {cinema.id} has no eligible showings.")


def get_seances(cinema, jour, is_showtime_eligible):
    seances = []

    date_obj = datetime.strptime(jour, "%d/%m/%Y").date()
    movies_available_today = cinema.get_movies_available_for_a_day(date=date_obj)

    for movie_version in movies_available_today:

        title = movie_version.title
        if len(title) >= 31:  # On tronque les titres trop longs
            title = title[:31] + "..."

        # '*1_film' pour être sûr que cela soit la 1ère colonne
        movie_row = {
            "*1_film": "{} ({}) - {}".format(
                title, movie_version.version, movie_version.duration_str
            )
        }

        movie_row["*2_note"] = "{}*".format(movie_version.rating_str)

        showtimes = cinema.get_showtimes_of_a_movie(
            movie_version=movie_version, date=date_obj
        )

        for showtime in showtimes:
            if is_showtime_eligible(showtime, date_obj):
                hour = showtime.hour_str.split(":")[0]  # 11:15 => 11
                movie_row[hour] = f"{showtime.hour_str} - {showtime.end_hour_str}"

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


if __name__ == "__main__":
    main()
