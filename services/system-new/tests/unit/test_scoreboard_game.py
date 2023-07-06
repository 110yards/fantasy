from datetime import datetime, timedelta, timezone

from app.domain.models.scoreboard import ScoreboardGame


def test_scoreboard_game_is_active_started_5_minutes_ago():
    game = ScoreboardGame.model_construct(**{"game_date": datetime.now(timezone.utc) - timedelta(minutes=5), "end_date": None})

    assert game.is_active(), "Game should be active"


def test_scoreboard_game_is_active_starts_in_5_minutes():
    game = ScoreboardGame.model_construct(**{"game_date": datetime.now(timezone.utc) + timedelta(minutes=5), "end_date": None})

    assert game.is_active(), "Game should be active"


def test_scoreboard_game_is_active_ended_5_minutes_ago():
    game = ScoreboardGame.model_construct(
        **{
            "game_date": datetime.now(timezone.utc) - timedelta(hours=2),
            "end_date": datetime.now(timezone.utc) - timedelta(minutes=5),
        }
    )

    assert game.is_active(), "Game should be active"


def test_scoreboard_game_is_not_active_starts_45_minutes_from_now():
    game = ScoreboardGame.model_construct(**{"game_date": datetime.now(timezone.utc) + timedelta(minutes=45), "end_date": None})

    assert not game.is_active(), "Game should not be active"


def test_scoreboard_game_is_not_active_ended_45_minutes_ago():
    game = ScoreboardGame.model_construct(
        **{
            "game_date": datetime.now(timezone.utc) - timedelta(hours=2),
            "end_date": datetime.now(timezone.utc) - timedelta(minutes=45),
        }
    )

    assert not game.is_active(), "Game should not be active"
