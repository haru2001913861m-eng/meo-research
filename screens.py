# -*- coding: utf-8 -*-
"""無料点検の残り2つの画面（英語の地図・AI）を Mac で実際に調べて、LINE の文にする（会長 2026-10-17「実際に聞く版で」）。

① 日本語の地図 … Railway が18項目で返し済み
② 英語の地図   … 英語の画面で店を開き（英字の店名・英語の住所から町）、日本語と英語で一覧を60位まで読んで位置を出す（en_rank と同じ）
③ AI           … ChatGPT（ウェブ検索つき）に日本語と英語で1回ずつ「この町のおすすめ」を聞き、店が出たか（ai_ask・調査と同じ聞き方）
ChatGPT に聞けない時（残高・上限）は、調査の数字（地図の上位10は12%・11位以下は4%）と店の条件で返す（聞かない版）。
実行（手で1軒）: python3 screens.py "https://maps.app.goo.gl/..."  または  python3 screens.py "山田食堂 吉祥寺"
"""
from __future__ import annotations
import json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("GMAPS_PROFILE", os.path.join(HERE, ".gprofile"))
import ai_ask, en_rank  # noqa: E402
from common import accept_consent, browser, sync_playwright  # noqa: E402

IND_WORDS = [("ラーメン", "ラーメン"), ("寿司", "寿司"), ("すし", "寿司"), ("居酒屋", "居酒屋"), ("カフェ", "カフェ"), ("喫茶", "カフェ"),
             ("焼肉", "焼肉"), ("そば", "そば"), ("蕎麦", "そば"), ("うどん", "うどん"), ("天ぷら", "天ぷら"), ("とんかつ", "とんかつ"),
             ("焼き鳥", "焼き鳥"), ("焼鳥", "焼き鳥"), ("和食", "和食"), ("日本料理", "和食"), ("定食", "和食"), ("イタリア", "イタリアン"),
             ("中華", "中華"), ("カレー", "カレー"), ("バー", "バー"), ("パン", "パン屋"), ("美容", "美容室"), ("ヘア", "美容室"),
             ("ネイル", "ネイルサロン"), ("整体", "整体"), ("マッサージ", "マッサージ"), ("鍼", "整体"), ("整骨", "整体"), ("接骨", "整体")]


def ind_word(cat: str) -> str:
    for k, w in IND_WORDS:
        if k in (cat or ""):
            return w
    return re.sub(r"(店|屋)$", "", (cat or "").split("・")[0]) or "お店"


def area_from_ja(addr: str) -> str:
    """日本語の住所から検索で打つ町（政令市は「京都市右京区」、それ以外は「松本市」）。"""
    a = re.sub(r"^.*?〒?\d{3}-?\d{4}\s*", "", addr or "").replace("住所:", "").strip()
    a = re.sub(r"^(東京都|北海道|(?:京都|大阪)府|.{2,3}県)", "", a)
    m = re.match(r"(.+?市.+?区|.+?区|.+?市|.+?郡.+?[町村]|.+?[町村])", a)
    return m.group(1) if m else a[:8]


def ja_profile(pg, url_ja: str) -> dict:
    en_rank._goto(pg, url_ja)
    accept_consent(pg)
    for _ in range(20):
        if pg.locator("h1").count():
            break
        time.sleep(0.5)
    name = pg.locator("h1").first.inner_text().strip() if pg.locator("h1").count() else ""
    cat = ""
    b = pg.locator("button[jsaction*='category']")
    if b.count():
        cat = b.first.inner_text().strip()
    addr = ""
    b = pg.locator("button[data-item-id='address']")
    if b.count():
        addr = (b.first.get_attribute("aria-label") or "").replace("住所:", "").strip()
    return {"name_ja": name, "category_ja": cat, "address_ja": addr}


