import json
import os
import requests
from bs4 import BeautifulSoup
import urllib.robotparser

BASE_URL = "https://www.koreabaseball.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

COLUMNS = ["rank", "team", "games", "win", "lose", "draw", "win_rate",
           "game_behind", "recent10", "streak", "home", "away"]

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
    print(f"[상태 코드] {res.status_code}")
    res.raise_for_status()
    res.encoding = "utf-8"
    return res.text

def parse_team_rank(html: str):
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.tData")
    if table is None:
        print("순위표 테이블을 찾을 수 없습니다. 페이지 구조가 바뀌었을 수 있어요.")
        return []

    rows = table.select("tbody tr")
    results = []
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.select("td")]
        if cols:
            results.append(cols)
    return results

def save_team_rank(teams: list, path: str = "data/standings/latest.json"):
    data = [dict(zip(COLUMNS, row)) for row in teams]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"저장 완료: {path} ({len(data)}개 팀)")

def main():
    html = fetch_page("/Record/TeamRank/TeamRank.aspx")
    if html is None:
        return

    teams = parse_team_rank(html)
    save_team_rank(teams)

if __name__ == "__main__":
    main()
