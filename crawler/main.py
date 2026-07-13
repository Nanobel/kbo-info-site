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
    return res.text

def main():
    # 예시: 팀 순위 페이지 (실제 경로는 확인 후 조정 필요)
    html = fetch_page("/Standings/TeamRank.aspx")
    if html is None:
        return
    soup = BeautifulSoup(html, "lxml")
    print(soup.title.string if soup.title else "제목 없음")

if __name__ == "__main__":
    main()
