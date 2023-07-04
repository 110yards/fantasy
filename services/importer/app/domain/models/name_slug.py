from .player import Player


def name_slug_for_player(player: Player) -> str:
    return name_slug(player.team_abbr, player.full_name)


def name_slug(team_abbr: str, full_name: str) -> str:
    name = full_name.lower()
    # remove suffixes
    name = name.replace("jr", "")
    name = name.replace("sr", "")
    name = name.replace("iii", "")
    name = name.replace("ii", "")
    name = name.replace("iv", "")
    name = name.replace(" ", "")

    # remove non-alpha characters
    name = "".join([c for c in name if c.isalpha()])

    return f"{team_abbr}-{name}"
