# KBO 사이트 구조

## 스케줄 페이지

URL: `https://www.koreabaseball.com/Schedule/Schedule.aspx`

### 드롭다운 선택자

| 선택자 | 설명 | 값 |
|---|---|---|
| `#ddlYear` | 연도 | `2001` ~ `2026` |
| `#ddlMonth` | 월 | `01` ~ `12` (두 자리) |
| `#ddlSeries` | 경기 종류 | 아래 표 참고 |

### ddlSeries 값

| 경기 종류 | value |
|---|---|
| 시범경기 | `1` |
| 정규시즌 | `0,9,6` |
| 포스트시즌 | `3,4,5,7` |

### 스케줄 테이블 구조 (`#tblScheduleList`)

**날짜 있는 행 (9 cells)**
```
[td.day] [td.time] [td.play] [td.relay] [td] [td] [td] [td(venue)] [td(notes)]
```

**날짜 없는 행 (8 cells)**
```
[td.time] [td.play] [td.relay] [td] [td] [td] [td(venue)] [td(notes)]
```

### play 셀 형식

```
완료 경기: 한화3vs5두산   (원정팀 + 원정점수 + vs + 홈점수 + 홈팀)
예정 경기: 한화vs두산     (점수 없음)
```

정규식: `^([가-힣A-Za-z]+)(\d*)vs(\d*)([가-힣A-Za-z]+)$`

### relay 셀 값

| 값 | 상태 |
|---|---|
| `리뷰` | 완료 (COMPLETED) |
| `프리뷰` | 예정 (SCHEDULED) |
| `` (빈 값) | 예정 (SCHEDULED) |

### notes 셀 (비고) 값

| 포함 문자열 | 상태 |
|---|---|
| `취소` | CANCELED (우천취소, 미세먼지취소, 폭염취소 등) |
| `연기` | POSTPONED |

## 게임센터 페이지

URL: `https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx?gameDate={YYYYMMDD}&gameId={gameId}&section=REVIEW`

### gameId 생성 규칙

형식: `{YYYYMMDD}{원정팀코드}{홈팀코드}{game_number - 1}`

예시: `20260602HHOB0` → 2026-06-02, 한화(원정) vs 두산(홈), 1번 경기

### KBO 팀코드 매핑

| 우리 코드 | KBO 사이트 코드 |
|---|---|
| HANWHA | HH |
| DOOSAN | OB |
| NC | NC |
| SAMSUNG | SS |
| KIWOOM | WO |
| SSG | SK |
| LOTTE | LT |
| KIA | HT |
| LG | LG |
| KT | KT |

### 게임센터 테이블

| 테이블 ID | 내용 |
|---|---|
| `tblScordboard2` | 이닝별 점수 (1~12회) |
| `tblScordboard3` | R / H / E / B 합계 |
| `tblEtc` | 결승타, 홈런, 장타, 도루, 심판 |
| `tblAwayPitcher` / `tblHomePitcher` | 투수 기록 |
| `tblAwayHitter1/3` / `tblHomeHitter1/3` | 타자 기록 |

## 월별 데이터 분포 (2025년 기준)

| 경기 종류 | 데이터 있는 월 | 경기 수 |
|---|---|---|
| 시범경기 | 3월 | 50경기 |
| 정규시즌 | 3~10월 | 804경기 |
| 포스트시즌 | 10월 | 16경기 |
