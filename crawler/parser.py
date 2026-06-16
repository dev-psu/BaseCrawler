import re
from datetime import date, time
from bs4 import BeautifulSoup, Tag
from models.game import Game, GameStatus, GameType

TEAM_NAME_TO_CODE: dict[str, str] = {
    "두산": "DOOSAN",
    "LG": "LG",
    "KT": "KT",
    "SSG": "SSG",
    "NC": "NC",
    "KIA": "KIA",
    "롯데": "LOTTE",
    "삼성": "SAMSUNG",
    "한화": "HANWHA",
    "키움": "KIWOOM",
}

_PLAY_RE = re.compile(r"^([가-힣A-Za-z]+)(\d*)vs(\d*)([가-힣A-Za-z]+)$")


def parse_schedule(html: str, season: int, year: int, month: int, game_type: GameType) -> list[Game]:
    soup = BeautifulSoup(html, "html.parser")
    games: list[Game] = []

    table = soup.select_one("#tblScheduleList")
    if not table:
        return games

    current_day: int | None = None
    # 더블헤더 추적: (game_date, home_code, away_code) → 당일 경기 순번
    game_counter: dict[tuple, int] = {}

    for row in table.select("tr"):
        cells = row.select("td")
        if not cells:
            continue

        day_cell = row.select_one("td.day")
        if day_cell:
            current_day = _parse_day(day_cell.get_text(strip=True))
            data_cells = cells[1:]
        else:
            data_cells = cells

        if current_day is None or len(data_cells) < 8:
            continue

        game_date = date(year, month, current_day)
        game = _parse_row(data_cells, game_date, season, game_type, game_counter)
        if game:
            games.append(game)

    return games


def _parse_day(text: str) -> int | None:
    match = re.match(r"\d+\.(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def _parse_row(
    cells: list[Tag],
    game_date: date,
    season: int,
    game_type: GameType,
    game_counter: dict[tuple, int],
) -> Game | None:
    time_text  = cells[0].get_text(strip=True)
    play_text  = cells[1].get_text(strip=True)
    relay_text = cells[2].get_text(strip=True)
    venue_text = cells[6].get_text(strip=True)
    notes_text = cells[7].get_text(strip=True)

    parsed = _parse_play(play_text)
    if parsed is None:
        return None

    away_code, away_score, home_score, home_code = parsed

    key = (game_date, home_code, away_code)
    game_counter[key] = game_counter.get(key, 0) + 1
    game_number = game_counter[key]

    return Game(
        season=season,
        game_type=game_type,
        game_date=game_date,
        game_time=_parse_time(time_text),
        home_team_code=home_code,
        away_team_code=away_code,
        venue=venue_text or None,
        home_score=home_score,
        away_score=away_score,
        status=_parse_status(relay_text, away_score, notes_text),
        game_number=game_number,
    )


def _parse_play(text: str) -> tuple[str, int | None, int | None, str] | None:
    match = _PLAY_RE.match(text)
    if not match:
        return None

    away_name, away_score_str, home_score_str, home_name = match.groups()

    away_code = TEAM_NAME_TO_CODE.get(away_name)
    home_code = TEAM_NAME_TO_CODE.get(home_name)
    if not away_code or not home_code:
        return None

    away_score = int(away_score_str) if away_score_str else None
    home_score = int(home_score_str) if home_score_str else None

    return away_code, away_score, home_score, home_code


def _parse_time(text: str) -> time | None:
    try:
        h, m = text.split(":")
        return time(int(h), int(m))
    except (ValueError, AttributeError):
        return None


def _parse_status(relay_text: str, away_score: int | None, notes_text: str) -> GameStatus:
    if "취소" in notes_text:
        return GameStatus.CANCELED
    if "연기" in notes_text:
        return GameStatus.POSTPONED
    if relay_text == "리뷰" and away_score is not None:
        return GameStatus.COMPLETED
    return GameStatus.SCHEDULED
