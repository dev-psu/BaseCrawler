# 프로젝트 개요

## 구조

```
kbo-crawler/
├── crawler/
│   ├── kbo.py        # Playwright 기반 HTML 수집
│   └── parser.py     # BeautifulSoup 기반 파싱
├── db/
│   ├── connection.py # SQLAlchemy 엔진/세션
│   ├── models.py     # GameEntity (SQLAlchemy ORM)
│   └── repository.py # upsert 로직
├── models/
│   ├── game.py       # Game 도메인 모델 (dataclass)
│   └── team.py       # Team 모델
├── docs/             # 이 문서들
├── main.py           # 진입점 + CLI
└── scheduler.py      # APScheduler (매일 08:00)
```

## 기술 스택

| 항목 | 선택 |
|---|---|
| 언어 | Python 3.14 |
| 브라우저 자동화 | Playwright (sync API) |
| HTML 파싱 | BeautifulSoup4 |
| ORM | SQLAlchemy 2.0 |
| DB | MySQL (BaseLog와 공유) |
| 스케줄러 | APScheduler |

## 연관 프로젝트

- **BaseLog** (`/Users/zaid/Desktop/dev/zaid/pro/BaseLog`) — Kotlin/Spring Boot API 서버, 동일 MySQL DB를 읽어 REST API 제공
- kbo-crawler는 DB에 직접 쓰고, BaseLog는 DB를 읽는 구조

## 실행 방법

```bash
# 현재 월 정규시즌만 (스케줄러용)
python main.py

# 전체 시즌 수집
python main.py --full

# 특정 연도 전체
python main.py --full --year 2024

# 특정 타입만
python main.py --type REGULAR
python main.py --type EXHIBITION

# 특정 월만
python main.py --type REGULAR --month 6

# 스케줄러 실행
python scheduler.py
```
