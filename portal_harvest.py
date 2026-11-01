# -*- coding: utf-8 -*-
"""予約サイトの「NEW OPEN」の店を毎日集め続ける（会長 2026-11-01「②の条件で再開して」）.

portal_leads.py は一覧の URL を1つずつ渡す作り。ここは全国の地域の一覧を順に回し、1日 DAY_MAX 店まで足す。
回す一覧: ホットペッパービューティー（地方 svcS? → 地域 mac??）・ホットペッパーグルメ（都道府県 SA01〜47 → 地域 Y???）。
どちらも robots.txt で許可された一覧だけ（/CSP/ などは触らない）。食べログは回さない（手で渡す時だけ）。
1店ずつの判定（送らない店・仮説 H1〜H9）は ~/sales-automation/src/need_hypo.py。Google 店検索の上限は portal_leads の PORTAL_PLACES_DAY。
出力: data/leads/portal_leads.jsonl（portal_leads.py が足す）／data/leads/portal_areas.json（地域の一覧と、地域ごとの 足した・判定を通った・メールまで取れた数）\n回す順: 美容3・グルメ1。2周目からは成績の良い地域を先に（next_area・会長 2026-11-01「3実行」）
実行: python3 portal_harvest.py [--max 30]   毎日 17:20（launchd com.hitotsunagi.portal-harvest・Google 店検索の上限が17時に戻った後）
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
AREAS = os.path.join(HERE, "data", "leads", "portal_areas.json")
OUT = os.path.join(HERE, "data", "leads", "portal_leads.jsonl")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"}
DAY_MAX = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 30
PER_AREA = 6          # 1つの地域から足す最大（同じ街ばかりにしない）
AREAS_PER_DAY = 12    # 1日に開く地域の数の上限（相手のサイトに負担をかけない）


def get(u: str) -> str:
    time.sleep(3)
    return requests.get(u, headers=UA, timeout=20).text


def build_areas() -> list[str]:
    """美容（地域）とグルメ（地域）を交互に並べる"""
    beauty, food = [], []
    for reg in sorted(set(re.findall(r"/svc(S[A-Z])/", get("https://beauty.hotpepper.jp/")))):
        for m in sorted(set(re.findall(rf"/svc{reg}/(mac[A-Z]{{2}})/", get(f"https://beauty.hotpepper.jp/svc{reg}/")))):
            beauty.append(f"https://beauty.hotpepper.jp/svc{reg}/{m}/salon/")
    for i in range(1, 48):
        sa = f"SA{i:02d}"
        for y in sorted(set(re.findall(rf"/{sa}/(Y\d{{3}})/", get(f"https://www.hotpepper.jp/{sa}/")))):
            food.append(f"https://www.hotpepper.jp/{sa}/{y}/lst/")
    out = []
    for i in range(max(len(beauty), len(food))):
        out += [x[i] for x in (beauty, food) if i < len(x)]
    return out


def places_left() -> bool:
    """Google 店検索の今日の分が残っているか（portal_leads.places_take と同じ記録）。無い店は照合できず判定に使えない"""
    from datetime import datetime
    try:
        d = json.load(open(os.path.join(HERE, "data", "leads", "places_used.json"), encoding="utf-8"))
    except Exception:
        return True
    return d.get(datetime.now().strftime("%Y-%m-%d"), 0) < int(os.getenv("PORTAL_PLACES_DAY", "30"))


def count() -> int:
    return sum(1 for _ in open(OUT, encoding="utf-8")) if os.path.exists(OUT) else 0


BEAUTY_SHARE = 3   # 美容の地域を何回に対してグルメ1回（2026-11-01: 判定を通った割合 美容40%＝118店中47・グルメ14%＝42店中6）


def area_score(stat: dict) -> float:
    """地域の成績: 判定を通った店＋メールまで取れた店（×3）を、足した店の数で割る。未試行は None 扱いで呼ばない"""
    return (stat.get("pass", 0) + 3 * stat.get("mail", 0)) / max(stat.get("added", 0), 1)


def next_area(st: dict) -> str:
    """回す順: 1周目は美容3・グルメ1の割合で順番に。2周目からは成績（area_score）の良い地域を先に（会長 2026-11-01「3実行」）"""
    urls, stat = st["urls"], st.setdefault("stat", {})
    beauty = [u for u in urls if "beauty.hotpepper" in u]
    food = [u for u in urls if u not in beauty]
    k = st.setdefault("turn", 0)
    st["turn"] = k + 1
    pool = food if (k % (BEAUTY_SHARE + 1)) == BEAUTY_SHARE else beauty
    pool = pool or urls
    untried = [u for u in pool if u not in stat]
    if untried:
        stat[untried[0]] = {"added": 0, "pass": 0, "mail": 0, "opened": 0}   # 選んだ時点で試した地域にする（同じ所を続けて開かない）
        return untried[0]
    st["laps"] = max(st.get("laps", 0), 1)
    return max(pool, key=lambda u: (area_score(stat[u]), -stat[u].get("opened", 0)))   # 同じ成績なら開いた回数の少ない所


def judge_new(start: int) -> tuple[int, int, int]:
    """start 行目より後に足された店の (数, 判定を通った数, メールまで取れた数)"""
    sys.path.insert(0, os.path.expanduser("~/sales-automation"))
    from src import need_hypo as N
    rows = [json.loads(l) for i, l in enumerate(open(OUT, encoding="utf-8")) if i >= start and l.strip()]
    ok = [r for r in rows if not N.judge(r)["exclude"]]
    mail = [r for r in ok if any("example" not in e for e in r.get("emails") or [])]
    return len(rows), len(ok), len(mail)


def main() -> None:
    st = json.load(open(AREAS, encoding="utf-8")) if os.path.exists(AREAS) else {}
    if not st.get("urls") or "--rebuild" in sys.argv:
        st = {"urls": build_areas(), "laps": 0, "stat": {}}
        print(f"[HARVEST] 地域の一覧 {len(st['urls'])}")
    before, opened = count(), 0
    while count() - before < DAY_MAX and opened < AREAS_PER_DAY:
        if not places_left():
            print("[HARVEST] Google 店検索の今日の上限に届いたので終わり（残りは明日）"); break
        u = next_area(st)
        opened += 1
        start = count()
        left = min(PER_AREA, DAY_MAX - (count() - before))
        r = subprocess.run([sys.executable, os.path.join(HERE, "portal_leads.py"), u, "--new-only", "--n", str(left), "--pages", "3"],
                           capture_output=True, text=True, timeout=1800, cwd=HERE)
        tail = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
        print(f"[HARVEST] {u} → {tail[0][:120]}")
        try:
            n, ok, mail = judge_new(start)
            x = st["stat"][u]
            x["added"] += n; x["pass"] += ok; x["mail"] += mail; x["opened"] += 1
            print(f"[HARVEST]   足した {n}・判定を通った {ok}・メールまで {mail}")
        except Exception as e:
            print(f"[HARVEST]   判定の記録に失敗（集めた店はそのまま）: {e}")
        json.dump(st, open(AREAS, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[HARVEST] 今日 {count() - before}店を足した（地域 {opened}・試した地域 {len(st.get('stat', {}))}/{len(st['urls'])}・{st.get('laps', 0)}周目）")


if __name__ == "__main__":
    main()
