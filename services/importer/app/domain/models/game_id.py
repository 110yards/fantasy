def create_game_id(year: int, week: int, game_number: int) -> str:
    return f"{year}{week:0>2}{game_number:0>2}"
