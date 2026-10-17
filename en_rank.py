# -*- coding: utf-8 -*-
"""店1軒の「日本語で調べた位置」と「英語で調べた位置」（2026-10-13・会長承認の提案2）。
LINE で店主が「英語の順位」を頼む → Railway が会話状態（Notion「💬 MEO LINE 状態」）に en_req を置く
→ この Mac の en_rank_watch.py が拾ってここで調べ、LINE で結果を返す。
実行（手で1軒）: python3 en_rank.py "たから寿司 京都市右京区" 寿司
調べ方は調査（frame_inbound.py）と同じ: Googleマップの一覧を60位まで。ログインした Chrome（GMAPS_PROFILE）で読む。
"""
from __future__ import annotations
import json, os, re, statistics as st, sys, time
from common import accept_consent, blocked, browser, sync_playwright
from frame_inbound import parse_card

TOPN = 60
IND_EN = {"ラーメン": "ramen", "寿司": "sushi", "居酒屋": "izakaya", "カフェ": "cafe", "焼肉": "yakiniku", "マッサージ": "massage",
          "そば": "soba", "うどん": "udon", "天ぷら": "tempura", "定食": "japanese restaurant", "和食": "japanese restaurant",
          "とんかつ": "tonkatsu", "お好み焼き": "okonomiyaki", "バー": "bar", "パン": "bakery", "整体": "massage", "その他": "restaurant"}
PREF = r"(Hokkaido|Aomori|Iwate|Miyagi|Akita|Yamagata|Fukushima|Ibaraki|Tochigi|Gunma|Saitama|Chiba|Tokyo|Kanagawa|Niigata|Toyama|Ishikawa|Fukui|Yamanashi|Nagano|Gifu|Shizuoka|Aichi|Mie|Shiga|Kyoto|Osaka|Hyogo|Nara|Wakayama|Tottori|Shimane|Okayama|Hiroshima|Yamaguchi|Tokushima|Kagawa|Ehime|Kochi|Fukuoka|Saga|Nagasaki|Kumamoto|Oita|Miyazaki|Kagoshima|Okinawa)"


def _goto(pg, url):
    for att in range(3):
        try:
            pg.goto(url, wait_until="commit", timeout=25000); return
        except Exception:
            if att == 2:
                raise
            time.sleep(5 + 5 * att)


def area_from_address(addr: str) -> str:
    """英語の住所（〒616-0016 Kyoto, Nishikyo Ward, Arashiyama Kamikaidocho, 74-8 …）から、旅行者が打つ町の名前を取る。
    政令市の区なら区の次の地名の頭（Arashiyama）、それ以外は市町村（Takayama）。"""
    parts = [x.strip() for x in addr.split(",") if x.strip()]
    loc = _tokyo_locality(parts)
    if loc:
        return loc
    for i, ptx in enumerate(parts):
        if re.search(PREF, ptx):
            if re.search(PREF + r"\s+\d{3}-?\d{4}", ptx) and i > 0:   # 英語式の並び（…, Takayama, Gifu 506-0846, Japan）
                return re.sub(r"\s+(City|Town|Village|District)$", "", parts[i - 1]).strip()
            rest = parts[i + 1:]
            if not rest:
                return ""
            if rest[0].endswith("Ward") and len(rest) > 1:
                return rest[1].split()[0]
            return re.sub(r"\s+(City|Town|Village|District)$", "", rest[0]).strip()
    return ""


def _tokyo_locality(parts: list[str]) -> str:
    """東京都の区以外の市（武蔵野市など）は、旅行者は駅の町の名前で探す（Kichijoji Honcho → Kichijoji・2026-10-17）。"""
    if not any(re.search(r"\bTokyo\b", x) for x in parts) or any(x.endswith("City") and "Tokyo" in x for x in parts) or any("Ward" in x or re.search(r"\b(Chiyoda|Chuo|Minato|Shinjuku|Bunkyo|Taito|Sumida|Koto|Shinagawa|Meguro|Ota|Setagaya|Shibuya|Nakano|Suginami|Toshima|Kita|Arakawa|Itabashi|Nerima|Adachi|Katsushika|Edogawa)\b", x) for x in parts):
        return ""
    for x in parts:
        if re.search(PREF, x) or x == "Japan":
            continue
        words = [w for w in x.split() if not re.search(r"[\d−-]", w) and w not in ("Chome",)]
        if not words:
            continue
        w = words[0]
        m = re.match(r"^([A-Z][a-z]+?)(honcho|minamicho|kitamachi|higashicho|nishicho|kitacho)?$", w)
        if m and len(m.group(1)) >= 4 and (m.group(2) or (len(words) > 1 and words[1].lower() in ("honcho", "minamicho", "kitamachi", "higashicho", "nishicho"))):
            return m.group(1)
    return ""


