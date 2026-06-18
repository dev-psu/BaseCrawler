# kbo-crawler

KBO 공식 사이트와 네이버 스포츠 API에서 경기 일정·결과·이닝 스코어를 수집해  
BaseLog MySQL DB에 upsert하는 Python 크롤러.

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.12 |
| 브라우저 자동화 | Playwright (sync) |
| HTML 파싱 | BeautifulSoup4 |
| HTTP | requests |
| ORM | SQLAlchemy 2.0 |
| DB | MySQL 8.0 (BaseLog와 공유) |
| 스케줄러 | APScheduler |

---

## 프로젝트 구조

```
kbo-crawler/
├── crawler/
│   ├── kbo.py        # Playwright — KBO 공식 사이트 HTML 수집
│   ├── parser.py     # BeautifulSoup — 일정 파싱, 더블헤더 추적
│   └── naver.py      # 네이버 스포츠 API — 당일 상태·이닝 스코어
├── db/
│   ├── connection.py # SQLAlchemy 엔진, .env 기반 DB 연결
│   ├── models.py     # GameEntity, GameDetailEntity (BaseLog 스키마 동일)
│   └── repository.py # upsert_games, upsert_today_statuses, upsert_game_detail
├── models/
│   ├── game.py       # Game 도메인 모델 (dataclass), GameType, GameStatus
│   └── team.py       # 팀명 → KboTeam 코드 매핑
├── docs/             # 상세 구현 문서
├── main.py           # CLI 진입점
└── scheduler.py      # 3-트랙 스케줄러
```

---

## 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

`.env` 파일 생성:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=baselog
DB_USER=root
DB_PASSWORD=baselog
```

---

## 실행

```bash
# 현재 월 정규시즌만 수집 (스케줄러 기본 단위)
python main.py

# 전체 시즌 수집 (시범 + 정규 + 포스트시즌)
python main.py --full

# 특정 연도 전체
python main.py --full --year 2025

# 특정 타입만
python main.py --type REGULAR
python main.py --type EXHIBITION

# 특정 월만 (--type 필수)
python main.py --type REGULAR --month 6

# 스케줄러 실행
python scheduler.py
```

---

## 3-트랙 스케줄러

| 트랙 | 주기 | 소스 | 대상 |
|------|------|------|------|
| Track A | 매일 08:00 | KBO 공식 사이트 (Playwright) | game 테이블 전체 일정 upsert |
| Track B | 매시간 :00 | 네이버 스포츠 API | 당일 경기 취소·연기·상태 동기화 |
| Track C | 17:00~23:00 매분 | 네이버 스포츠 API | LIVE·완료 경기 이닝 스코어 upsert |

Track A는 Playwright 브라우저를 띄워 HTML을 수집하므로 순차 실행.  
Track B·C는 경량 HTTP GET으로 실시간 동기화.

---

## 파싱 핵심

### 팀명·점수 추출 (parser.py)

KBO 사이트의 `td.play` 셀은 `한화3vs5두산` 형태로 팀명과 점수가 혼합됨:

```python
_PLAY_RE = re.compile(r"^([가-힣A-Za-z]+)(\d*)vs(\d*)([가-힣A-Za-z]+)$")
```

### 더블헤더 순번

동일 `(날짜, 홈팀, 원정팀)` 조합이 한 달에 여러 번 등장하면 `game_number` 1, 2로 자동 부여.

### DB upsert

MySQL `ON DUPLICATE KEY UPDATE` 기반. UNIQUE 제약: `(season, game_type, game_date, home_team, away_team, game_number)`.

---

## 연관 프로젝트

- **BaseLog** (`../BaseLog`) — 동일 MySQL DB를 읽어 REST API 제공
- kbo-crawler는 DB에 쓰고, BaseLog API는 DB에서 읽기만 함

상세 구현은 `docs/` 디렉터리 참고.
