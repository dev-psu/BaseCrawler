# 데이터 수집 전략

## 3-트랙 스케줄러

```
Track A — 매일 08:00 (KBO 공식 사이트, Playwright)
  전체 시즌 일정 upsert → game 테이블

Track B — 매시간 :00 (Naver API, HTTP GET)
  오늘 경기 상태 동기화 → 취소/연기 감지

Track C — 매분 17:00~23:00 (Naver API, HTTP GET)
  LIVE/완료 경기 이닝 스코어 업데이트 → game_detail 테이블
```

### 트랙별 역할 분리 이유

- **Track A**: KBO 공식 사이트가 전체 시즌 일정의 원본. 월별로 한 번에 수집 가능
- **Track B**: 당일 취소/연기는 17:30 이전에 확정되는 경우도 있어 별도 경량 동기화 필요
- **Track C**: Playwright 없이 HTTP GET만으로 실시간 이닝 스코어 수집 가능

## 월별 탐색 범위 (Track A)

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

## 요청 딜레이

KBO 서버 부하 방지 — 월 단위 크롤링 사이에 랜덤 딜레이:
```python
time.sleep(random.uniform(0.1, 0.5))  # 100~500ms
```

Track B/C는 Naver API 사용으로 딜레이 불필요.

## 병렬 수집을 하지 않는 이유 (Track A)

- 1년치 탐색 월 수: 시범 4 + 정규 9 + 포스트 4 = 17회
- 완전 병렬이면 브라우저 17개 동시 → KBO 서버 입장에서 동시 요청 ~51개
- 하루 한 번 배치이므로 순차 실행으로 충분 (약 3~5분)
