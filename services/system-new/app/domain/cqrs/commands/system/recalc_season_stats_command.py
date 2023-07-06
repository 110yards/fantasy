from dataclasses import dataclass


@dataclass
class RecalcSeasonStatsCommand:
    completed_week_number: int
