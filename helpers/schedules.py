from dataclasses import dataclass
from datetime import datetime, timedelta, date, time
from collections import OrderedDict
from typing import List, Optional

from helpers.timing import (
    day_str,
    get_hour_short_str,
    short_day_str,
    to_french_short_weekday,
)

@dataclass
class Schedule:
    date_time: datetime
    end_time: datetime

    def __init__(self, date_time: datetime, end_time: Optional[datetime] = None):
        self.date_time = date_time
        self.end_time = end_time if end_time is not None else date_time + timedelta(minutes=15)

    @property
    def date(self) -> date:
        return self.date_time.date()

    @property
    def hour(self) -> datetime.time:
        return self.date_time.time()

    @property
    def hour_str(self) -> str:
        return self.date_time.strftime("%H:%M")

    @property
    def end_hour_str(self) -> str:
        return self.end_time.strftime("%H:%M")

    @property
    def hour_short_str(self) -> str:
        return get_hour_short_str(self.hour)

    @property
    def date_str(self) -> date:
        return self.date_time.strftime("%d/%m/%Y %H:%M")

    @property
    def end_date_str(self) -> date:
        return self.end_time.strftime("%d/%m/%Y %H:%M")

    @property
    def day_str(self) -> str:
        return day_str(self.date)

    @property
    def short_day_str(self) -> str:
        return short_day_str(self.date)

    @property
    def start_as_utc_string(self) -> str:
        return self.date_time.strftime("%Y%m%dT%H%M%S")

    @property
    def end_as_utc_string(self) -> str:
        return self.end_time.strftime("%Y%m%dT%H%M%S")

    @property
    def start_end_utc_string(self) -> str:
        return f"{self.start_as_utc_string}/{self.end_as_utc_string}"

def build_weekly_schedule_str(schedule_list: List[Schedule]) -> str:
    check_schedules_within_week(schedule_list)

    _hours_hashmap = {}  # ex: {16h: [Lun, Mar], 17h: [Lun], 17h30: [Lun]}
    _grouped_date_hashmap = {}  # ex: {[Lun]: [16h, 17h30], [Lun, Mar]: [17h]}

    for s in schedule_list:

        if _hours_hashmap.get(s.hour) is None:
            _hours_hashmap[s.hour] = []
        _hours_hashmap[s.hour].append(s.date)

    for hour, grouped_dates in _hours_hashmap.items():
        grouped_dates_str = create_weekdays_str(grouped_dates)
        if _grouped_date_hashmap.get(grouped_dates_str) is None:
            _grouped_date_hashmap[grouped_dates_str] = []
        _grouped_date_hashmap[grouped_dates_str].append(hour)

    # Then sort it chronologically
    for grouped_dates_str, hours in _grouped_date_hashmap.items():
        # Sort the hours inside
        hours = list(set(hours))
        hours.sort()
        _grouped_date_hashmap[grouped_dates_str] = hours

    grouped_date_hashmap = OrderedDict()
    _grouped_date_hashmap = sorted(
        _grouped_date_hashmap.items(), key=__get_time_weight_in_list
    )
    grouped_date_hashmap = OrderedDict(_grouped_date_hashmap)

    hours_hashmap = OrderedDict()
    for t in sorted(_hours_hashmap.keys(), key=__get_time_weight):
        hours_hashmap[t] = _hours_hashmap.get(t)

    different_showtimes = len(grouped_date_hashmap)

    # True if at least one schedule is available everyday
    some_schedules_available_everyday = grouped_date_hashmap.get("") is not None

    weekly_schedule = ""

    if some_schedules_available_everyday:
        for hour, grouped_dates in hours_hashmap.items():
            hour_str = get_hour_short_str(hour)
            grouped_dates_str = create_weekdays_str(grouped_dates)
            if grouped_dates_str:
                weekly_schedule += f"{hour_str} ({grouped_dates_str}), "
            else:  # Available everyday
                weekly_schedule += f"{hour_str}, "
    else:
        for grouped_dates, hours in grouped_date_hashmap.items():
            hours_str = ", ".join([get_hour_short_str(h) for h in hours])
            if different_showtimes == 1:
                weekly_schedule += f"{grouped_dates} {hours_str}, "
            else:
                if some_schedules_available_everyday:
                    weekly_schedule += f"{hours_str} ({grouped_dates}), "
                else:
                    weekly_schedule += f"{grouped_dates} {hours_str}; "

    if weekly_schedule:
        weekly_schedule = weekly_schedule[:-2]  # Remove trailing comma
    return weekly_schedule


def __get_time_weight_in_list(d: dict) -> timedelta:
    """Returns the minimum time weight from the time list contained in the dict values
    ex: {'key': [time(hour=12), time(hour=9)]} => timedelta(hour=9)
    """
    weights = [__get_time_weight(t) for t in d[1]]
    return min(weights)


def create_weekdays_str(dates: List[date]) -> str:
    """
    Returns a compact string from a list of dates.
    Examples:
        - [0,1] -> 'Lun, Mar'
        - [0,1,2,3,4] -> 'sf Sam, Dim'
        - [0,1,2,3,4,5,6] -> ''  # Everyday is empty string
        - [0,2] -> 'Mer, Lun'  # And not 'Lun, Mer' because we sort chrologically
    """
    FULL_WEEK = range(0, 7)
    unique_dates = sorted(list(set(dates)))
    week_days = [d.weekday() for d in unique_dates]

    if len(unique_dates) == 7:
        return ""
    elif len(unique_dates) <= 4:
        return ", ".join([to_french_short_weekday(d) for d in week_days])
    else:
        missing_days = list(set(week_days).symmetric_difference(FULL_WEEK))
        return "sf {}".format(
            ", ".join([to_french_short_weekday(d) for d in missing_days])
        )


def __get_time_weight(t: time) -> timedelta:
    """Return a timedelta taking into account night time.
    Basically, it allows to sort a list of times 18h>23h>0h30
    and not 0h30>18h>23h
    """
    _NIGHT_TIME = [time(hour=0), time(hour=5)]
    delta = timedelta(hours=t.hour, minutes=t.minute)
    if t >= min(_NIGHT_TIME) and t <= max(_NIGHT_TIME):
        delta += timedelta(days=1)
    return delta


def check_schedules_within_week(schedule_list: List[Schedule]) -> bool:
    schedule_dates = [s.date for s in schedule_list]
    min_date = min(schedule_dates)
    max_date = max(schedule_dates)
    delta = max_date - min_date
    if delta >= timedelta(days=7):
        raise ValueError("Schedule list contains more days than the typical movie week")
    # Check that the week is not from Mon/Tue to Wed/Thu/Fri/Sat/Sun
    # because a typical week is from Wed to Tue
    # but we need to handle the case of a schedule_list with only a few day
    # ex: Wed, Mon = OK ; Tue = OK ; Mon, Wed : NOK
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    if delta > timedelta(days=0):
        if (min_date.weekday() == MONDAY and max_date.weekday() >= WEDNESDAY) or (
            min_date.weekday() == TUESDAY
        ):
            raise ValueError(
                "Schedule list should not start before wednesday or end after tuesday"
            )

    return True
