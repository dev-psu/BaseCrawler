# DB 스키마

## game 테이블

BaseLog Flyway 마이그레이션 기준 (V4 + V6 + V7):

```sql
CREATE TABLE game
(
    id          BIGINT   NOT NULL AUTO_INCREMENT,
    season      SMALLINT NOT NULL,
    game_type   ENUM ('EXHIBITION', 'REGULAR', 'POSTSEASON') NOT NULL,
    game_date   DATE     NOT NULL,
    game_time   TIME     NULL,
    home_team   ENUM ('DOOSAN', 'LG', 'KT', 'SSG', 'NC', 'SAMSUNG', 'HANWHA', 'LOTTE', 'KIA', 'KIWOOM') NOT NULL,
    away_team   ENUM ('DOOSAN', 'LG', 'KT', 'SSG', 'NC', 'SAMSUNG', 'HANWHA', 'LOTTE', 'KIA', 'KIWOOM') NOT NULL,
    venue       VARCHAR(100) NULL,
    home_score  INT      NULL,
    away_score  INT      NULL,
    status      ENUM ('SCHEDULED', 'LIVE', 'COMPLETED', 'CANCELED', 'POSTPONED') NOT NULL DEFAULT 'SCHEDULED',
    game_number INT      NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_game (season, game_type, game_date, home_team, away_team, game_number)
);
```

### 필드 설명

| 필드 | 설명 |
|---|---|
| `season` | 시즌 연도 (ex: 2026) |
| `game_type` | 경기 종류 |
| `game_date` | 경기 날짜 |
| `game_time` | 경기 시작 시간 (nullable) |
| `home_team` | 홈팀 코드 |
| `away_team` | 원정팀 코드 |
| `venue` | 구장명 (잠실, 대구, 문학 등) |
| `home_score` | 홈팀 득점 (경기 후) |
| `away_score` | 원정팀 득점 (경기 후) |
| `status` | 경기 상태 |
| `game_number` | 더블헤더 구분 (1: 첫 번째, 2: 두 번째) |

### status 값

| 값 | 의미 | 수집 출처 |
|---|---|---|
| `SCHEDULED` | 예정 | KBO 공식 (Track A) |
| `LIVE` | 진행 중 | Naver API (Track C) |
| `COMPLETED` | 종료 | KBO 공식 / Naver API |
| `CANCELED` | 취소 | KBO 공식 / Naver API (Track B) |
| `POSTPONED` | 연기 | KBO 공식 / Naver API (Track B) |

## game_detail 테이블

완료/진행 중 경기의 이닝별 스코어 및 R/H/E (Flyway V6 + V8):

```sql
CREATE TABLE game_detail
(
    game_id     BIGINT NOT NULL,
    away_hits   INT    NOT NULL,
    away_errors INT    NOT NULL,
    home_hits   INT    NOT NULL,
    home_errors INT    NOT NULL,
    innings     JSON   NOT NULL,
    PRIMARY KEY (game_id),
    CONSTRAINT fk_game_detail_game FOREIGN KEY (game_id) REFERENCES game (id)
);
```

### innings JSON 구조

```json
{
  "away": [0, 0, 2, 0, 0, 0, 0, 3, 0],
  "home": [1, 0, 1, 4, 0, 0, 0, 0]
}
```

- `away[i]`: i+1회 원정팀 득점
- `home[i]`: i+1회 홈팀 득점 (9회말 공격 없이 끝나면 배열 길이가 짧을 수 있음)

## upsert 전략

### game 테이블 (Track A)

MySQL `INSERT ... ON DUPLICATE KEY UPDATE` — bulk 단일 쿼리:

```python
stmt = mysql_insert(GameEntity).values(rows)
stmt = stmt.on_duplicate_key_update(
    game_time=stmt.inserted.game_time,
    venue=stmt.inserted.venue,
    home_score=stmt.inserted.home_score,
    away_score=stmt.inserted.away_score,
    status=stmt.inserted.status,
    game_number=stmt.inserted.game_number,
)
```

### game 상태 업데이트 (Track B/C)

Naver API 응답 기준으로 오늘 경기만 UPDATE:

```python
UPDATE game
SET status = :status, home_score = :home_score, away_score = :away_score
WHERE game_date = :game_date
  AND home_team = :home_team
  AND away_team = :away_team
  AND game_number = :game_number
```

### game_detail (Track C)

```python
stmt = mysql_insert(GameDetailEntity).values(game_id=game_id, **detail)
stmt = stmt.on_duplicate_key_update(
    away_hits=stmt.inserted.away_hits,
    away_errors=stmt.inserted.away_errors,
    home_hits=stmt.inserted.home_hits,
    home_errors=stmt.inserted.home_errors,
    innings=stmt.inserted.innings,
)
```

## BaseLog Flyway 마이그레이션 이력

| 버전 | 내용 |
|---|---|
| V4 | game 테이블 생성 |
| V5 | no-op (game_number는 V4에 포함됨) |
| V6 | game.status에 LIVE 추가, game_detail 테이블 생성 |
| V7 | game.game_number SMALLINT → INT |
| V8 | game_detail 컬럼 TINYINT → INT |

## BaseLog 연동

kbo-crawler와 BaseLog는 동일한 MySQL DB를 공유:
- kbo-crawler → SQLAlchemy로 직접 write
- BaseLog → Spring Data JPA로 read
