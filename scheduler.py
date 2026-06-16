from apscheduler.schedulers.blocking import BlockingScheduler
from main import run_full

scheduler = BlockingScheduler(timezone="Asia/Seoul")

# 매일 오전 8시 실행
scheduler.add_job(run_full, "cron", hour=8, minute=0)

if __name__ == "__main__":
    print("스케줄러 시작 (매일 08:00 KST)")
    scheduler.start()
