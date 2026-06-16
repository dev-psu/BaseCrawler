import os
import random
import time
from datetime import datetime
from dotenv import load_dotenv
from db.connection import Base, engine
from db.repository import upsert_games
from crawler.kbo import fetch_schedule_html
from crawler.parser import parse_schedule
from models.game import GameType

load_dotenv()

SEASON = int(os.getenv("KBO_SEASON", str(datetime.now().year)))

# 각 경기 종류별로 데이터가 존재할 수 있는 월 범위 (초과 월은 파싱 결과 0건으로 자동 스킵)
_MONTH_RANGES: dict[GameType, range] = {
    GameType.EXHIBITION: range(1, 5),    # 1~4월
    GameType.REGULAR:    range(3, 12),   # 3~11월
    GameType.POSTSEASON: range(9, 13),   # 9~12월
}


def init_db() -> None:
    Base.metadata.create_all(engine)


def crawl_month(year: int, month: int, game_type: GameType) -> int:
    html = fetch_schedule_html(year, month, game_type)
    games = parse_schedule(html, season=year, year=year, month=month, game_type=game_type)
    if not games:
        return 0
    return upsert_games(games)


def crawl_season(year: int, game_type: GameType) -> None:
    print(f"[{year}][{game_type.value}] 시즌 전체 크롤링 시작")
    total = 0
    for month in _MONTH_RANGES[game_type]:
        time.sleep(random.uniform(0.1, 0.5))
        saved = crawl_month(year, month, game_type)
        if saved:
            print(f"  [{month:02d}월] {saved}경기 저장")
        total += saved
    print(f"[{year}][{game_type.value}] 완료 — 총 {total}경기")


def crawl_all(year: int) -> None:
    for game_type in GameType:
        crawl_season(year, game_type)


def run() -> None:
    """스케줄러용: 현재 월 정규시즌 수집"""
    init_db()
    now = datetime.now()
    saved = crawl_month(now.year, now.month, GameType.REGULAR)
    print(f"[{now.year}-{now.month:02d}][REGULAR] {saved}경기 저장 완료")


def run_full(year: int = SEASON) -> None:
    """전체 수집: 시범/정규/포스트시즌 모든 월"""
    init_db()
    crawl_all(year)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KBO 일정 크롤러")
    parser.add_argument("--full", action="store_true", help="전체 시즌 수집 (시범+정규+포스트)")
    parser.add_argument("--year", type=int, default=SEASON, help="수집 연도 (기본: 현재 연도)")
    parser.add_argument("--type", choices=["EXHIBITION", "REGULAR", "POSTSEASON"], help="특정 경기 종류만 수집")
    parser.add_argument("--month", type=int, help="특정 월만 수집 (--type 필수)")
    args = parser.parse_args()

    init_db()

    if args.month:
        if not args.type:
            parser.error("--month 사용 시 --type 필수")
        game_type = GameType[args.type]
        saved = crawl_month(args.year, args.month, game_type)
        print(f"[{args.year}-{args.month:02d}][{args.type}] {saved}경기 저장 완료")
    elif args.type:
        crawl_season(args.year, GameType[args.type])
    elif args.full:
        crawl_all(args.year)
    else:
        run()
