from db.connection import SessionLocal
from db.models import TeamEntity, GameEntity
from models.team import Team
from models.game import Game


def upsert_teams(teams: list[Team]) -> None:
    with SessionLocal() as session:
        for team in teams:
            existing = session.query(TeamEntity).filter_by(code=team.code).first()
            if existing:
                existing.name = team.name
                existing.short_name = team.short_name
            else:
                session.add(TeamEntity(code=team.code, name=team.name, short_name=team.short_name))
        session.commit()


def upsert_games(games: list[Game]) -> int:
    with SessionLocal() as session:
        team_map: dict[str, int] = {
            t.code: t.id for t in session.query(TeamEntity).all()
        }

        saved = 0
        for game in games:
            home_id = team_map.get(game.home_team_code)
            away_id = team_map.get(game.away_team_code)
            if not home_id or not away_id:
                continue

            existing = session.query(GameEntity).filter_by(
                season=game.season,
                game_date=game.game_date,
                home_team_id=home_id,
                away_team_id=away_id,
            ).first()

            if existing:
                existing.game_time = game.game_time
                existing.venue = game.venue
                existing.home_score = game.home_score
                existing.away_score = game.away_score
                existing.status = game.status
            else:
                session.add(GameEntity(
                    season=game.season,
                    game_date=game.game_date,
                    game_time=game.game_time,
                    home_team_id=home_id,
                    away_team_id=away_id,
                    venue=game.venue,
                    home_score=game.home_score,
                    away_score=game.away_score,
                    status=game.status,
                ))
            saved += 1

        session.commit()
        return saved