def find_shop(pg, text: str) -> dict:
    """英語の画面で店を1軒に決める（cid・英語の店名・英語の住所から市の名前）。"""
    if text.startswith("http"):   # 無料点検で送られた Googleマップのリンク（短い URL は開いてから英語の画面へ）
        _goto(pg, text); accept_consent(pg)
        for _ in range(20):
            if "/maps/" in pg.url and "goo.gl" not in pg.url:
                break
            time.sleep(0.5)
        u = re.sub(r"([?&])hl=[a-z-]+", "", pg.url)
        _goto(pg, u + ("&" if "?" in u else "?") + "hl=en")
    else:
        _goto(pg, "https://www.google.com/maps/search/" + text + "?hl=en")
    accept_consent(pg)
    for _ in range(20):
        if "/maps/place/" in pg.url or pg.locator("div[role='feed']").count():
            break
        time.sleep(0.5)
    if "/maps/place/" not in pg.url:
        a = pg.locator("div[role='feed'] a[href*='/maps/place/']")
        if not a.count():
            return {}
        a.first.click(); time.sleep(3)
    for _ in range(20):
        if pg.locator("h1").count():
            break
        time.sleep(0.5)
    m = re.search(r"!1s(0x[0-9a-f]+:0x[0-9a-f]+)", pg.url) or re.search(r"(0x[0-9a-f]+:0x[0-9a-f]+)", pg.content())
    addr = ""
    b = pg.locator("button[data-item-id='address']")
    if b.count():
        addr = (b.first.get_attribute("aria-label") or "").replace("Address:", "").strip()
    city = area_from_address(addr)
    name = pg.locator("h1").first.inner_text().strip() if pg.locator("h1").count() else ""
    return {"cid": m.group(1) if m else None, "name_en": name, "address_en": addr, "city_en": city}


def ranks(pg, q: str, lang: str) -> list[dict]:
    _goto(pg, "https://www.google.com/maps/search/" + q + f"?hl={lang}")
    accept_consent(pg)
    if blocked(pg):
        raise RuntimeError("blocked")
    pg.wait_for_selector("div[role='feed']", timeout=25000)
    feed = pg.locator("div[role='feed']")
    last, still = -1, 0
    for _ in range(TOPN // 5 + 4):
        feed.evaluate("el => el.scrollBy(0, 5000)"); time.sleep(1.2)
        cnt = pg.locator("div[role='feed'] a[href*='/maps/place/']").count()
        if cnt >= TOPN:
            break
        still = still + 1 if cnt == last else 0
        if still >= 2:
            break
        last = cnt
    items = pg.locator("div[role='feed'] a[href*='/maps/place/']")
    out = []
    for i in range(min(items.count(), TOPN)):
        try:
            r = parse_card(items.nth(i), lang); r["rank"] = i + 1; out.append(r)
        except Exception:
            pass
    return out


def report(text: str, industry: str, town_ja: str = "") -> dict:
    """text = 店名＋市町村名（または Googleマップのリンク）。industry = 業種（日本語）。"""
    town_ja = town_ja or (text.split()[-1] if len(text.split()) > 1 else "")
    with sync_playwright() as p:
        b, ctx = browser(p)
        pg = ctx.new_page()
        try:
            shop = find_shop(pg, text)
            if not shop.get("cid"):
                return {"ok": False, "why": "お店が見つからない"}
            en_q = f"{IND_EN.get(industry, 'restaurant')} {shop['city_en']}" if shop['city_en'] else f"{IND_EN.get(industry, 'restaurant')} {town_ja}"
            ja_q = f"{industry} {town_ja or shop['city_en']}"
            ja = ranks(pg, ja_q, "ja"); time.sleep(2)
            en = ranks(pg, en_q, "en")
        finally:
            b.close()
    pos = lambda lst: next((r["rank"] for r in lst if r.get("cid") == shop["cid"]), None)
    top10 = [r["reviews"] for r in en[:10] if r.get("reviews")]
    return {"ok": True, **shop, "ja_query": ja_q, "en_query": en_q, "rank_ja": pos(ja), "rank_en": pos(en),
            "n_ja": len(ja), "n_en": len(en), "en_top10_reviews_median": st.median(top10) if top10 else None,
            "at": time.strftime("%Y-%m-%d %H:%M")}


def message(r: dict, shop_label: str) -> str:
    """LINE で返す文（店主向け・弱気な断りなし・AIの語なし）。"""
    if not r.get("ok"):
        return ("お店をGoogleマップで見つけられませんでした。\nGoogleマップのお店のページの「共有」からリンクをコピーして、このLINEに送ってください。")
    def where(k, n):
        if k:
            return f"{k}番目"
        return f"{n}位までに出てきません" if n >= 20 else f"一覧に出てくるのは{n}軒だけで、その中に入っていません"
    ja, en = where(r["rank_ja"], r["n_ja"]), where(r["rank_en"], r["n_en"])
    lines = [f"{shop_label}を調べました。", "",
             f"日本語で「{r['ja_query']}」と調べると：{ja}",
             f"英語で「{r['en_query']}」と調べると：{en}", ""]
    if r["rank_ja"] and (not r["rank_en"] or r["rank_en"] > 10) and r["rank_ja"] <= 20:
        lines.append("日本語では見つけてもらえているのに、英語で探す旅行者の画面には、まだ届いていません。")
    elif r["rank_en"] and r["rank_en"] <= 10:
        lines.append("英語で探す旅行者の画面でも、上位に出ています。この位置を保つことが次の一歩です。")
    else:
        lines.append("英語で探す旅行者の画面は、これから上の席を取りにいける状態です。")
    if r.get("en_top10_reviews_median"):
        lines.append(f"英語の画面で上位10に入っているお店の口コミは、中央値{int(r['en_top10_reviews_median'])}件でした。")
    lines += ["", "英語を話さずに、旅行者の画面で上に出る手順は「note」と送ると届きます。任せたいときは「プランを見る」と送ってください。",
              f"※{r['at']}に調べた位置です。検索のたびに少し動きます。"]
    return "\n".join(lines)


if __name__ == "__main__":
    os.environ.setdefault("GMAPS_PROFILE", os.path.expanduser("~/meo-research/.gprofile"))
    r = report(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "その他")
    print(json.dumps(r, ensure_ascii=False, indent=1)); print(message(r, "お店"))
