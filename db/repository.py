from datetime import date
from sqlalchemy import select, update
from sqlalchemy.dialects.mysql import insert as mysql_insert
from db.connection import SessionLocal
from db.models import GameDetailEntity, GameEntity
from models.game import Game


def upsert_games(games: list[Game]) -> int:
    if not games:
        return 0

    rows = [
        {
            "season": game.season,
            "game_type": game.game_type,
            "game_date": game.game_date,
            "game_time": game.game_time,
            "home_team": game.home_team_code,
            "away_team": game.away_team_code,
            "venue": game.venue,
            "home_score": game.home_score,
            "away_score": game.away_score,
            "status": game.status,
            "game_number": game.game_number,
        }
        for game in games
    ]

    stmt = mysql_insert(GameEntity).values(rows)
    stmt = stmt.on_duplicate_key_update(
        game_time=stmt.inserted.game_time,
        venue=stmt.inserted.venue,
        home_score=stmt.inserted.home_score,
        away_score=stmt.inserted.away_score,
        status=stmt.inserted.status,
        game_number=stmt.inserted.game_number,
    )

    with SessionLocal() as session:
        session.execute(stmt)
        session.commit()

    return len(rows)


def upsert_today_statuses(naver_games: list[dict]) -> None:
    if not naver_games:
        return

    with SessionLocal() as session:
        for g in naver_games:
            session.execute(
                update(GameEntity)
                .where(
                    GameEntity.game_date == g["game_date"],
                    GameEntity.home_team == g["home_team"],
                    GameEntity.away_team == g["away_team"],
                    GameEntity.game_number == g["game_number"],
                )
                .values(
                    status=g["status"],
                    home_score=g["home_score"],
                    away_score=g["away_score"],
                )
            )
        session.commit()


def find_game_id(game_date: date, home_team: str, away_team: str, game_number: int) -> int | None:
    with SessionLocal() as session:
        return session.execute(
            select(GameEntity.id).where(
                GameEntity.game_date == game_date,
                GameEntity.home_team == home_team,
                GameEntity.away_team == away_team,
                GameEntity.game_number == game_number,
            )
        ).scalar_one_or_none()


def upsert_game_detail(game_id: int, detail: dict) -> None:
    stmt = mysql_insert(GameDetailEntity).values(game_id=game_id, **detail)
    stmt = stmt.on_duplicate_key_update(
        away_hits=stmt.inserted.away_hits,
        away_errors=stmt.inserted.away_errors,
        home_hits=stmt.inserted.home_hits,
        home_errors=stmt.inserted.home_errors,
        innings=stmt.inserted.innings,
    )
    with SessionLocal() as session:
        session.execute(stmt)
        session.commit()
