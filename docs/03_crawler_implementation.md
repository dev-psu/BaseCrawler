# 크롤러 구현

## 수집 흐름

```
fetch_schedule_html(year, month, game_type)
    └── Playwright 브라우저 실행
        ├── #ddlYear 선택
        ├── #ddlSeries 선택  ← game_type → ddlSeries 값 변환
        ├── #ddlMonth 선택
        └── page.content() 반환

parse_schedule(html, season, year, month, game_type)
    └── #tblScheduleList 파싱
        ├── td.day → 날짜 추출
        ├── td.play → 팀명 + 점수 regex 파싱
        ├── td.relay → 완료/예정 판단
        └── td(notes) → 취소/연기 판단
```

## 파싱 핵심 로직

### 날짜 파싱
`td.day` 텍스트 형식: `06.02(화)`
```python
re.match(r"\d+\.(\d+)", text)  # → 일(day) 숫자 추출
```

### 팀명 + 점수 파싱
`td.play` 텍스트는 하나의 셀에 모두 포함:
```python
_PLAY_RE = re.compile(r"^([가-힣A-Za-z]+)(\d*)vs(\d*)([가-힣A-Za-z]+)$")
# 한화3vs5두산 → ('한화', '3', '5', '두산')
# 한화vs두산   → ('한화', '',  '',  '두산')
```

### 더블헤더 추적
동일 `(game_date, home_team, away_team)` 조합이 한 달에 여러 번 등장할 때 순번 부여:
```python
game_counter: dict[tuple, int] = {}
key = (game_date, home_code, away_code)
game_counter[key] = game_counter.get(key, 0) + 1
game_number = game_counter[key]  # 1, 2, ...
```

### 팀명 → 코드 매핑
```python
TEAM_NAME_TO_CODE = {
    "두산": "DOOSAN", "LG": "LG", "KT": "KT", "SSG": "SSG",
    "NC": "NC", "KIA": "KIA", "롯데": "LOTTE", "삼성": "SAMSUNG",
    "한화": "HANWHA", "키움": "KIWOOM",
}
```

## 수정 이력

### kbo.py — ddlSeries 값 수정
기존 코드의 값이 실제 사이트와 달랐음:

| GameType | 수정 전 | 수정 후 |
|---|---|---|
| EXHIBITION | `"0"` | `"1"` |
| REGULAR | `"1"` | `"0,9,6"` |
| POSTSEASON | `"4"` | `"3,4,5,7"` |

### parser.py — HTML 구조 오인식 수정
기존 코드가 팀명/점수를 별도 셀로 가정했으나, 실제로는 `td.play` 단일 셀에 `한화3vs5두산` 형태로 포함.
- `td.date/num` 클래스 → `td.day` 클래스로 수정
- cell index 전면 재조정 (day row 9 cells / non-day row 8 cells)
- 점수 파싱: `score:score` 형식 → regex 방식으로 전환

### 취소/연기 처리 추가
`notes` 셀(index 7)에서 감지:
- `'취소'` 포함 → `GameStatus.CANCELED`
- `'연기'` 포함 → `GameStatus.POSTPONED`
