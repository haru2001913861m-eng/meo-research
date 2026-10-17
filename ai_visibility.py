"""AIに聞いて、どの店が何%の回で出るかを測る（OpenAI・ウェブ検索つき・2026-10-16 会長「OpenAIで撮りに行く」）.

材料: data/inb_detail60.jsonl（32都市×6業種・5,571店。日本語名・英語名・日本語と英語のGoogleマップ順位・口コミ・英語の手入れ）
やり方: 都市×業種ごとに「おすすめの店を教えて」を 日本語・英語・中国語・韓国語 で R 回ずつ聞き、
       答えの本文に出た店を、その都市×業種の店名（日本語・英語）と突き合わせる。出典のURLも残す。
結果: data/ai_vis_raw.jsonl（1回＝1行・答えの全文と出典）／data/ai_vis_latest.md（集計）
鍵: ~/.config/hitotsunagi/openai_key（会長が保存。表示しない）
使い方: python3 ai_visibility.py --combos 10 --runs 2 [--langs ja,en,zh,ko] [--model gpt-5-mini] [--dry]
        python3 ai_visibility.py --report   （raw から集計だけ作り直す）
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import random
import re
import statistics
import time
import unicodedata
from datetime import datetime

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SRC = os.path.join(DATA, "inb_detail60.jsonl")
RAW = os.path.join(DATA, "ai_vis_raw.jsonl")
OUT = os.path.join(DATA, "ai_vis_latest.md")
KEY = os.path.expanduser("~/.config/hitotsunagi/openai_key")

CITY_EN = {"京都 嵐山": "Arashiyama, Kyoto", "京都 河原町": "Kawaramachi, Kyoto", "京都 祇園": "Gion, Kyoto", "別府": "Beppu",
           "名古屋 栄": "Sakae, Nagoya", "大阪 梅田": "Umeda, Osaka", "大阪 道頓堀": "Dotonbori, Osaka", "大阪 難波": "Namba, Osaka",
           "奈良": "Nara", "宮島": "Miyajima", "小樽": "Otaru", "広島": "Hiroshima", "日光": "Nikko", "札幌 すすきの": "Susukino, Sapporo",
           "東京 上野": "Ueno, Tokyo", "東京 六本木": "Roppongi, Tokyo", "東京 新宿": "Shinjuku, Tokyo", "東京 池袋": "Ikebukuro, Tokyo",
           "東京 浅草": "Asakusa, Tokyo", "東京 渋谷": "Shibuya, Tokyo", "東京 秋葉原": "Akihabara, Tokyo", "東京 銀座": "Ginza, Tokyo",
           "松本": "Matsumoto", "横浜 中華街": "Yokohama Chinatown", "神戸 三宮": "Sannomiya, Kobe", "福岡 博多": "Hakata, Fukuoka",
           "箱根湯本": "Hakone-Yumoto", "那覇 国際通り": "Kokusai-dori, Naha", "金沢": "Kanazawa", "鎌倉": "Kamakura", "長崎": "Nagasaki",
           "高山": "Takayama"}
IND = {"カフェ": ("カフェ", "cafes", "咖啡馆", "카페"), "居酒屋": ("居酒屋", "izakaya", "居酒屋", "이자카야"),
       "マッサージ": ("マッサージ店", "massage places", "按摩店", "마사지 가게"), "焼肉": ("焼肉店", "yakiniku restaurants", "烤肉店", "야키니쿠 가게"),
       "ラーメン": ("ラーメン店", "ramen shops", "拉面店", "라멘 가게"), "寿司": ("寿司店", "sushi restaurants", "寿司店", "스시 가게")}
PROMPT = {
    "ja": "{city}で、おすすめの{ind}を5つ、店名で教えてください。",
    "en": "I'm visiting {city_en}, Japan. Recommend 5 {ind_en} by name.",
    "zh": "我要去日本{city_en}。请推荐5家{ind_zh}，写出店名。",
    "ko": "일본 {city_en}에 갑니다. {ind_ko} 5곳을 가게 이름으로 추천해 주세요.",
}


def key() -> str:
    k = open(KEY).read().strip() if os.path.exists(KEY) else os.getenv("OPENAI_API_KEY", "")
    if not k:
        raise SystemExit(f"OpenAI の鍵がありません（{KEY}）")
    return k


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"[\s・･\-‐ー—'’\"“”.,!！?？()（）\[\]【】「」&＆/／|｜:：]", "", s)


def core(name: str) -> str:
    """支店名・説明を落とした看板の名前（「らーめん鴨to葱 新宿西口店」→「らーめん鴨to葱」）"""
    s = re.split(r"[｜|/／(（]", name or "")[0].strip()
    s = re.sub(r"\s+\S*(店|本店|支店|号店|館)$", "", s)
    s = re.sub(r"(本店|支店|[0-9０-９]*号店)$", "", s)
    return s.strip()


def load_shops() -> dict:
    by = collections.defaultdict(list)
    for l in open(SRC, encoding="utf-8"):
        r = json.loads(l)
        by[(r["city"], r["industry"])].append(r)
    return by


def mentioned(text: str, shop: dict) -> bool:
    t = norm(text)
    for nm in (shop.get("name_list"), shop.get("name_en")):
        c = norm(core(nm or ""))
        if len(c) >= 3 and c in t:
            return True
    return False


def ask(prompt: str, model: str, k: str) -> dict:
    body = {"model": model, "input": prompt, "tools": [{"type": "web_search"}]}
    for attempt in range(6):
        r = requests.post("https://api.openai.com/v1/responses", headers={"Authorization": f"Bearer {k}"}, json=body, timeout=180)
        if r.status_code == 200:
            break
        # 1分あたりの量の上限（無料に近い段は 6万トークン/分）は、言われた秒数＋余裕を待ってやり直す。残高切れは待っても無駄なので止める
        if r.status_code in (429, 500, 502, 503) and attempt < 5 and "insufficient_quota" not in r.text:
            m = re.search(r"try again in ([\d.]+)s", r.text)
            time.sleep((float(m.group(1)) if m else 20) + 5 * (attempt + 1))
            continue
        raise RuntimeError(f"OpenAI {r.status_code}: {r.text[:300]}")
    j = r.json()
    text, urls = [], []
    for item in j.get("output", []):
        for c in item.get("content", []) or []:
            if c.get("type") == "output_text":
                text.append(c.get("text", ""))
                urls += [a.get("url") for a in c.get("annotations", []) if a.get("url")]
    searches = sum(1 for item in j.get("output", []) if item.get("type") == "web_search_call")
    return {"text": "\n".join(text), "urls": urls, "usage": j.get("usage", {}), "searches": searches}


# 1回の値段の見積もり（$／100万トークン・検索1回）。料金が変わったらここを直す
PRICE = {"gpt-5-mini": (0.25, 2.0), "gpt-5-nano": (0.05, 0.4), "gpt-5": (1.25, 10.0)}
SEARCH_USD = 0.01


def cost(res: dict, model: str) -> float:
    pin, pout = PRICE.get(model, PRICE["gpt-5"])
    u = res.get("usage") or {}
    return u.get("input_tokens", 0) / 1e6 * pin + u.get("output_tokens", 0) / 1e6 * pout + res.get("searches", 0) * SEARCH_USD


def run(combos: int, runs: int, langs: list, model: str, dry: bool, seed: int, budget: float) -> None:
    by = load_shops()
    keys = sorted(k for k in by if k[0] in CITY_EN and len(by[k]) >= 10)
    random.Random(seed).shuffle(keys)
    keys = keys[:combos]
    k = "" if dry else key()
    n, spent = 0, 0.0
    done = set()
    if os.path.exists(RAW):                   # 同じモデルで聞き終えた（都市・業種・言語・回）は飛ばす＝止まっても続きから
        for l in open(RAW, encoding="utf-8"):
            r = json.loads(l)
            done.add((r["model"], r["city"], r["industry"], r["lang"], r["run"]))
    with open(RAW, "a", encoding="utf-8") as fp:
        for city, ind in keys:
            ja, en, zh, ko = IND[ind]
            for lang in langs:
                prompt = PROMPT[lang].format(city=city, city_en=CITY_EN[city], ind=ja, ind_en=en, ind_zh=zh, ind_ko=ko)
                for i in range(runs):
                    n += 1
                    if dry:
                        print("DRY", city, ind, lang, prompt)
                        continue
                    if (model, city, ind, lang, i) in done:
                        continue
                    if spent >= budget:
                        print(f"上限 ${budget} に届いたので止めます（見積もり ${spent:.2f}）")
                        report()
                        import ai_vis_neta
                        ai_vis_neta.write(import_=True)
                        return
                    res = ask(prompt, model, k)
                    spent += cost(res, model)
                    hits = [s["cid"] for s in by[(city, ind)] if mentioned(res["text"], s)]
                    fp.write(json.dumps({"at": datetime.now().isoformat(timespec="seconds"), "model": model, "city": city,
                                         "industry": ind, "lang": lang, "run": i, "prompt": prompt, "hits": hits,
                                         "text": res["text"], "urls": res["urls"], "usage": res["usage"], "searches": res["searches"], "usd": round(cost(res, model), 4)}, ensure_ascii=False) + "\n")
                    fp.flush()
                    print(f"{n} {city} {ind} {lang} 出た店 {len(hits)}  累計 ${spent:.3f}", flush=True)
                    time.sleep(15)            # 1回 1.6〜1.9万トークン。6万/分の上限に当たらない間隔
    if not dry:
        report()
        import ai_vis_neta                      # 計測が終わったら、すぐ投稿の材料（ネタ帳→Notion）にする
        ai_vis_neta.write(import_=True)


def report() -> None:
    by = load_shops()
    rows = [json.loads(l) for l in open(RAW, encoding="utf-8") if l.strip()]
    if not rows:
        return
    asked = collections.Counter()             # (city,ind,lang) → 聞いた回数
    hit = collections.Counter()               # (cid,lang) → 出た回数
    domains = collections.Counter()
    for r in rows:
        asked[(r["city"], r["industry"], r["lang"])] += 1
        for c in r["hits"]:
            hit[(c, r["lang"])] += 1
        for u in r.get("urls") or []:
            m = re.match(r"https?://(?:www\.)?([^/]+)", u or "")
            if m:
                domains[m.group(1)] += 1
    combos = {(r["city"], r["industry"]) for r in rows}
    langs = sorted({r["lang"] for r in rows})
    shops = [s for k in combos for s in by[k]]

    def rate(group, lang):
        """その群の店のうち、AIに1回でも出た店の割合"""
        g = [s for s in group if asked[(s["city"], s["industry"], lang)]]
        if not g:
            return "—"
        return f"{sum(1 for s in g if hit[(s['cid'], lang)]) / len(g) * 100:.0f}%（{len(g)}店）"

    def en_fix(s):
        return int(bool(s.get("rv_reply_latin"))) + int(bool(s.get("owner_post_latin"))) + int(bool(s.get("latin_name")))
    groups = [
        ("全部の店", shops),
        ("日本語のGoogleマップで上位10", [s for s in shops if (s.get("rank_ja") or 99) <= 10]),
        ("日本語で11位以下", [s for s in shops if (s.get("rank_ja") or 99) > 10]),
        ("英語のGoogleマップで上位10", [s for s in shops if (s.get("rank_en") or 99) <= 10]),
        ("口コミ50件以上", [s for s in shops if (s.get("list_reviews") or 0) >= 50]),
        ("口コミ50件未満", [s for s in shops if (s.get("list_reviews") or 0) < 50]),
        ("英語の手入れ 0", [s for s in shops if en_fix(s) == 0]),
        ("英語の手入れ 2〜3", [s for s in shops if en_fix(s) >= 2]),
    ]
    L = [f"# AIに聞いて、店が出たか（OpenAI・ウェブ検索つき）", "",
         f"聞いた回数 {len(rows)}回／都市×業種 {len(combos)}組／対象の店 {len(shops)}店／モデル {rows[-1]['model']}／{rows[0]['at'][:10]}〜{rows[-1]['at'][:10]}", "",
         "| 店の群 | " + " | ".join(langs) + " |", "|---|" + "---|" * len(langs)]
    for name, g in groups:
        L.append(f"| {name} | " + " | ".join(rate(g, la) for la in langs) + " |")
    per = [len(r["hits"]) for r in rows]
    L += ["", f"1回の答えに出た店（このデータの店と一致した数）の中央値: {statistics.median(per)}", "",
          "## 答えの出典（多い順・上位15）", "| サイト | 回数 |", "|---|---|"]
    L += [f"| {d} | {n} |" for d, n in domains.most_common(15)]
    L += ["", "※店名の突き合わせは、看板の名前（支店名を除く）が答えの本文に含まれるかで判定。"]
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--combos", type=int, default=10)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--langs", default="ja,en,zh,ko")
    ap.add_argument("--model", default=os.getenv("AI_VIS_MODEL", "gpt-5-mini"))
    ap.add_argument("--seed", type=int, default=16)
    ap.add_argument("--budget", type=float, default=2.0, help="見積もりの合計がこの金額（ドル）に届いたら止める")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        report()
    else:
        run(a.combos, a.runs, a.langs.split(","), a.model, a.dry, a.seed, a.budget)
