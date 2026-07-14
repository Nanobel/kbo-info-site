import json
import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.robotparser

BASE_URL = "https://www.koreabaseball.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

HITTER_COLUMNS = ["rank", "name", "team", "avg", "games", "pa", "ab", "run",
                  "hit", "h2", "h3", "hr", "tb", "rbi", "sac", "sf"]

HITTER_DETAIL_COLUMNS_1 = ["team", "avg", "games", "pa", "ab", "run", "hit",
                           "h2", "h3", "hr", "tb", "rbi", "sb", "cs", "sac", "sf"]

HITTER_DETAIL_COLUMNS_2 = ["bb", "ibb", "hbp", "so", "gdp", "slg", "obp",
                           "e", "sb_pct", "mh", "ops", "risp", "ph_ba"]


def check_robots_allowed(path: str) -> bool:
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{BASE_URL}/robots.txt")
    rp.read()
    return rp.can_fetch(HEADERS["User-Agent"], f"{BASE_URL}{path}")


def fetch_page(path: str):
    if not check_robots_allowed(path):
        print(f"[차단됨] robots.txt에 의해 {path} 크롤링 불가")
        return None
    res = requests.get(f"{BASE_URL}{path}", headers=HEADERS, timeout=10)
    print(f"[상태 코드] {res.status_code} - {path}")
    res.raise_for_status()
    res.encoding = "utf-8"
    return res.text


def parse_hitter_basic(html: str):
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.tData01")
    if table is None:
        print("타자 기록 테이블을 찾을 수 없습니다.")
        return []

    rows = table.select("tbody tr")
    results = []
    for row in rows:
        cells = row.select("td")
        if not cells:
            continue

        cols = [td.get_text(strip=True) for td in cells]

        name_cell = cells[1]
        link = name_cell.select_one("a")
        player_id = None
        if link and link.get("href"):
            match = re.search(r"playerId=(\d+)", link["href"])
            if match:
                player_id = match.group(1)

        row_data = dict(zip(HITTER_COLUMNS, cols))
        row_data["player_id"] = player_id
        results.append(row_data)

    return results


def parse_hitter_detail(html: str):
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")

    season_table = None
    extra_table = None

    for t in tables:
        headers = [th.get_text(strip=True) for th in t.select("thead th")]
        if headers[:1] == ["팀명"]:
            season_table = t
        elif headers[:1] == ["BB"]:
            extra_table = t

    if season_table is None or extra_table is None:
        print("선수 상세기록 테이블을 찾을 수 없습니다.")
        return None

    season_row = season_table.select_one("tbody tr")
    extra_row = extra_table.select_one("tbody tr")
    if season_row is None or extra_row is None:
        return None

    season_cols = [td.get_text(strip=True) for td in season_row.select("td")]
    extra_cols = [td.get_text(strip=True) for td in extra_row.select("td")]

    data = dict(zip(HITTER_DETAIL_COLUMNS_1, season_cols))
    data.update(dict(zip(HITTER_DETAIL_COLUMNS_2, extra_cols)))
    return data


def crawl_hitter_detail(player_id: str):
    html = fetch_page(f"/Record/Player/HitterDetail/Basic.aspx?playerId={player_id}")
    if html is None:
        return None
    return parse_hitter_detail(html)


def save_json(data, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"저장 완료: {path}")


def crawl_hitters():
    html = fetch_page("/Record/Player/HitterBasic/Basic1.aspx")
    if html is None:
        return
    data = parse_hitter_basic(html)
    save_json(data, "data/players/hitters_basic.json")


if __name__ == "__main__":
    result = crawl_hitter_detail("66606")
    print(result)
