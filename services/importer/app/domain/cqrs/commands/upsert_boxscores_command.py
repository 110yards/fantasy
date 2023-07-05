from dataclasses import dataclass

from ...models.boxscore import Boxscore


@dataclass
class UpsertBoxscoresCommand:
    boxscores: list[Boxscore]
