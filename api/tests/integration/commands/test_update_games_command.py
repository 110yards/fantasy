

from api.app.domain.commands.system.update_games import (get_changed_games,
                                                         get_changed_players)
from api.app.domain.entities.game import Game
from api.app.domain.entities.game_player_stats import GamePlayerStats


def test_get_changed_games_not_in_db():
    current_games = {
        "1": Game.construct(id="1")
    }
    existing_games = {}

    changed_games = get_changed_games(current_games, existing_games)

    assert "1" in changed_games


def test_get_changed_games_in_db_new_hash():
    current_game1 = Game.construct(id="1")
    current_game1.hash = "12345"

    current_games = {
        "1": current_game1
    }

    existing_game1 = Game.construct()
    existing_game1.hash = "1234"
    existing_games = {
        "1": existing_game1
    }

    changed_games = get_changed_games(current_games, existing_games)

    assert "1" in changed_games


def test_get_changed_games_no_changes():
    current_game1 = Game.construct(id="1")
    current_game1.hash = "12345"

    current_games = {
        "1": current_game1
    }

    existing_game1 = Game.construct()
    existing_game1.hash = "12345"
    existing_games = {
        "1": existing_game1
    }

    changed_games = get_changed_games(current_games, existing_games)

    assert len(changed_games) == 0


def test_get_changed_players_new_player():
    current_game1 = Game.construct()
    player1 = GamePlayerStats.construct()
    player1.hash = "1234"
    current_game1.player_stats = {
        "1": player1
    }
    current_games = {
        "1": current_game1
    }

    existing_game1 = Game.construct()
    existing_game1.player_stats = {}
    existing_games = {
        "1": existing_game1
    }

    changed_players = get_changed_players(current_games, existing_games)

    assert player1 in changed_players


def test_get_changed_players_new_hash():
    current_game1 = Game.construct()
    player1 = GamePlayerStats.construct()
    player1.hash = "1234"
    current_game1.player_stats = {
        "1": player1
    }
    current_games = {
        "1": current_game1
    }

    existing_game1 = Game.construct()
    existing_player1 = GamePlayerStats.construct()
    existing_player1.hash = "5678"
    existing_game1.player_stats = {
        "1": existing_player1
    }
    existing_games = {
        "1": existing_game1
    }

    changed_players = get_changed_players(current_games, existing_games)

    assert player1 in changed_players


def test_get_changed_players_no_change():
    current_game1 = Game.construct()
    player1 = GamePlayerStats.construct()
    player1.hash = "1234"
    current_game1.player_stats = {
        "1": player1
    }
    current_games = {
        "1": current_game1
    }

    existing_game1 = Game.construct()
    existing_player1 = GamePlayerStats.construct()
    existing_player1.hash = "1234"
    existing_game1.player_stats = {
        "1": existing_player1
    }
    existing_games = {
        "1": existing_game1
    }

    changed_players = get_changed_players(current_games, existing_games)

    assert player1 not in changed_players
