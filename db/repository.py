from sqlalchemy.dialects.mysql import insert as mysql_insert
from db.connection import SessionLocal
from db.models import GameEntity
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