def check(text: str, industry_hint: str = "", langs=("ja", "en"), runs: int = 1, who: str = "") -> dict:
    with sync_playwright() as p:
        b, ctx = browser(p)
        pg = ctx.new_page()
        try:
            shop = en_rank.find_shop(pg, text)
            if not shop.get("cid"):
                return {"ok": False, "why": "お店が見つからない"}
            url_ja = re.sub(r"([?&])hl=en", r"\1hl=ja", pg.url) if "hl=en" in pg.url else pg.url + ("&" if "?" in pg.url else "?") + "hl=ja"
            ja = ja_profile(pg, url_ja)
            ind = ind_word(industry_hint or ja["category_ja"])
            town = text.split()[-1] if (not text.startswith("http") and len(text.split()) > 1) else area_from_ja(ja["address_ja"])
            ja_q = f"{ind} {town}"
            en_ind = ai_ask.ind4(ind)[1].replace(" shops", "").replace(" restaurants", "").replace(" places", "").replace("izakaya", "izakaya")
            en_ind = {"cafes": "cafe", "bars": "bar", "bakeries": "bakery", "hair salons": "hair salon", "nail salons": "nail salon", "restaurants": "restaurant"}.get(en_ind, en_ind)
            en_q = f"{en_ind} {shop['city_en'] or town}"
            r_ja = en_rank.ranks(pg, ja_q, "ja"); time.sleep(2)
            r_en = en_rank.ranks(pg, en_q, "en")
        finally:
            b.close()
    pos = lambda lst: next((r["rank"] for r in lst if r.get("cid") == shop["cid"]), None)
    me_ja = next((r for r in r_ja if r.get("cid") == shop["cid"]), {})
    top10 = [r["reviews"] for r in r_en[:10] if r.get("reviews")]
    out = {"ok": True, **shop, **ja, "industry": ind, "town": town, "ja_query": ja_q, "en_query": en_q,
           "rank_ja": pos(r_ja), "rank_en": pos(r_en), "n_ja": len(r_ja), "n_en": len(r_en),
           "reviews": me_ja.get("reviews"), "rating": me_ja.get("rating"),
           "en_top10_reviews_median": sorted(top10)[len(top10) // 2] if top10 else None, "at": time.strftime("%Y-%m-%d %H:%M")}
    out["ai"] = ai_ask.check(ja["name_ja"], shop.get("name_en", ""), town, shop.get("city_en", ""), ind, langs, runs, who)
    return out


def _where(k, n):
    if k:
        return f"{k}番目"
    return f"{n}番目までに出てきません" if n >= 20 else f"一覧に出るのは{n}軒で、その中に入っていません"


def message(r: dict, label: str) -> str:
    """LINE の1通（②英語の地図 ③AI → 次の一歩）。順位の約束・弱気な断りは書かない。"""
    if not r.get("ok"):
        return ("②英語の地図と③AIの点検で、お店をGoogleマップで見つけられませんでした。\n"
                "Googleマップのお店のページの「共有」からリンクをコピーして、このLINEに送ってください。")
    L = [f"【3つの画面の点検】{label}", "",
         "② 英語の地図（外国のお客さんの画面）",
         f"・日本語「{r['ja_query']}」：{_where(r['rank_ja'], r['n_ja'])}",
         f"・英語「{r['en_query']}」：{_where(r['rank_en'], r['n_en'])}"]
    if r.get("name_en") and not re.search(r"[A-Za-z]{3,}", r["name_en"]):
        L.append("・英語の画面で、店名が英字になっていません（旅行者が読めない名前で並んでいます）")
    if r["rank_ja"] and r["rank_ja"] <= 20 and (not r["rank_en"] or r["rank_en"] > 10):
        L.append("・日本語では見つけてもらえているのに、英語で探す旅行者の画面には届いていません。日本語で上位10の店の約半分が、英語では上位10から消えていました（観光地688軒中335軒）")
    if r.get("en_top10_reviews_median"):
        L.append(f"・英語の画面で上位10の店の口コミは、中央値{int(r['en_top10_reviews_median'])}件")
    L += ["", "③ AI（ChatGPT）"]
    a = r.get("ai") or {}
    if a.get("ok"):
        L.append(f"「{r['town']}でおすすめの{r['industry']}を5つ」と、日本語と英語で聞きました。")
        for lg, v in (a.get("by_lang") or {}).items():
            L.append(f"・{ai_ask_lang(lg)}で聞くと：" + ("あなたのお店が出ました" if v["hit"] else "あなたのお店は出ませんでした"))
        if a.get("sources"):
            L.append("・答えに使われたサイト：" + "、".join(d for d, _ in a["sources"][:4]))
        L.append("・ChatGPTの出典の1位は食べログ（126回）、Googleマップは0回でした（4言語で75回・533店）。食べログと公式サイトをGoogleマップと同じにそろえるのが近道です")
    else:
        top = r["rank_ja"] and r["rank_ja"] <= 10
        many = (r.get("reviews") or 0) >= 50
        L += [f"・日本語の地図で上位10：{'はい' if top else 'いいえ'}（上位10の店はChatGPTに12%の割合で出て、11位以下は4%）",
              f"・口コミ50件以上：{'はい' if many else 'いいえ'}（50件以上の店は7%、50件未満は4%）",
              "・ChatGPTの出典の1位は食べログ（126回）、Googleマップは0回。食べログと公式サイトをGoogleマップと同じにそろえるのが近道です"]
    L += ["", "英語の地図とAIの画面まで任せるなら、スタンダード（月¥29,800）。英語の口コミへの英語の返信・英字の店名・食べログのそろえ表・毎月ChatGPTに聞いて出た回数の報告まで、こちらでやります。",
          "「プランを見る」と送ると、3つのプランの違いが並びます。自分でやるなら「note」と送ってください。",
          f"※{r['at']}に調べた結果です。地図の位置もAIの答えも、調べるたびに少し動きます。"]
    return "\n".join(L)


def ai_ask_lang(lg: str) -> str:
    return {"ja": "日本語", "en": "英語", "zh": "中国語", "ko": "韓国語"}.get(lg, lg)


if __name__ == "__main__":
    r = check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "", who="manual")
    print(json.dumps({k: v for k, v in r.items() if k != "ai"}, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in (r.get("ai") or {}).items() if k != "answers"}, ensure_ascii=False))
    print(message(r, "お店"))
