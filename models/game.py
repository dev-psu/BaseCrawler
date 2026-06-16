from dataclasses import dataclass
from datetime import date, time
from enum import Enum


class GameType(str, Enum):
    EXHIBITION = "EXHIBITION"
    REGULAR = "REGULAR"
    POSTSEASON = "POSTSEASON"


class GameStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    POSTPONED = "POSTPONED"


@dataclass
class Game:
    season: int
    game_type: GameType
    game_date: date
    home_team_code: str
    away_team_code: str
    status: GameStatus
    game_time: time | None = None
    venue: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    game_number: int = 1
