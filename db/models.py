from datetime import date, time
from sqlalchemy import Date, Enum, Integer, SmallInteger, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from db.connection import Base
from models.game import GameStatus, GameType

TEAM_ENUM = Enum(
    "DOOSAN", "LG", "KT", "SSG", "NC", "SAMSUNG", "HANWHA", "LOTTE", "KIA", "KIWOOM",
    name="kbo_team",
)


class GameEntity(Base):
    __tablename__ = "game"
    __table_args__ = (
        UniqueConstraint("season", "game_type", "game_date", "home_team", "away_team", "game_number", name="uq_game"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    game_type: Mapped[GameType] = mapped_column(Enum(GameType), nullable=False)
    game_date: Mapped[date] = mapped_column(Date, nullable=False)
    game_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    home_team: Mapped[str] = mapped_column(TEAM_ENUM, nullable=False)
    away_team: Mapped[str] = mapped_column(TEAM_ENUM, nullable=False)
    venue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus), nullable=False, default=GameStatus.SCHEDULED)
    game_number: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
