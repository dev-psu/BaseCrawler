from datetime import date, time
from bs4 import BeautifulSoup
from models.game import Game, GameStatus
from models.team import Team

# KBO 사이트 표기명 → 내부 팀 코드
# 실제 사이트 크롤링 후 팀명 표기 확인 필요
TEAM_NAME_TO_CODE: dict[str, str] = {
    "두산": "OB",
    "LG": "LG",
    "KT": "KT",
    "SSG": "SSG",
    "NC": "NC",
    "KIA": "KIA",
    "롯데": "LT",
    "삼성": "SS",
    "한화": "HH",
    "키움": "KW",
}

KNOWN_TEAMS: list[Team] = [
    Team(code="OB",  name="두산 베어스",  short_name="두산"),
    Team(code="LG",  name="LG 트윈스",   short_name="LG"),
    Team(code="KT",  name="KT 위즈",     short_name="KT"),
    Team(code="SSG", name="SSG 랜더스",  short_name="SSG"),
    Team(code="NC",  name="NC 다이노스", short_name="NC"),
    Team(code="KIA", name="KIA 타이거즈",short_name="KIA"),
    Team(code="LT",  name="롯데 자이언츠",short_name="롯데"),
    Team(code="SS",  name="삼성 라이온즈",short_name="삼성"),
    Team(code="HH",  name="한화 이글스", short_name="한화"),
    Team(code="KW",  name="키움 히어로즈",short_name="키움"),
]


def parse_schedule(html: str, season: int, year: int, month: int) -> list[Game]:
    soup = BeautifulSoup(html, "html.parser")
    games: list[Game] = []

    # KBO 사이트 일정 테이블 id — 실제 HTML 확인 후 조정 필요
    table = soup.select_one("#tblScheduleList")
    if not table:
        return games

    current_day: int | None = None

    for row in table.select("tr"):
        date_cell = row.select_one("td.date, td.num")
        if date_cell:
            text = date_cell.get_text(strip=True).split("(")[0].strip()
            try:
                current_day = int(text)
            except ValueError:
                pass

        if current_day is None:
            continue

        cells = row.select("td")
        if len(cells) < 5:
            continue

        game = _parse_row(cells, date(year, month, current_day), season)
        if game:
            games.append(game)

    return games


def _parse_row(cells: list, game_date: date, season: int) -> Game | None:
    time_text  = cells[0].get_text(strip=True)
    away_text  = cells[1].get_text(strip=True)
    score_text = cells[2].get_text(strip=True)
    home_text  = cells[3].get_text(strip=True)
    venue_text = cells[4].get_text(strip=True)

    away_code = TEAM_NAME_TO_CODE.get(away_text)
    home_code = TEAM_NAME_TO_CODE.get(home_text)
    if not away_code or not home_code:
        return None

    game_time = _parse_time(time_text)
    home_score, away_score, status = _parse_score(score_text)

    return Game(
        season=season,
        game_date=game_date,
        game_time=game_time,
        home_team_code=home_code,
        away_team_code=away_code,
        venue=venue_text or None,
        home_score=home_score,
        away_score=away_score,
        status=status,
    )


def _parse_time(text: str) -> time | None:
    try:
        h, m = text.split(":")
        return time(int(h), int(m))
    except (ValueError, AttributeError):
        return None


def _parse_score(text: str) -> tuple[int | None, int | None, GameStatus]:
    if not text or text == "-":
        return None, None, GameStatus.SCHEDULED
    if "취소" in text or "우천" in text:
        return None, None, GameStatus.CANCELED
    if "연기" in text:
        return None, None, GameStatus.POSTPONED

    # 완료된 경기: "5:3" 형태
    if ":" in text:
        try:
            away_str, home_str = text.split(":")
            return int(home_str.strip()), int(away_str.strip()), GameStatus.COMPLETED
        except ValueError:
            pass

    return None, None, GameStatus.SCHEDULED
