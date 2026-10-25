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
            try:   # ④ 投稿（お知らせ）の有無: 英語の画面では店の投稿が "From the owner" の下に出る（detail_inbound と同じ見方・2026-10-25）
                has_posts = "From the owner" in pg.inner_text("body")
            except Exception:
                has_posts = None
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
    latin10 = sum(1 for r in r_en[:10] if r.get("latin_name"))
    out = {"ok": True, **shop, **ja, "industry": ind, "town": town, "ja_query": ja_q, "en_query": en_q,
           "rank_ja": pos(r_ja), "rank_en": pos(r_en), "n_ja": len(r_ja), "n_en": len(r_en),
           "reviews": me_ja.get("reviews"), "rating": me_ja.get("rating"),
           "en_top10_reviews_median": sorted(top10)[len(top10) // 2] if top10 else None, "en_top10_latin": latin10, "en_top10_n": min(10, len(r_en)),
           "has_posts": has_posts, "at": time.strftime("%Y-%m-%d %H:%M")}
    if not en_relevant(out):   # 外国のお客さんの兆しが無い店は日本語だけで聞く（英語の話をしない）
        langs = [lg for lg in langs if lg == "ja"] or ["ja"]
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
    en = en_relevant(r)   # 外国のお客さんの兆しが無い店には英語の地図の話をしない（会長 2026-10-18「いらない提案はしない」）
    L = [f"【{'3つの画面' if en else '地図とAI'}の点検】{label}", ""]
    if en:
        L += ["② 英語の地図（外国のお客さんの画面）",
              f"・日本語「{r['ja_query']}」：{_where(r['rank_ja'], r['n_ja'])}",
              f"・英語「{r['en_query']}」：{_where(r['rank_en'], r['n_en'])}"]
    if en and r.get("name_en") and not re.search(r"[A-Za-z]{3,}", r["name_en"]):
        L.append(f"・英語の画面で、店名が英字で出ていません。この街の英語の上位10では{r.get('en_top10_latin', 0)}店が英字です（店名は Google が決めるので、サイト・SNS・予約サイトの英字のつづりをそろえて拾ってもらいます）")
    if en and r["rank_ja"] and r["rank_ja"] <= 20 and (not r["rank_en"] or r["rank_en"] > 10):
        L.append(_n().fmt("・日本語では見つけてもらえているのに、英語で探す旅行者の画面には届いていません。日本語で上位10の店の約半分が、英語では上位10から消えていました（{label:inb.ja10_n}中{n:inb.ja10_lost}軒）"))
    if en and r.get("en_top10_reviews_median"):
        L.append(f"・英語の画面で上位10の店の口コミは、中央値{int(r['en_top10_reviews_median'])}件")
    L += (["", "③ AI（ChatGPT）"] if en else ["② AI（ChatGPT）"])
    a = r.get("ai") or {}
    if a.get("ok"):
        L.append(f"「{r['town']}でおすすめの{r['industry']}を5つ」と、" + ("日本語と英語で" if en else "日本語で") + "聞きました。")
        for lg, v in (a.get("by_lang") or {}).items():
            L.append(f"・{ai_ask_lang(lg)}で聞くと：" + ("あなたのお店が出ました" if v["hit"] else "あなたのお店は出ませんでした"))
        if a.get("sources"):
            L.append("・答えに使われたサイト：" + "、".join(d for d, _ in a["sources"][:4]))
        L.append(_n().fmt("・ChatGPTの出典の1位は食べログ（{n:ai.sources_tabelog}回）、Googleマップは{n:ai.sources_gmaps}回でした（4言語で{n:ai.questions}回・{n:ai.stores}店）。食べログと公式サイトをGoogleマップと同じにそろえるのが近道です"))
    else:
        top = r["rank_ja"] and r["rank_ja"] <= 10
        many = (r.get("reviews") or 0) >= 50
        N = _n()
        L += [f"・日本語の地図で上位10：{'はい' if top else 'いいえ'}" + N.fmt("（上位10の店はChatGPTに{n:ai.top10_all}の割合で出て、11位以下は{n:ai.rest_all}）"),
              f"・口コミ50件以上：{'はい' if many else 'いいえ'}" + N.fmt("（50件以上の店は{n:ai.rv50_hi_all}、50件未満は{n:ai.rv50_lo_all}）"),
              N.fmt("・ChatGPTの出典の1位は食べログ（{n:ai.sources_tabelog}回）、Googleマップは{n:ai.sources_gmaps}回。食べログと公式サイトをGoogleマップと同じにそろえるのが近道です")]
    if r.get("has_posts") is not None:
        L += ["", ("④ 投稿（お知らせ）：あり" if r["has_posts"] else "④ 投稿（お知らせ）：なし") + _n().fmt("（出しているお店は{n:jp.post.share}。投稿のある店は口コミの増え方が約7倍でした）")]
    if os.path.exists(os.path.expanduser("~/sales-automation/src/meo_pricing.py")):   # 本番の LINE が1プランになってから新しい案内（それまでは本番の LINE と同じ言葉）
        L += ["", f"任せるなら、{_offer_line()}。" + ("英語の口コミへの英語の返信・英字の店名・" if en else "") + "食べログのそろえ表・毎月ChatGPTに聞いて出た回数の報告まで、こちらでやります。",
              "「月額と中身を見る」と送ると、中身が並びます。自分でやるなら「note」と送ってください。"]
    else:
        L += ["", "英語の地図とAIの画面まで任せるなら、スタンダード（月¥29,800）。英語の口コミへの英語の返信・英字の店名・食べログのそろえ表・毎月ChatGPTに聞いて出た回数の報告まで、こちらでやります。",
              "「プランを見る」と送ると、3つのプランの違いが並びます。自分でやるなら「note」と送ってください。"]
    L += [
          f"※{r['at']}に調べた結果です。地図の位置もAIの答えも、調べるたびに少し動きます。"]
    return "\n".join(L)


def ai_ask_lang(lg: str) -> str:
    return {"ja": "日本語", "en": "英語", "zh": "中国語", "ko": "韓国語"}.get(lg, lg)


if __name__ == "__main__":
    r = check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "", who="manual")
    print(json.dumps({k: v for k, v in r.items() if k != "ai"}, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in (r.get("ai") or {}).items() if k != "answers"}, ensure_ascii=False))
    print(message(r, "お店"))


