import requests
from datetime import date
from models.game import GameStatus

_SCHEDULE_URL = "https://api-gw.sports.naver.com/schedule/games"
_RECORD_URL = "https://api-gw.sports.naver.com/schedule/games/{game_id}/record"

_NAVER_CODE_TO_TEAM = {
    "HH": "HANWHA", "OB": "DOOSAN", "NC": "NC", "SS": "SAMSUNG",
    "WO": "KIWOOM", "SK": "SSG", "LT": "LOTTE", "HT": "KIA",
    "LG": "LG", "KT": "KT",
}

_NAVER_STATUS_MAP = {
    "BEFORE": GameStatus.SCHEDULED,
    "LIVE": GameStatus.LIVE,
    "RESULT": GameStatus.COMPLETED,
}


def _parse_status(cancel: bool, suspended: bool, status_code: str) -> GameStatus:
    if cancel:
        return GameStatus.CANCELED
    if suspended:
        return GameStatus.POSTPONED
    return _NAVER_STATUS_MAP.get(status_code, GameStatus.SCHEDULED)


def _game_number_from_id(game_id: str) -> int:
    # 형식: {YYYYMMDD(8)}{away(2)}{home(2)}{N(1)}{season(4)}
    return int(game_id[12]) + 1


def fetch_today_kbo_games(target_date: date) -> list[dict]:
    date_str = target_date.strftime("%Y-%m-%d")
    resp = requests.get(
        _SCHEDULE_URL,
        params={
            "fields": "basic,schedule,baseball",
            "upperCategoryId": "kbaseball",
            "fromDate": date_str,
            "toDate": date_str,
            "size": 500,
        },
        timeout=10,
    )
    resp.raise_for_status()

    games = []
    for g in resp.json().get("result", {}).get("games", []):
        if g.get("categoryId") != "kbo":
            continue
        home_code = _NAVER_CODE_TO_TEAM.get(g.get("homeTeamCode", ""))
        away_code = _NAVER_CODE_TO_TEAM.get(g.get("awayTeamCode", ""))
        if not home_code or not away_code:
            continue

        game_id = g["gameId"]
        games.append({
            "naver_game_id": game_id,
            "game_date": date.fromisoformat(g["gameDate"]),
            "home_team": home_code,
            "away_team": away_code,
            "home_score": g.get("homeTeamScore"),
            "away_score": g.get("awayTeamScore"),
            "game_number": _game_number_from_id(game_id),
            "status": _parse_status(
                g.get("cancel", False),
                g.get("suspended", False),
                g.get("statusCode", ""),
            ),
        })
    return games


def fetch_game_detail(naver_game_id: str) -> dict | None:
    resp = requests.get(
        _RECORD_URL.format(game_id=naver_game_id),
        timeout=10,
    )
    if resp.status_code != 200:
        return None

    score_board = (
        resp.json()
        .get("result", {})
        .get("recordData", {})
        .get("scoreBoard")
    )
    if not score_board:
        return None

    rheb = score_board.get("rheb", {})
    inn = score_board.get("inn", {})

    return {
        "away_hits":   rheb.get("away", {}).get("h", 0),
        "away_errors": rheb.get("away", {}).get("e", 0),
        "home_hits":   rheb.get("home", {}).get("h", 0),
        "home_errors": rheb.get("home", {}).get("e", 0),
        "innings": {"away": inn.get("away", []), "home": inn.get("home", [])},
    }
