import json
import os
import requests
from bs4 import BeautifulSoup
import urllib.robotparser

BASE_URL = "https://www.koreabaseball.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

HITTER_COLUMNS = ["rank", "name", "team", "avg", "games", "pa", "ab", "run",
                  "hit", "h2", "h3", "hr", "tb", "rbi", "sac", "sf"]

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
        cols = [td.get_text(strip=True) for td in row.select("td")]
        if cols:
            results.append(cols)
    return results

    rows = table.select("tbody tr")
    results = []
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.select("td")]
        if cols:
            results.append(cols)
    return results

def save_json(data: list, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"저장 완료: {path} ({len(data)}개)")

def crawl_hitters():
    html = fetch_page("/Record/Player/HitterBasic/Basic1.aspx")
    if html is None:
        return
    rows = parse_hitter_basic(html)
    data = [dict(zip(HITTER_COLUMNS, row)) for row in rows]
    save_json(data, "data/players/hitters_basic.json")

def debug_detail_page():
    html = fetch_page("/Record/Player/HitterBasic/Detail1.aspx")
    if html is None:
        return
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.tData01")
    if table is None:
        print("세부기록 테이블을 찾을 수 없습니다.")
        return

    header_row = table.select_one("thead tr")
    headers = [th.get_text(strip=True) for th in header_row.select("th")]
    print(f"컬럼 목록: {headers}")

    first_row = table.select_one("tbody tr")
    if first_row:
        first_data = [td.get_text(strip=True) for td in first_row.select("td")]
        print(f"첫 번째 선수 데이터: {first_data}")
        
if __name__ == "__main__":
    crawl_hitters()