_SA_MODS: dict = {}


def _sa(name: str):
    """sales-automation の src/<name>.py を読む（本番の ~/sales-automation に入るまでは NUMBERS_REPO の作業場所から）。
    値段・観光地の一覧・数字は向こうが正本（ここに書かない）。"""
    if name not in _SA_MODS:
        import importlib.util
        import sys
        for repo in (os.path.expanduser("~/sales-automation"), os.path.expanduser(os.getenv("NUMBERS_REPO", "~/sales-automation-1plan"))):
            p = os.path.join(repo, "src", f"{name}.py")
            if os.path.exists(p) and (name != "meo_observe" or "TOURIST_AREAS" in open(p, encoding="utf-8").read()):
                if repo not in sys.path:
                    sys.path.append(repo)
                spec = importlib.util.spec_from_file_location(f"sa_{name}", p)
                m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m)
                _SA_MODS[name] = m
                break
        else:
            raise FileNotFoundError(f"src/{name}.py が見つからない（~/sales-automation・NUMBERS_REPO）")
    return _SA_MODS[name]


def en_relevant(r: dict) -> bool:
    """英語の地図の話をする店か（英語の画面で20位以内に出ている／英字の店名／観光地の街）。"""
    TOURIST_AREAS = _sa("meo_observe").TOURIST_AREAS
    addr = " ".join(str(r.get(k) or "") for k in ("address", "address_ja", "town", "city"))
    return bool((r.get("rank_en") and r["rank_en"] <= 20) or re.search(r"[A-Za-z]{3,}", r.get("name") or "")
                or any(a in addr for a in TOURIST_AREAS))


_NUM = None


def _n():
    """調査の数字の正本（data/numbers.json）を読む src/numbers.py。~/sales-automation に入るまでは numbers_build.py の書き先（NUMBERS_REPO）から。
    ここで数字を書かない（{n:キー}・{label:キー} を fmt する）"""
    global _NUM
    if _NUM is None:
        import importlib.util
        for repo in (os.path.expanduser("~/sales-automation"), os.path.expanduser(os.getenv("NUMBERS_REPO", "~/sales-automation-1plan"))):
            p = os.path.join(repo, "src", "numbers.py")
            if os.path.exists(p) and os.path.exists(os.path.join(repo, "data", "numbers.json")):
                spec = importlib.util.spec_from_file_location("sa_numbers", p)
                _NUM = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(_NUM)
                break
        else:
            raise FileNotFoundError("src/numbers.py と data/numbers.json が見つからない（~/sales-automation・NUMBERS_REPO）")
    return _NUM


def _offer_line() -> str:
    """値段の1行（正本は ~/sales-automation/data/numbers.json の "offer"。ここで値段を書かない）。"""
    return _sa("meo_pricing").offer_sentence()
