import datetime
from dateutil.relativedelta import relativedelta

from core.settings import DEFAULT_DATE_FORMAT


def now():
    return datetime.datetime.now()


def parse_datetime(value: str):
    try:
        return datetime.datetime.strptime(value, DEFAULT_DATE_FORMAT)
    except:
        return None
