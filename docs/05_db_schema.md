# DB 스키마

## game 테이블

BaseLog Flyway 마이그레이션 기준 (V4 + V5):

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
    status      ENUM ('SCHEDULED', 'COMPLETED', 'CANCELED', 'POSTPONED') NOT NULL DEFAULT 'SCHEDULED',
    game_number TINYINT  NOT NULL DEFAULT 1,
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

### Unique Key 구성

`(season, game_type, game_date, home_team, away_team, game_number)`
- 더블헤더: 같은 날 같은 매치업이 `game_number=1`, `game_number=2`로 구분

## upsert 전략

MySQL `INSERT ... ON DUPLICATE KEY UPDATE` 사용 — bulk 단일 쿼리:

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

upsert 기준 컬럼 (변경 없음): `season`, `game_type`, `game_date`, `home_team`, `away_team`, `game_number`
업데이트 컬럼 (덮어쓰기): `game_time`, `venue`, `home_score`, `away_score`, `status`

## kbo-crawler GameEntity (SQLAlchemy)

```python
class GameEntity(Base):
    __tablename__ = "game"
    __table_args__ = (
        UniqueConstraint("season", "game_type", "game_date",
                         "home_team", "away_team", "game_number", name="uq_game"),
    )
    id:          Mapped[int]       # PK, autoincrement
    season:      Mapped[int]       # SmallInteger
    game_type:   Mapped[GameType]  # Enum
    game_date:   Mapped[date]
    game_time:   Mapped[time|None]
    home_team:   Mapped[str]       # TEAM_ENUM
    away_team:   Mapped[str]       # TEAM_ENUM
    venue:       Mapped[str|None]
    home_score:  Mapped[int|None]
    away_score:  Mapped[int|None]
    status:      Mapped[GameStatus]
    game_number: Mapped[int]       # SmallInteger, default=1
```

## BaseLog 연동

kbo-crawler와 BaseLog는 동일한 MySQL DB를 공유:
- kbo-crawler → SQLAlchemy로 직접 write
- BaseLog → Spring Data JPA로 read

BaseLog 마이그레이션 파일:
- `V4__add_game_schedule.sql` — game 테이블 생성
- `V5__add_game_number.sql` — game_number 컬럼 추가 및 uq_game 재설정
