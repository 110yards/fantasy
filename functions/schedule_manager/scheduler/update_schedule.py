
from .store import get_path
from .store import set_path
from .schedule import Schedule
from .create_schedule import create_schedule
from .get_games import get_all_games


def update_schedule(key: str, year: int, post_week_buffer_hours: int):
    games = get_all_games(key, year)
    print(f"Fetched {year} data")

    previous_hash = read_schedule_hash(year)

    schedule = create_schedule(year, games, post_week_buffer_hours)

    if schedule.hash == previous_hash:
        print("No changes to schedule detected")
        return

    print("Schedule has changed, attempting to save...")

    save_schedule(year, schedule)

    print(f"{year} schedule has been updated")
    return schedule


def get_schedule_path(year: int) -> str:
    return f"schedule/{year}"


def read_schedule_hash(year: int) -> str:
    schedule_path = get_schedule_path(year)
    hash_path = f"{schedule_path}/hash"
    return get_path(hash_path)


def save_schedule(year: int, schedule: Schedule):
    path = get_schedule_path(year)
    set_path(path, schedule.serialize())
