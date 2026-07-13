import requests
from bs4 import BeautifulSoup
import urllib.robotparser

BASE_URL = "https://www.koreabaseball.com"
HEADERS = {
    "User-Agent": "kbo-info-site-bot/0.1 (personal non-commercial project)"
}

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
    res.raise_for_status()
    res.encoding = "utf-8"   # 인코딩 명시적으로 고정
    return res.text

def parse_team_rank(html: str):
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.tData")  # 순위표 테이블 클래스
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

def main():
    html =
