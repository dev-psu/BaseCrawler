# 데이터 수집 전략

## 월별 탐색 범위

데이터가 없는 달은 파싱 결과 0건으로 자동 스킵.

```python
_MONTH_RANGES = {
    GameType.EXHIBITION: range(1, 5),    # 1~4월 탐색 (실제 데이터: 3월)
    GameType.REGULAR:    range(3, 12),   # 3~11월 탐색 (실제 데이터: 3~10월)
    GameType.POSTSEASON: range(9, 13),   # 9~12월 탐색 (실제 데이터: 10월)
}
```

## CLI 실행 옵션

```bash
python main.py                          # 현재 월 정규시즌 (스케줄러 기본값)
python main.py --full                   # 전체 시즌 (시범+정규+포스트)
python main.py --full --year 2024       # 특정 연도 전체
python main.py --type REGULAR           # 정규시즌 전체 월
python main.py --type EXHIBITION        # 시범경기 전체 월
python main.py --type REGULAR --month 6 # 특정 월만
```

## 스케줄러

`scheduler.py` — APScheduler, 매일 08:00 KST 실행:
```python
scheduler.add_job(run_full, "cron", hour=8, minute=0)
```
매일 전체 시즌 upsert 수행. 하루 한 번 전체를 다시 긁어도 bulk upsert로 부담 없음.

## 요청 딜레이

KBO 서버 부하 방지 — 월 단위 크롤링 사이에 랜덤 딜레이:
```python
time.sleep(random.uniform(0.1, 0.5))  # 100~500ms
```

병렬 수집을 하지 않는 이유:
- 1년치 탐색 월 수: 시범 4 + 정규 9 + 포스트 4 = 17회
- 완전 병렬이면 브라우저 17개 동시 → KBO 서버 입장에서 동시 요청 ~51개 (AJAX 포함)
- 하루 한 번 배치이므로 순차 실행으로 충분 (약 3~5분)
