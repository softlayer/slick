from datetime import datetime


def parse_date(date):
    return datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S")
