from datetime import date, time
from sqlalchemy import Date, Enum, ForeignKey, Integer, SmallInteger, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.connection import Base
from models.game import GameStatus


class TeamEntity(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    short_name: Mapped[str] = mapped_column(String(20), nullable=False)

    home_games: Mapped[list["GameEntity"]] = relationship(
        back_populates="home_team", foreign_keys="GameEntity.home_team_id"
    )
    away_games: Mapped[list["GameEntity"]] = relationship(
        back_populates="away_team", foreign_keys="GameEntity.away_team_id"
    )


class GameEntity(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    game_date: Mapped[date] = mapped_column(Date, nullable=False)
    game_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus), nullable=False, default=GameStatus.SCHEDULED
    )

    home_team: Mapped["TeamEntity"] = relationship(
        back_populates="home_games", foreign_keys=[home_team_id]
    )
    away_team: Mapped["TeamEntity"] = relationship(
        back_populates="away_games", foreign_keys=[away_team_id]
    )
