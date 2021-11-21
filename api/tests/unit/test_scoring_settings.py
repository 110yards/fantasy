from api.app.domain.entities.stats import Stats
from api.app.domain.entities.scoring_settings import ScoringSettings


def test_score_calculation():

    stats = Stats.construct()
    stats = stats.dict()

    for key in stats:
        stats[key] = 1

    stats = Stats.parse_obj(stats)

    settings = ScoringSettings.create_default()
    score = settings.calculate_score(stats)

    settings = settings.dict()
    score = score.dict()

    for key in score:
        if key == "total_score" or key == "id":
            continue
        stat_score = score[key]
        setting = settings[key]

        # All of the scores should match the setting since all of the stat totals are 1
        assert stat_score == setting, f"{key} does not match"
