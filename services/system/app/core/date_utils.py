from datetime import datetime


def hours_since(start: datetime, end: datetime) -> float:
    diff = (end - start)
    hours = (diff.days * 24) + (diff.seconds / 3600)

    return hours
