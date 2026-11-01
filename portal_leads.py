# -*- coding: utf-8 -*-
"""ホットペッパービューティー・食べログに載っている店から営業リストを作る（会長 2026-10-21「OTA に依存している所にフックが刺さるように。
ホットペッパーや食べログに掲載している店舗からリストを作り、そこに書いてある情報をリストに入れて、インスタDMでもメールでも送れるように」）.

流れ: 一覧ページ（robots.txt で許可されている場所だけ・1ページ3秒あける）→ 店のページ（店名・住所・営業時間・定休日・支払い・
      カット価格・席数・スタッフ数・こだわり・ホットペッパーの口コミの点と件数）→ Google Places（同じ店のGoogleマップの口コミ件数・星・
      公式サイト・電話・place_id）→ 公式サイト（Instagram・Facebook・公開メール・営業お断り・問い合わせフォーム・求人。list_build.read_site＝送る時と同じ検査）
出力: data/leads/portal_leads.jsonl（1行1店・cid＝"hpb:<サロンID>"／"tbl:<店ID>"・portal／portal_reviews／portal_star）。
      1店ずつの判定（送らない店・仮説 H1〜H9・連絡手段）は ~/sales-automation/src/need_hypo.py、文は src/need_copy.py。毎朝の候補（scripts/dm_daily.py）に混ざる
実行: python3 portal_leads.py <ホットペッパービューティーか食べログの一覧ページのURL> [--n 10] [--start 4] [--pages 3] [--skip-top 10]
      都心の1〜2ページ目は人気店ばかり（10/31 新宿）。--start で深いページから。口コミの日付は maps_chrome.py（いつもの Chrome・毎晩18:30）
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime

import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser("~/sales-automation"))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.expanduser("~/sales-automation/.env"))
import config  # noqa: E402
from src import meo_observe  # noqa: E402

OUT = os.path.join(HERE, "data", "leads", "portal_leads.jsonl")
TBL = re.compile(r"https?://tabelog\.com/[a-z]+/A\d{4}/A\d{6}/(\d{8})/")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"}
WAIT = 3.0   # ホットペッパーへの間隔（秒）
HPG = re.compile(r"https?://www\.hotpepper\.jp/str(J\d+)/")   # ホットペッパーグルメ（来店1人ごとの手数料・10/31 会長「飲食はこちらから」）
NEW_CARD = re.compile(r"NEW\s*OPEN|ニューオープン|新規オープン|オープンしました|グランドオープン|(20\d{2})年\s*\d{1,2}月\s*\d{0,2}日?\s*(?:に)?\s*(?:オープン|OPEN|開業|開店)", re.I)
SALON = re.compile(r"https?://beauty\.hotpepper\.jp/(sln[H0-9]+)/")
INFO_KEYS = ("住所", "営業時間", "定休日", "支払い方法", "カット価格", "席数", "スタッフ数", "駐車場", "こだわり条件", "アクセス・道案内")


def get(url: str) -> str:
    r = requests.get(url, headers=UA, timeout=20)
    r.encoding = r.apparent_encoding or r.encoding
    time.sleep(WAIT)
    return r.text


def page_url(list_url: str, page: int) -> str:
    """一覧の page ページ目（ホットペッパー …/salon/PN2.html・食べログ …/rstLst/2/）"""
    if page <= 1:
        return list_url
    if "hotpepper.jp/SA" in list_url:
        return re.sub(r"/bgn\d+/?$", "/", list_url).rstrip("/") + f"/bgn{page}/"
    if "tabelog.com" in list_url:
        return re.sub(r"/rstLst/(\d+/)?", f"/rstLst/{page}/", list_url, count=1)
    return list_url.rstrip("/") + f"/PN{page}.html"


def kind_of(url: str) -> str:
    return "tabelog" if "tabelog.com" in url else "hpg" if "www.hotpepper.jp" in url else "hpb"


def ranked_urls(list_url: str, pages: int = 3, start: int = 1, new_only: bool = False) -> list[tuple[str, int]]:
    """一覧の並び（ホットペッパーはおすすめ順・食べログは標準＝有料の店が優先）のとおりに [(店のURL, 何番目)]。
    2026-10-31 会長「予約サイトで検索順位が10位に入っていない店を狙う」"""
    out: list[tuple[str, int]] = []
    seen = set()
    for pg in range(start, start + pages):
        html = get(page_url(list_url, pg))
        found = 0
        k = kind_of(list_url)
        pat = {"tabelog": TBL, "hpb": SALON, "hpg": re.compile(r"/str(J\d+)/")}[k]
        ms = [m for m in pat.finditer(html)]
        firsts = {}
        for m in ms:   # 店ごとに最初に出た位置（カードの始まり）
            u = m.group(0) if k == "tabelog" else f"https://beauty.hotpepper.jp/{m.group(1)}/" if k == "hpb" else f"https://www.hotpepper.jp/str{m.group(1)}/"
            firsts.setdefault(u, m.start())
        order = sorted(firsts.items(), key=lambda x: x[1])
        for i, (u, pos) in enumerate(order):
            if u in seen:
                continue
            seen.add(u); found += 1
            card = re.sub(r"<[^>]+>", " ", html[pos: order[i + 1][1] if i + 1 < len(order) else pos + 6000])
            if new_only and not NEW_CARD.search(card):   # 一覧のカードに「NEW OPEN」がある店だけ開く（10/31 会長「開業したばかり」）
                continue
            out.append((u, len(seen) + (start - 1) * 20))
        if not found:
            break
    return out


def shop_urls(list_url: str, n: int) -> list[str]:
    return [u for u, _ in ranked_urls(list_url, 1)][:n]


OPEN_RE = re.compile(r"(20\d{2})年\s*(\d{1,2})月(?:\s*\d{1,2}日)?\s*(?:に)?\s*[!！]?\s*(?:NEW\s*|ニュー|グランド|リニューアル)?\s*(?:オープン|OPEN|開業|開店)", re.I)


def opened_month(text: str) -> str:
    """「2026年9月オープン」「NEW OPEN 2026年8月」などから YYYY-MM（無ければ空）"""
    m = OPEN_RE.search(text or "")
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    m = re.search(r"(?:NEW\s*OPEN|ニューオープン|新規オープン)[^0-9]{0,12}(20\d{2})[./年]\s*(\d{1,2})", text or "", re.I)
    return f"{m.group(1)}-{int(m.group(2)):02d}" if m else ""


def parse_hpg(url: str, html: str) -> dict:
    """ホットペッパーグルメの店のページ（店名・住所・総席数・口コミ件数・ジャンル。HP とオープン日の欄は無い）"""
    soup = BeautifulSoup(html, "html.parser")
    info = {}
    for th in soup.select("th"):
        k = th.get_text(" ", strip=True)
        td = th.find_next_sibling("td")
        if td and 1 < len(k) <= 20 and k not in info:
            info[k] = td.get_text(" ", strip=True)[:300]
    title = soup.title.get_text(strip=True) if soup.title else ""
    g = re.search(r"\(([^/()]+)/([^()]+)\)", title)
    rv = re.search(r"口コミ\s*([\d,]+)\s*件", html)
    text = soup.get_text(" ", strip=True)
    links = [a.get("href", "") for a in soup.select("a[href]")]
    ig = next((h for h in links if re.match(r"https?://(www\.)?instagram\.com/[A-Za-z0-9._]+/?$", h)), "")
    fb = next((h for h in links if re.match(r"https?://(www\.)?facebook\.com/(?!dialog|sharer)[^?]+$", h)), "")
    keep = ("店名", "住所", "アクセス", "営業時間", "定休日", "予算詳細", "総席数", "個室", "貸切", "お店の特長", "備考")
    return {"portal": "hpg", "portal_url": url, "cid": "hpg:" + HPG.match(url).group(1),
            "name": (info.get("店名") or re.sub(r"\(.*", "", title)).replace("\u3000", " ").strip(), "yomi": "",
            "address": info.get("住所", "").replace(" ", "").replace("\u3000", ""), "industry": "飲食店",
            "genre": g.group(2).strip() if g else "", "portal_reviews": int(rv.group(1).replace(",", "")) if rv else None,
            "portal_star": None, "portal_info": {k: info[k] for k in keep if k in info}, "instagram_portal": ig,
            "website_portal": "", "opened": opened_month(text), "new_open_card": bool(re.search(r"NEW\s*OPEN|ニューオープン", text, re.I)),
            "facebook_portal": fb}


def parse_salon(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", property="og:title")
    yomi = (og.get("content") if og else soup.title.get_text()).split("｜")[0].strip()     # 「ナル 新宿(nalu)」＝読み（本当の名前）
    dt = soup.select_one("p.detailTitle a") or soup.select_one(".detailTitle")
    name = re.split(r"[【\[［/／|｜]", dt.get_text(" ", strip=True))[0].strip() if dt else ""   # 「nalu新宿【ナル】髪質改善/…」→ nalu新宿
    paren = re.search(r"[（(]([^）)]+)[）)]\s*$", yomi)
    name = name or (paren.group(1) if paren else yomi)
    info = {}
    for th in soup.find_all("th"):
        k = th.get_text(" ", strip=True)
        if k in INFO_KEYS and k not in info:
            td = th.find_next_sibling("td")
            if td:
                info[k] = re.sub(r"\s+", " ", td.get_text(" ", strip=True))[:300]
    pt = soup.select_one(".slnHeaderKuchikomiPoint")
    cnt = soup.select_one(".slnHeaderKuchikomiCount")
    m = re.search(r"([0-9,]+)", cnt.get_text() if cnt else "")
    ig = ""
    for a in soup.find_all("a", href=True):
        mm = re.match(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{2,30})/?", a["href"])
        if mm and mm.group(1).lower() not in ("hotpepperbeauty", "p", "explore", "accounts"):
            ig = f"https://www.instagram.com/{mm.group(1)}/"; break
    fb = next((a["href"] for a in soup.find_all("a", href=True) if re.match(r"https?://(?:www\.)?facebook\.com/(?!hotpepper)[^/?#]+", a["href"])), "")
    return {"portal": "hpb", "portal_url": url, "cid": "hpb:" + SALON.match(url).group(1), "name": name, "yomi": yomi,
            "opened": opened_month(soup.get_text(" ", strip=True)), "facebook_portal": fb,
            "address": info.get("住所", ""), "industry": "美容室",
            "portal_reviews": int(m.group(1).replace(",", "")) if m else None,
            "portal_star": float(pt.get_text(strip=True)) if pt and re.match(r"^[0-9.]+$", pt.get_text(strip=True)) else None,
            "portal_info": info, "instagram_portal": ig}


TBL_KEYS = ("ジャンル", "予約・お問い合わせ", "住所", "営業時間", "定休日", "予算", "席数", "ホームページ", "公式アカウント", "オープン日")
# 食べログのジャンル → うちの業種（DM の冒頭・順番に使う）
TBL_IND = (("ラーメン", "ラーメン"), ("つけ麺", "ラーメン"), ("焼肉", "焼肉"), ("ホルモン", "焼肉"), ("寿司", "寿司"), ("鮨", "寿司"),
           ("居酒屋", "居酒屋"), ("焼き鳥", "居酒屋"), ("バー", "居酒屋"), ("カフェ", "カフェ"), ("喫茶", "カフェ"))


def parse_tabelog(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    info = {}
    for th in soup.find_all("th"):
        k = th.get_text(" ", strip=True)
        if k in TBL_KEYS and k not in info:
            td = th.find_next_sibling("td")
            if td:
                info[k] = re.sub(r"\s+", " ", td.get_text(" ", strip=True)).replace("大きな地図を見る 周辺のお店を探す", "").strip()[:300]
                if k == "公式アカウント":
                    info["_links"] = [a["href"] for a in td.find_all("a", href=True)]
    dn = soup.select_one("h2.display-name")
    name = dn.get_text(" ", strip=True) if dn else soup.title.get_text().split("（")[0]
    sc = soup.select_one(".rdheader-rating__score-val-dtl")
    rv = soup.select_one(".rdheader-rating__review-target em")
    ig = next((f"https://www.instagram.com/{m.group(1)}/" for h in info.get("_links", [])
               for m in [re.match(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{2,30})", h)] if m), "")
    genre = info.get("ジャンル", "")
    fb = next((h for h in info.get("_links", []) if "facebook.com" in h), "")
    om = re.search(r"(20\d{2})年\s*(\d{1,2})月", info.get("オープン日", ""))
    ind = next((v for k, v in TBL_IND if k in genre), "飲食")
    return {"portal": "tabelog", "portal_url": url, "cid": "tbl:" + TBL.match(url).group(1), "name": name, "yomi": (info.get("店名") or ""),
            "address": info.get("住所", "").replace(" ", ""), "industry": ind, "genre": genre,
            "portal_reviews": int(rv.get_text(strip=True).replace(",", "")) if rv and rv.get_text(strip=True).replace(",", "").isdigit() else None,
            "portal_star": float(sc.get_text(strip=True)) if sc and re.match(r"^[0-9.]+$", sc.get_text(strip=True)) else None,
            "portal_info": {k: v for k, v in info.items() if not k.startswith("_")}, "instagram_portal": ig,
            "website_portal": info.get("ホームページ", "") if info.get("ホームページ", "").startswith("http") else "",
            "opened": f"{om.group(1)}-{int(om.group(2)):02d}" if om else "", "facebook_portal": fb}


PLACES_DAY = int(os.getenv("PORTAL_PLACES_DAY", "30"))   # 1日に使ってよい Google 店検索（Cloud の割り当ては1日100回を営業の在庫・LP の店名検索と共有。10/31 に使い切った）
_USED = os.path.join(HERE, "data", "leads", "places_used.json")


def places_take(exhausted: bool = False) -> bool:
    """今日の分が残っていれば1回分使って True。exhausted=True で今日はもう使わない"""
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        d = json.load(open(_USED, encoding="utf-8"))
    except Exception:
        d = {}
    n = d.get(today, 0)
    if exhausted:
        d = {today: 10 ** 6}
    elif n >= PLACES_DAY:
        return False
    else:
        d = {today: n + 1}
    os.makedirs(os.path.dirname(_USED), exist_ok=True)
    json.dump(d, open(_USED, "w", encoding="utf-8"))
    return not exhausted


def google(name: str, address: str, yomi: str = "") -> dict:
    """同じ店の Google マップ（店名＋住所で1件目。店名の頭が合わなければ使わない）"""
    key = getattr(config, "GOOGLE_MAPS_API_KEY", "") or os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not key or not places_take():
        return {"g_skip": "今日の Google 店検索の割り当てを使い切った（LP の店名検索の分を残す）"}
    r = requests.post(meo_observe._SEARCH_URL, json={"textQuery": f"{name} {address}", "languageCode": "ja", "maxResultCount": 1},
                      headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": meo_observe._FIELDS}, timeout=20).json()
    if (r.get("error") or {}).get("code") == 429:
        places_take(exhausted=True)
        return {"g_skip": "Google の1日の割り当て切れ（429）"}
    places = r.get("places") or []
    if not places:
        return {}
    p = places[0]
    gname = (p.get("displayName") or {}).get("text", "")
    def norm(x):
        x = unicodedata.normalize("NFKC", x or "")
        return re.sub(r"[\s・･\-－_.,'’&＆]", "", x or "").lower()
    a, b = norm(name), norm(gname)
    paren = re.search(r"[（(]([^）)]+)[）)]\s*$", yomi or "")
    alts = [a, norm(paren.group(1)) if paren else "", norm(re.sub(r"[（(].*", "", yomi or ""))]
    if not any(x[:3] and (x[:3] in b or (len(b) >= 3 and b[:3] in x)) for x in alts if x):
        return {"g_mismatch": gname}   # 別の店に当たった時は Google の数字を使わない
    o = meo_observe.from_place(p)
    days = []
    for rv in p.get("reviews") or []:   # 返ってくる口コミ（最大5件・関連の高い順）の日付
        try:
            days.append((datetime.now() - datetime.strptime(rv["publishTime"][:10], "%Y-%m-%d")).days)
        except Exception:
            pass
    return {"g_last_review_days": min(days) if days else None, "g_recent90": sum(1 for d in days if d <= 90),
            "g_photos": len(p.get("photos") or []), "g_name": gname, "g_reviews": o.get("review_count") or 0,   # 口コミ0件の店は件数の欄そのものが返らない（10/31 HALO ひばりヶ丘） "g_star": o.get("rating"), "website": o.get("website_url") or "",
            "place_id": p.get("id", ""), "g_address": p.get("formattedAddress", ""), "phone": p.get("nationalPhoneNumber", ""),
            "maps": f"https://www.google.com/maps/place/?q=place_id:{p.get('id', '')}", "category": o.get("primary_category") or ""}


def site(url: str) -> dict:
    if not url or any(h in url for h in ("instagram.com", "hotpepper.jp")):
        return {"instagram": url if "instagram.com" in (url or "") else "", "facebook": "", "emails": [], "email_pages": [], "no_sales": False}
    import list_build   # 送る時と同じ検査でメールを確かめる（旧 lead_harvest.enrich_site はページの「〇〇@〇〇」を全部拾っていた・2026-11-01）
    if list_build.site_kind(url) != "own":
        return {"instagram": "", "facebook": "", "emails": [], "email_pages": [], "no_sales": False}
    w = list_build.read_site(url)
    return {"instagram": w["instagram"], "facebook": w["facebook"], "emails": [w["email"]] if w["email"] else [],
            "email_pages": [w["email_page"]] if w["email_page"] else [], "no_sales": w["no_sales"], "form": w["form"], "hire": w["hire"]}


TABELOG_NG = "食べログは規約（6条・9条）で営業目的の利用を禁止しているので読まない（2026-11-01）"


def build(url: str) -> dict:
    k = kind_of(url)
    if k == "tabelog":
        raise ValueError(TABELOG_NG)
    s = (parse_tabelog if k == "tabelog" else parse_hpg if k == "hpg" else parse_salon)(url, get(url))
    g = google(s["name"], s["address"], s.get("yomi", ""))
    w = site(s.get("website_portal") or g.get("website", ""))
    rec = {"at": datetime.now().isoformat(timespec="seconds"), **s, **g,
           "instagram": s["instagram_portal"] or w.get("instagram", ""), "facebook": s.get("facebook_portal") or w.get("facebook", ""),
           "emails": w.get("emails", []), "email_pages": w.get("email_pages", []), "no_sales": w.get("no_sales", False)}
    city = re.search(r"(東京都|北海道|(?:京都|大阪)府|.{2,3}県)(.+?[市区町村])", s["address"])
    rec["city"] = city.group(2) if city else ""
    rec["website_is_portal"] = any(h in (g.get("website") or "") for h in ("hotpepper.jp", "tabelog.com"))   # Googleマップのウェブサイト欄が予約サイト＝地図から来た人も予約サイト経由
    web = s.get("website_portal") or g.get("website", "") or ""
    rec["site_kind"] = ("none" if not web else "portal" if rec["website_is_portal"]
                        else "sns" if any(h in web for h in ("instagram.com", "facebook.com", "ameblo.jp", "lit.link", "linktr.ee"))
                        else "own")   # 自分の HP があるか（2026-10-31）
    if not rec["instagram"]:
        rec["instagram"], rec["instagram_from"] = find_instagram(s["name"], rec["city"], s.get("yomi", ""), s["industry"]), "search"
    if not rec["emails"] and not rec["instagram"] and not rec["facebook"]:   # メールも Instagram も無い店は Facebook のページを探す（会長 10/31）
        rec["facebook"], rec["facebook_from"] = find_profile(s["name"], rec["city"], s.get("yomi", ""), s["industry"], "facebook"), "search"
    return rec


def find_instagram(name: str, city: str, yomi: str = "", industry: str = "") -> str:
    return find_profile(name, city, yomi, industry, "instagram")


def base_name(name: str) -> str:
    """検索用の店名（「新宿店」「本店」などの支店名・後ろの飾りを外す）"""
    t = re.sub(r"[【\[（(].*?[】\]）)]", " ", unicodedata.normalize("NFKC", name or ""))
    toks = [w for w in re.split(r"\s+", t) if w]
    keep = []
    for w in toks:
        if keep and (w.endswith("店") or w in ("韓国", "本店")):
            break
        keep.append(w)
    return " ".join(keep) or (name or "")


def find_profile(name: str, city: str, yomi: str = "", industry: str = "", sns: str = "instagram") -> str:
    """検索（DuckDuckGo）で instagram.com／facebook.com の店のページを1つ（2026-10-31: site: で探す・名前が一番近い物）。
    名前がアカウント名か見出しに入っている物だけ（違う店を拾わない）。スタッフ個人より店の名前そのものに近い物を選ぶ"""
    host = "instagram" if sns == "instagram" else "facebook"
    bn = base_name(name)
    def norm(x):
        return re.sub(r"[\s・･\-－_.,'’&＆]", "", unicodedata.normalize("NFKC", x or "")).lower()
    paren = re.search(r"[（(]([^）)]+)[）)]\s*$", yomi or "")
    keys = [k for k in (norm(bn), norm(paren.group(1)) if paren else "") if len(k) >= 3]
    if not keys:
        return ""
    res = []
    try:
        from ddgs import DDGS
        with DDGS() as d:
            for q in (f"site:{host}.com {bn} {city}", f"site:{host}.com {bn} {industry}", f"{bn} {city} {industry} {host}"):
                try:
                    res += list(d.text(q, max_results=8))
                except Exception:
                    pass
                if any(host + ".com/" in (r.get("href") or "") for r in res):
                    break
    except Exception:
        return ""
    best = None
    for r in res:
        m = re.match(rf"https?://(?:www\.|[a-z]{{2}}-[a-z]{{2}}\.|m\.)?{host}\.com/([A-Za-z0-9._\-]{{2,60}})/?(?:[?#].*)?$", r.get("href", ""))
        if not m or m.group(1).lower() in ("p", "reel", "reels", "explore", "accounts", "stories", "groups", "events", "watch", "share", "people", "profile.php", "help", "about", "legal"):
            continue
        h = norm(m.group(1))
        hay = norm(r.get("title", "")) + h
        if not any(k[:6] in hay for k in keys):
            continue
        dist = 0 if any(k[:6] in h for k in keys) else 1        # アカウント名そのものに店名がある方を先に
        cand = (dist, len(h), m.group(1))
        best = min(best, cand) if best else cand
    return f"https://www.{host}.com/{best[2]}/" if best else ""


def area_word(rec: dict) -> str:
    """お客さんが打つ地名（アクセス欄の最初の駅名。無ければ市区町村から「市」「区」を外した名前）"""
    info = rec.get("portal_info") or {}
    acc = unicodedata.normalize("NFKC", " ".join(str(v) for k, v in info.items() if "アクセス" in k) + " " + str(info.get("最寄り駅", "")))
    m = re.search(r"(?:JR|東京メトロ|都営|西武|東武|京王|小田急|東急|京急|京成|つくばエクスプレス|地下鉄)?[^\s「」『』、。/・（()）]*?「?([^\s「」『』、。/・（()）]{1,8}?)」?駅", acc)
    if m and m.group(1) not in ("各", "最寄", "最寄り"):
        st = re.sub(r"^.*(線|ライン|】|』|」|案内|腺)", "", m.group(1))   # 「西武池袋線練馬」「東武スカイツリーライン越谷」→ 駅名だけ
        for _ in range(3):   # 「◎JR新宿」のように前の飾りが重なる
            st = re.sub(r"^[^\w一-龥ぁ-んァ-ヶ]+|^(JR|東京メトロ|都営|西武|東武|京王|小田急|東急|京急|京成|地下鉄|メトロ|の)", "", st)
        if st and not re.search(r"から|分|\d+分|徒歩|各|最寄", st):
            return st
    city = rec.get("city") or ""
    return re.sub(r"[市区町村]$", "", city) if len(city) > 2 else city


def search_word(rec: dict) -> str:
    """業種の言葉（美容室・ネイルサロン…／飲食はジャンルの最初の語）"""
    if rec.get("portal") in ("hpg", "tabelog"):
        g = re.split(r"[、,・/／\s]", rec.get("genre") or "")[0]
        return g or "居酒屋"
    return rec.get("industry") or "美容室"


def search_rank(rec: dict) -> dict:
    """「<駅名> <業種>」で Google の文字検索（最大20店）を1回。その店が何番目か・上10店の口コミの平均（2026-10-31 会長 案A）。
    20店の中にいなければ g_rank=0。割り当てが無ければ {}"""
    key = getattr(config, "GOOGLE_MAPS_API_KEY", "") or os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not key or not rec.get("place_id") or not places_take():
        return {}
    q = f"{area_word(rec)} {search_word(rec)}"
    r = requests.post(meo_observe._SEARCH_URL, json={"textQuery": q, "languageCode": "ja", "maxResultCount": 20},
                      headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": "places.id,places.userRatingCount"}, timeout=20).json()
    if (r.get("error") or {}).get("code") == 429:
        places_take(exhausted=True)
        return {}
    ps = r.get("places") or []
    ids = [p.get("id") for p in ps]
    top = [int(p.get("userRatingCount") or 0) for p in ps if p.get("id") != rec["place_id"]][:10]
    return {"g_rank": ids.index(rec["place_id"]) + 1 if rec["place_id"] in ids else 0, "g_rank_query": q,
            "g_rank_total": len(ps), "g_top10_avg": round(sum(top) / len(top)) if top else None,
            "g_rank_at": datetime.now().strftime("%Y-%m-%d")}


def rank_candidates(n: int = 20) -> None:
    """送る候補（sales-automation の need_hypo で外れなかった店・点の高い順）の検索順位を、今日の割り当ての範囲で測る"""
    from src import need_hypo
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8") if l.strip()]
    todo = [(r, j) for r, j in need_hypo.judge_many([r for r in rows if r.get("portal_rank")]) if not j["exclude"] and r.get("place_id") and "g_rank" not in r]
    todo.sort(key=lambda x: -x[1]["score"])
    done = 0
    for r, _ in todo[:n]:
        g = search_rank(r)
        if not g:
            break
        r.update(g)
        done += 1
        print(f"[RANK] {r['name'][:20]}｜「{g['g_rank_query']}」{g['g_rank'] or '20番目までに無し'}・上10店の口コミ平均 {g['g_top10_avg']}")
    open(OUT, "w", encoding="utf-8").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows))
    print(f"[RANK] {done}店を測りました・残り {max(0, len(todo) - done)}店")


def refresh_google() -> None:
    """Google で照合できなかった行（割り当て切れ）だけ、今日の分の範囲で照合し直す（2026-10-31）。
    HP・メール・Instagram もその Google の結果から読み直す"""
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8") if l.strip()]
    done = 0
    for rec in rows:
        if rec.get("place_id") or rec.get("g_mismatch"):
            continue
        g = google(rec["name"], rec.get("address", ""), rec.get("yomi", ""))
        if g.get("g_skip"):
            break
        rec.update(g)
        rec.pop("g_skip", None)
        if g.get("website") and not rec.get("emails"):
            w = site(g["website"])
            rec["emails"] = w.get("emails", [])
            rec["instagram"] = rec.get("instagram") or w.get("instagram", "")
            rec["facebook"] = rec.get("facebook") or w.get("facebook", "")
            rec["no_sales"] = w.get("no_sales", False)
        rec["website_is_portal"] = any(h in (g.get("website") or "") for h in ("hotpepper.jp", "tabelog.com"))
        web = rec.get("website_portal") or g.get("website", "") or ""
        rec["site_kind"] = ("none" if not web else "portal" if rec["website_is_portal"]
                            else "sns" if any(h in web for h in ("instagram.com", "facebook.com", "ameblo.jp", "lit.link", "linktr.ee")) else "own")
        done += 1
    open(OUT, "w", encoding="utf-8").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    left = sum(1 for r in rows if not r.get("place_id") and not r.get("g_mismatch"))
    print(f"[PORTAL] Google 照合し直し {done}店・残り {left}店")


def main():
    if "--refresh-google" in sys.argv:
        return refresh_google()
    if "--rank" in sys.argv:   # 送る候補の Google 検索の順位（案A の1行目の数字）
        return rank_candidates(int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 20)
    list_url = sys.argv[1]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 10
    pages = int(sys.argv[sys.argv.index("--pages") + 1]) if "--pages" in sys.argv else 3
    start = int(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 1   # 都心の1〜2ページ目は人気店ばかり（10/31 新宿で確認）
    skip_top = int(sys.argv[sys.argv.index("--skip-top") + 1]) if "--skip-top" in sys.argv else 10   # 予約サイトで上位10の店は困っていない（会長 10/31）
    have = set()
    if os.path.exists(OUT):
        have = {json.loads(l)["cid"] for l in open(OUT, encoding="utf-8") if l.strip()}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    got = 0
    new_only = "--new-only" in sys.argv   # 一覧で「NEW OPEN」と書いてある店だけ（開業したばかり・H9）
    for u, rank in ranked_urls(list_url, pages, start, new_only):
        if rank <= skip_top:
            continue
        k = kind_of(u)
        cid = "tbl:" + TBL.match(u).group(1) if k == "tabelog" else "hpg:" + HPG.match(u).group(1) if k == "hpg" else "hpb:" + SALON.match(u).group(1)
        if cid in have:
            continue
        try:
            rec = build(u)
        except Exception as e:
            print(f"[PORTAL] 失敗 {u}: {e}"); continue
        rec["portal_rank"], rec["portal_list"] = rank, list_url
        if new_only:
            rec["new_open_card"] = True
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        got += 1
        print(f"[PORTAL] {rec['portal']} {rank}番目 {rec['name']}｜口コミ {rec['portal_reviews']}件・Google {rec.get('g_reviews')}件"
              f"（最新 {rec.get('g_last_review_days')}日前）｜HP {rec['site_kind']}・IG {bool(rec['instagram'])}・FB {bool(rec['facebook'])}・メール {len(rec['emails'])}")
        if got >= n:
            break
    print(f"[PORTAL] {got}店を {OUT} に足しました")


if __name__ == "__main__":
    main()
