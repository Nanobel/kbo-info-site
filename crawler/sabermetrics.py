# 표준 선형가중치 (세이버메트릭스 학계에서 널리 쓰이는 근사 상수)
# 주의: 이건 KBO 전용으로 매 시즌 재계산한 정확한 값이 아니라,
# 여러 리그에서 안정적으로 쓰이는 근사치를 그대로 적용한 것입니다.
WEIGHTS = {
    "bb": 0.69,
    "hbp": 0.72,
    "1b": 0.89,
    "2b": 1.27,
    "3b": 1.62,
    "hr": 2.10,
}

def calc_woba_raw(player: dict) -> float:
    """선수 1명의 '보정 전' wOBA 원점수를 계산"""
    bb = player["bb"]
    hbp = player["hbp"]
    singles = player["hit"] - player["h2"] - player["h3"] - player["hr"]
    numerator = (
        WEIGHTS["bb"] * bb
        + WEIGHTS["hbp"] * hbp
        + WEIGHTS["1b"] * singles
        + WEIGHTS["2b"] * player["h2"]
        + WEIGHTS["3b"] * player["h3"]
        + WEIGHTS["hr"] * player["hr"]
    )
    denominator = player["ab"] + bb + player["sf"] + hbp
    if denominator == 0:
        return 0.0
    return numerator / denominator

def calc_league_totals(players: list) -> dict:
    """리그 전체 합계 계산 (스케일 보정 및 wRC+에 필요)"""
    total_ab = sum(p["ab"] for p in players)
    total_bb = sum(p["bb"] for p in players)
    total_hbp = sum(p["hbp"] for p in players)
    total_sf = sum(p["sf"] for p in players)
    total_pa = sum(p["pa"] for p in players)
    total_run = sum(p["run"] for p in players)

    league_obp_num = sum(
        p["hit"] + p["bb"] + p["hbp"] for p in players
    )
    league_obp_den = total_ab + total_bb + total_hbp + total_sf
    league_obp = league_obp_num / league_obp_den if league_obp_den else 0

    woba_raw_values = [calc_woba_raw(p) * p["pa"] for p in players]
    league_woba_raw = sum(woba_raw_values) / total_pa if total_pa else 0

    woba_scale = league_obp / league_woba_raw if league_woba_raw else 1
    league_r_per_pa = total_run / total_pa if total_pa else 0

    return {
        "league_obp": league_obp,
        "league_woba_raw": league_woba_raw,
        "woba_scale": woba_scale,
        "league_r_per_pa": league_r_per_pa,
    }

def calc_woba(player: dict, league: dict) -> float:
    """보정된(스케일링된) 최종 wOBA"""
    return calc_woba_raw(player) * league["woba_scale"]

def calc_wrc_plus(player: dict, league: dict) -> float:
    """wRC+ 계산 (100 = 리그 평균, 파크팩터는 미적용 근사치)"""
    woba = calc_woba(player, league)
    if player["pa"] == 0:
        return 0.0
    wraa_per_pa = (woba - league["league_obp"]) / league["woba_scale"]
    player_r_per_pa = wraa_per_pa + league["league_r_per_pa"]
    if league["league_r_per_pa"] == 0:
        return 100.0
    return round((player_r_per_pa / league["league_r_per_pa"]) * 100, 1)
