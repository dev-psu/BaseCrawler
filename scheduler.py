from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler
from main import run_full
from crawler.naver import fetch_today_kbo_games, fetch_game_detail
from db.repository import find_game_id, upsert_game_detail, upsert_today_statuses
from models.game import GameStatus

scheduler = BlockingScheduler(timezone="Asia/Seoul")


def track_b_status_sync() -> None:
    """Track B: 매시간 오늘 경기 취소/연기/상태 동기화"""
    today = date.today()
    try:
        games = fetch_today_kbo_games(today)
        upsert_today_statuses(games)
        print(f"[Track B] {today} 상태 동기화 완료 ({len(games)}경기)")
    except Exception as e:
        print(f"[Track B] 오류: {e}")


def track_c_live_update() -> None:
    """Track C: 매분 17:00~23:00 LIVE/완료 경기 이닝 스코어 업데이트"""
    today = date.today()
    try:
        games = fetch_today_kbo_games(today)
        upsert_today_statuses(games)

        updated = 0
        for g in games:
            if g["status"] not in (GameStatus.LIVE, GameStatus.COMPLETED):
                continue
            game_id = find_game_id(g["game_date"], g["home_team"], g["away_team"], g["game_number"])
            if game_id is None:
                continue
            detail = fetch_game_detail(g["naver_game_id"])
            if detail:
                upsert_game_detail(game_id, detail)
                updated += 1

        if updated:
            print(f"[Track C] {today} 이닝 스코어 업데이트 완료 ({updated}경기)")
    except Exception as e:
        print(f"[Track C] 오류: {e}")


# Track A: 매일 08:00 KBO 공식 전체 일정 수집
scheduler.add_job(run_full, "cron", hour=8, minute=0)

# Track B: 매시간 (:00) 오늘 경기 상태 동기화
scheduler.add_job(track_b_status_sync, "cron", minute=0)

# Track C: 17:00~23:00 매분 라이브 스코어 업데이트
scheduler.add_job(track_c_live_update, "cron", hour="17-23", minute="*")

if __name__ == "__main__":
    print("스케줄러 시작")
    print("  Track A: 매일 08:00 전체 일정 수집")
    print("  Track B: 매시간 상태 동기화")
    print("  Track C: 17:00~23:00 매분 라이브 업데이트")
    scheduler.start()
