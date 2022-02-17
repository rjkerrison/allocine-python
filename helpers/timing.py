from datetime import datetime, timedelta, date, time


def to_french_weekday(weekday: int) -> str:
    DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    return DAYS[weekday]


def get_french_month(month_number: int) -> str:
    MONTHS = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]
    return MONTHS[month_number - 1]


def to_french_short_weekday(weekday: int) -> str:
    return to_french_weekday(weekday)[:3]


def get_hour_short_str(hour: datetime.time) -> str:
    # Ex: 9h, 11h, 23h30
    # Minus in '%-H' removes the leading 0
    return hour.strftime("%-Hh%M").replace("h00", "h")


def day_str(date: date) -> str:
    return to_french_weekday(date.weekday())


def short_day_str(date: date) -> str:
    return day_str(date)[:3]
