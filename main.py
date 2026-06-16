import os
from datetime import datetime
from dotenv import load_dotenv
from db.connection import Base, engine
from db.repository import upsert_teams, upsert_games
from crawler.kbo import fetch_schedule_html
from crawler.parser import parse_schedule, KNOWN_TEAMS

load_dotenv()

SEASON = int(os.getenv("KBO_SEASON", str(datetime.now().year)))


def init_db() -> None:
    Base.metadata.create_all(engine)


def crawl_month(year: int, month: int) -> None:
    print(f"[{year}-{month:02d}] 크롤링 시작")
    html = fetch_schedule_html(year, month)
    games = parse_schedule(html, SEASON, year, month)
    saved = upsert_games(games)
    print(f"[{year}-{month:02d}] {saved}경기 저장 완료")


def run() -> None:
    init_db()
    upsert_teams(KNOWN_TEAMS)

    now = datetime.now()
    crawl_month(now.year, now.month)


if __name__ == "__main__":
    run()
