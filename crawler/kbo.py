from playwright.sync_api import sync_playwright
from models.game import GameType

KBO_SCHEDULE_URL = "https://www.koreabaseball.com/Schedule/Schedule.aspx"

# KBO 사이트 select 요소 id — 변경 시 여기만 수정
_SEL_YEAR = "#ddlYear"
_SEL_MONTH = "#ddlMonth"
_SEL_SERIES = "#ddlSeries"

# KBO 사이트 경기 종류 값 — 실제 사이트 확인 후 조정 필요
_GAME_TYPE_VALUES: dict[GameType, str] = {
    GameType.EXHIBITION: "1",
    GameType.REGULAR: "0,9,6",
    GameType.POSTSEASON: "3,4,5,7",
}


def fetch_schedule_html(year: int, month: int, game_type: GameType) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(KBO_SCHEDULE_URL, wait_until="networkidle")

        page.select_option(_SEL_YEAR, str(year))
        page.wait_for_load_state("networkidle")

        page.select_option(_SEL_SERIES, _GAME_TYPE_VALUES[game_type])
        page.wait_for_load_state("networkidle")

        page.select_option(_SEL_MONTH, f"{month:02d}")
        page.wait_for_load_state("networkidle")

        html = page.content()
        browser.close()
        return html
