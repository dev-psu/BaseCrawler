# 네이버 스포츠 API

Playwright 불필요, 단순 HTTP GET으로 이닝별 스코어 + R/H/E 수집 가능.

## 경기 목록 API

```
GET https://api-gw.sports.naver.com/schedule/games
    ?fields=basic,schedule,baseball,manualRelayUrl
    &upperCategoryId=kbaseball
    &fromDate=2026-06-16
    &toDate=2026-06-16
    &size=500
```

### 응답 필드 (KBO 경기)

```json
{
  "gameId": "20260616HHNC02026",
  "categoryId": "kbo",
  "gameDate": "2026-06-16",
  "gameDateTime": "2026-06-16T18:30:00",
  "stadium": "창원",
  "homeTeamCode": "NC",
  "homeTeamName": "NC",
  "awayTeamCode": "HH",
  "awayTeamName": "한화",
  "homeTeamScore": 0,
  "awayTeamScore": 0,
  "statusCode": "BEFORE",
  "homeStarterName": "구창모",
  "awayStarterName": "화이트",
  "broadChannel": "KBS N SPORTS"
}
```

### statusCode 값

| 값 | 의미 |
|---|---|
| `BEFORE` | 경기 전 |
| `RESULT` | 경기 종료 |
| `LIVE` | 경기 중 (추정) |

## 경기 상세 API (이닝 스코어)

```
GET https://api-gw.sports.naver.com/schedule/games/{gameId}/record
```

### 이닝 스코어 응답

`result.recordData.scoreBoard`:

```json
{
  "rheb": {
    "away": { "r": 1, "h": 6, "e": 1, "b": 2 },
    "home": { "r": 3, "h": 5, "e": 0, "b": 1 }
  },
  "inn": {
    "away": [0, 0, 0, 0, 1, 0, 0, 0, 0],
    "home": [0, 0, 0, 0, 1, 0, 1, 1]
  }
}
```

- `inn.away[i]`: i+1회 원정팀 득점
- `inn.home[i]`: i+1회 홈팀 득점 (9회말 공격 없이 끝나면 배열 길이가 짧을 수 있음)
- `r`: 총 득점 (R), `h`: 총 안타 (H), `e`: 실책 (E), `b`: 볼넷 (B)
- `result.recordData.currentInning`: 현재/최종 이닝 (ex: `"9"`)

## Naver gameId 생성 규칙

형식: `{YYYYMMDD}{원정팀코드}{홈팀코드}{game_number-1}{연도}`

| 예시 | 해석 |
|---|---|
| `20260616HHNC02026` | 2026-06-16, 한화(원정) vs NC(홈), 1번 경기, 2026시즌 |
| `20260613HHWO02026` | 2026-06-13, 한화(원정) vs 키움(홈), 1번 경기, 2026시즌 |

기존 `Game` 모델로 생성:
```python
TEAM_TO_NAVER_CODE = {
    "HANWHA": "HH", "DOOSAN": "OB", "NC": "NC", "SAMSUNG": "SS",
    "KIWOOM": "WO", "SSG": "SK", "LOTTE": "LT", "KIA": "HT",
    "LG": "LG", "KT": "KT",
}

def build_naver_game_id(game: Game) -> str:
    date_str = game.game_date.strftime("%Y%m%d")
    away = TEAM_TO_NAVER_CODE[game.away_team_code]
    home = TEAM_TO_NAVER_CODE[game.home_team_code]
    return f"{date_str}{away}{home}{game.game_number - 1}{game.game_date.year}"
```

## 활용 방안

- 완료 경기: 경기 후 1회 호출로 이닝 스코어 저장
- 라이브 경기: `statusCode == "LIVE"` 확인 후 N분 간격 폴링
- 오늘 경기 목록은 경기 목록 API로 먼저 조회 후 gameId 추출

## 참고 — KBO 공식 스코어보드

URL: `https://www.koreabaseball.com/Schedule/ScoreBoard.aspx?gameDate={YYYYMMDD}`

- `table.tScore` 구조: TEAM | 1~12회 | R | H | E | B
- 데이터가 JS로 동적 로딩되어 Playwright 필요
- 네이버 API 대비 번거로우므로 사용 불필요
