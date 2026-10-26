# -*- coding: utf-8 -*-
"""調査の数字の正本を作る（会長 2026-10-18「調査が増えるたびに数字は変わる。1か所にまとめ、全部そこから読む。
1か所でも食い違うと信用を落とす」）。

使い方: python3 numbers_build.py            （analyze.py・survey_stats.py を回し直してから全部の数字を作る）
        python3 numbers_build.py --no-run   （回し直さず、今あるファイルから作るだけ）
結果:   ~/sales-automation-1plan/data/numbers.json（Railway が読む・リポジトリに入れる）
        ~/sales-automation/data/numbers.json は触らない（本番のリポジトリはマージで入る）
        ~/meo-research/data/numbers.json（写し）
材料:   data/survey_stats.json（数えた店の合計）／data/result_latest.md（日本語の全国調査の表 A〜G）／
        data/detail*.jsonl・frame.jsonl（写真の枚数・調査の規模）／data/inb_gap_latest.md（観光地の日英）／
        data/ai_vis_latest.md・ai_vis_raw.jsonl（AI）／sales-automation の data/meo_top10_yardstick.json（上位10%の物差し）
        作る台本が無い一回きりの集計（10/10 の個人店13,804店・10/12 の上位10%の再集計 N349〜N357・218店・132店 など）は
        下の FIXED に「母数・出所のファイル・日付」つきで書く（ここも正本の1か所）。

1つの数字の形:
  "jp.stores": {"value": "14,504", "num": 14504, "unit": "店", "base": "…母数…", "label": "全国14,504店の調査",
                "source": "…", "at": "2026-10-18", "kind": "computed|fixed", "pattern": "（照合用の正規表現・任意）"}
  value は店に見せる形そのまま。label は「どの調査の数字か」を書く時の言い方（結果の数字は合計の27,326店ではなく、その調査の母数で書く）。
  pattern の {v} は value に置き換えて、numbers_check.py が古い値・取り違えを探すのに使う。
値が変わったら、前の値を history に残す（numbers_check.py が古い写しを見つける）。
"offer"（値段）は値段の担当が持つ。ここでは読まずに、そのまま残す。
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import statistics as st
import subprocess
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SA = os.path.expanduser(os.getenv("NUMBERS_REPO", "~/sales-automation-1plan"))
OUT_MAIN = os.path.join(SA, "data", "numbers.json")
OUT_COPY = os.path.join(DATA, "numbers.json")
TODAY = date.today().isoformat()

IND_KEYS = {"カフェ": "cafe", "ラーメン": "ramen", "居酒屋": "izakaya", "整体": "seitai", "美容室": "biyou"}
IND_NAMES = {"カフェ": "カフェ", "ラーメン": "ラーメン", "居酒屋": "居酒屋", "整体": "整体院", "美容室": "美容室"}


# ── 表の読み方 ───────────────────────────────────────────────────────────
def md_tables(path: str) -> dict[str, list[list[str]]]:
    """「### A. …」の見出しごとに、表の行（セルのリスト）を返す。キーは見出しの先頭の記号（A, B, 1, 2 …）"""
    out: dict[str, list[list[str]]] = {}
    key = None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"^###\s*([0-9A-Z]+)\.", line)
        if m:
            key = m.group(1)
            out[key] = []
            continue
        if key and line.startswith("|") and not re.match(r"^\|(-+\|)+$", line.replace(" ", "")):
            cells = [c.strip() for c in line.strip("|").split("|")]
            out[key].append(cells)
    for k in out:                       # 先頭の行は見出し
        out[k] = out[k][1:]
    return out


def n_int(s: str) -> int:
    return int(re.sub(r"[^\d]", "", s))


def n_float(s: str) -> float:
    return float(re.search(r"\d+(?:\.\d+)?", s).group(0))


def row(tab: list[list[str]], ind: str, lab: str) -> list[str]:
    for r in tab:
        if r[0] == ind and r[1] == lab:
            return r
    raise KeyError(f"表に行が無い: {ind} / {lab}")


def pct(a: float, b: float) -> int:
    """四捨五入（Python の round は偶数丸めなので使わない）"""
    return int(100 * a / b + 0.5) if b else 0


def comma(v: int) -> str:
    return f"{v:,}"


def dec(v: float) -> str:
    return f"{v:.1f}"


def ratio_txt(a: float, b: float) -> str:
    r = a / b
    return f"約{int(r + 0.5)}倍"


# ── 材料を読む ──────────────────────────────────────────────────────────
def read_jsonl(path: str):
    if not os.path.exists(path):
        return
    for l in open(path, encoding="utf-8"):
        try:
            yield json.loads(l)
        except ValueError:
            continue


def jp_raw() -> dict:
    """日本語の全国調査の生データ（analyze.py と同じ読み方: frame は cid の最初の行・detail は最後の行）"""
    frame = [r for r in read_jsonl(os.path.join(DATA, "frame.jsonl")) if r.get("cid")]
    uniq: dict = {}
    for r in frame:
        uniq.setdefault(r["cid"], r)
    detail: dict = {}
    for fn in sorted(os.listdir(DATA)):
        if fn.startswith("detail") and fn.endswith(".jsonl"):
            for r in read_jsonl(os.path.join(DATA, fn)):
                if r.get("cid") and not r.get("error"):
                    detail[r["cid"]] = r
    return {"frame": frame, "uniq": uniq, "detail": detail}


# ── 事実を作る ──────────────────────────────────────────────────────────
class Book:
    def __init__(self):
        self.facts: dict[str, dict] = {}

    def add(self, key, value, num, unit, base, label, source, *, kind="computed", at=TODAY, pattern=None, note=None):
        if key in self.facts:
            raise ValueError(f"同じキーが2回: {key}")
        f = {"value": value, "num": num, "unit": unit, "base": base, "label": label, "source": source, "at": at, "kind": kind}
        if pattern:
            f["pattern"] = pattern
        if note:
            f["note"] = note
        self.facts[key] = f


# 町の名前で呼ぶ投稿に使う地方の市（キーは英字・Threads の town 型が上から回す）。医療・施術所（整体）は口コミの話に使わないので外す。
# 高松・金沢は sales-automation の伏せ字の禁止語（tob_guard）に入っているので使わない
TOWNS = {"matsue": "松江市", "tokushima": "徳島市", "miyazaki": "宮崎市", "himeji": "姫路市",
         "matsumoto": "松本市", "hakodate": "函館市", "oita": "大分市", "kochi": "高知市",
         "tottori": "鳥取市", "wakayama": "和歌山市", "fukui": "福井市", "kofu": "甲府市", "gifu": "岐阜市", "toyama": "富山市"}
TOWN_INDS = {"カフェ": "cafe", "ラーメン": "ramen", "居酒屋": "izakaya", "美容室": "biyou"}
TOWN_MIN = 30          # 1つの市×業種で読めた店がこれ未満なら作らない


def town_facts(b: "Book", detail: dict) -> None:
    """市×業種: 読めた店の数・最新の口コミ（最大20件）に返事が1件も無い店・お知らせ（投稿）を出している店"""
    g = collections.defaultdict(list)
    for r in detail.values():
        g[(r.get("city"), r.get("industry"))].append(r)
    for slug, city in TOWNS.items():
        for ind, ik in TOWN_INDS.items():
            rows = g.get((city, ind)) or []
            rv = [r for r in rows if isinstance(r.get("rv_n"), int) and r["rv_n"] >= 3]
            if len(rv) < TOWN_MIN:
                continue
            nr = sum(1 for r in rv if r.get("rv_replies") == 0)
            po = [r for r in rows if r.get("has_posts") is not None]
            base = f"「{ind} {city}」でGoogleマップを探して出た{IND_NAMES[ind]}のうち、最新の口コミ（最大20件）を読めた{len(rv)}店（2026-10-09〜）"
            lab = f"{city}の{IND_NAMES[ind]}{len(rv)}店の調査"
            src = "meo-research/data/detail*.jsonl（numbers_build.town_facts）"
            k = f"town.{slug}.{ik}"
            b.add(k + ".n", comma(len(rv)), len(rv), "店", base, lab, src, pattern=city[:2] + r"[^。\n]{0,12}{v}店")
            b.add(k + ".noreply_n", comma(nr), nr, "店", base + "で、返事が1件も無い店", lab, src)
            b.add(k + ".noreply_share", f"{pct(nr, len(rv))}%", pct(nr, len(rv)), "%", base + "で、返事が1件も無い店の割合", lab, src)
            if len(po) >= TOWN_MIN:
                pn = sum(1 for r in po if r["has_posts"])
                b.add(k + ".post_n", comma(pn), pn, "店", base.replace(f"最新の口コミ（最大20件）を読めた{len(rv)}店", f"お知らせ（投稿）の有無を読めた{len(po)}店"),
                      lab, src)
                b.add(k + ".post_base", comma(len(po)), len(po), "店", "お知らせ（投稿）の有無を読めた店", lab, src)


def build(seed_old: str | None = None) -> tuple[dict, dict]:
    b = Book()
    # 1) 数えた店の合計（survey_stats.json）
    s = json.load(open(os.path.join(DATA, "survey_stats.json"), encoding="utf-8"))
    s_at = s["at"][:10]
    B_TOTAL = (f"調査の合計（日本語の全国調査＋観光地の日英調査＋業種の標本調査・同じ店は1回）{comma(s['stores'])}店"
               f"・{s['cities']}地域・{s['industries']}業種")
    SRC_TOTAL = "meo-research/survey_stats.py → data/survey_stats.json"
    lab_total = f"全国{comma(s['stores'])}店"
    b.add("total.stores", comma(s["stores"]), s["stores"], "店", B_TOTAL, lab_total, SRC_TOTAL, at=s_at,
          note="数えた店の合計を言う文だけに使う。結果の数字（月2.9件・15% など）の母数ではない")
    b.add("total.reviews", comma(s["reviews"]), s["reviews"], "件", B_TOTAL, f"口コミ{s['reviews_man']}件", SRC_TOTAL, at=s_at)
    b.add("total.reviews_man", s["reviews_man"], s["reviews"] // 10000, "万", B_TOTAL, f"口コミ{s['reviews_man']}件", SRC_TOTAL, at=s_at,
          pattern=r"{v}件")
    b.add("total.searches", str(s["searches"]), s["searches"], "回", B_TOTAL, f"{s['searches']}回の検索", SRC_TOTAL, at=s_at,
          pattern=r"{v}回")
    b.add("total.searches_en", str(s["searches_en"]), s["searches_en"], "回", B_TOTAL, f"英語で{s['searches_en']}回", SRC_TOTAL, at=s_at)
    b.add("total.cities", str(s["cities"]), s["cities"], "地域", B_TOTAL, f"{s['cities']}地域", SRC_TOTAL, at=s_at,
          pattern=r"{v}地域")
    b.add("total.industries", str(s["industries"]), s["industries"], "業種", B_TOTAL, f"{s['industries']}業種", SRC_TOTAL, at=s_at)

    # 2) 日本語の全国調査（result_latest.md の表＋生データ）
    res = os.path.join(DATA, "result_latest.md")
    head = open(res, encoding="utf-8").readline()
    m = re.search(r"母集団\s*(\d+)店／詳細\s*(\d+)店／取得\s*([\d-]+)", head)
    pop, det, got = int(m.group(1)), int(m.group(2)), m.group(3)
    T = md_tables(res)
    raw = jp_raw()
    jp_queries = {r.get("query") for r in raw["frame"]}
    jp_cities = {r["city"] for r in raw["uniq"].values()}
    jp_inds = {r["industry"] for r in raw["uniq"].values()}
    jp_reviews = sum(int(r.get("reviews") or 0) for r in raw["uniq"].values())
    B_JP = f"日本語の全国調査 {comma(pop)}店（{len(jp_cities)}都市×{len(jp_inds)}業種・{len(jp_queries)}回検索・詳細を見られた{comma(det)}店・{got}〜）"
    L_JP = f"全国{comma(pop)}店の調査"
    SRC_R = "meo-research/analyze.py → data/result_latest.md"
    SRC_RAW = "meo-research/data/frame.jsonl・detail*.jsonl（numbers_build.py で集計）"
    b.add("jp.stores", comma(pop), pop, "店", B_JP, L_JP, SRC_R, pattern=r"{v}店")
    b.add("jp.detail", comma(det), det, "店", B_JP, f"詳細を見られた{comma(det)}店", SRC_R, pattern=r"{v}店",
          note="1店ずつ開いて詳細を読めた店。結果の表（A〜G）はこの店数で数えている")
    b.add("jp.cities", str(len(jp_cities)), len(jp_cities), "都市", B_JP, f"{len(jp_cities)}都市", SRC_RAW, pattern=r"{v}都市")
    b.add("jp.industries", str(len(jp_inds)), len(jp_inds), "業種", B_JP, f"{len(jp_inds)}業種", SRC_RAW)
    b.add("jp.searches", str(len(jp_queries)), len(jp_queries), "回", B_JP, f"{len(jp_queries)}回検索", SRC_RAW, pattern=r"{v}(回|検索)")
    b.add("jp.reviews", comma(jp_reviews), jp_reviews, "件", B_JP, f"口コミ{comma(jp_reviews)}件", SRC_RAW, pattern=r"{v}件")
    b.add("jp.reviews_man", f"{jp_reviews // 10000}万", jp_reviews // 10000, "万", B_JP, f"口コミ{jp_reviews // 10000}万件", SRC_RAW,
          pattern=r"{v}")

    # A. 投稿
    A = T["A"]
    ya, na = row(A, "全業種", "投稿あり"), row(A, "全業種", "投稿なし")
    yn, nn = n_int(ya[2]), n_int(na[2])
    b.add("jp.post.share", f"{pct(yn, yn + nn)}%", pct(yn, yn + nn), "%", B_JP, L_JP, SRC_R + " 表A",
          pattern=r"投稿[^。\n]{0,20}{v}")
    b.add("jp.post.none_share", f"{pct(nn, yn + nn)}%", pct(nn, yn + nn), "%", B_JP, L_JP, SRC_R + " 表A",
          pattern=r"投稿[^。\n]{0,20}{v}")
    b.add("jp.post.yes_n", comma(yn), yn, "店", B_JP, L_JP, SRC_R + " 表A", pattern=r"{v}店")
    b.add("jp.post.no_n", comma(nn), nn, "店", B_JP, L_JP, SRC_R + " 表A", pattern=r"{v}店")
    yp, np_ = n_float(ya[3]), n_float(na[3])
    b.add("jp.post.yes_pace", dec(yp), yp, "件/月", B_JP, L_JP, SRC_R + " 表A（月あたり口コミ・中央値）", pattern=r"月{v}件")
    b.add("jp.post.no_pace", dec(np_), np_, "件/月", B_JP, L_JP, SRC_R + " 表A（月あたり口コミ・中央値）", pattern=r"{v}件")
    b.add("jp.post.ratio", ratio_txt(yp, np_), round(yp / np_, 1), "倍", B_JP, L_JP, SRC_R + " 表A（月あたりの比）")
    for ind, k in IND_KEYS.items():
        y, n = n_int(row(A, ind, "投稿あり")[2]), n_int(row(A, ind, "投稿なし")[2])
        b.add(f"jp.post.share.{k}", f"{pct(y, y + n)}%", pct(y, y + n), "%", B_JP, L_JP, SRC_R + f" 表A（{ind}）",
              pattern=IND_NAMES[ind][:2] + r"[^。\n、・]{0,8}{v}")

    # B. 手入れの数
    Bt = T["B"]
    lo, hi = row(Bt, "全業種", "0〜2個"), row(Bt, "全業種", "5個以上")
    lp, hp = n_float(lo[3]), n_float(hi[3])
    b.add("jp.care.hi_pace", dec(hp), hp, "件/月", B_JP, L_JP, SRC_R + " 表B", pattern=r"月{v}件")
    b.add("jp.care.lo_pace", dec(lp), lp, "件/月", B_JP, L_JP, SRC_R + " 表B", pattern=r"{v}件")
    b.add("jp.care.hi_n", comma(n_int(hi[2])), n_int(hi[2]), "店", B_JP, L_JP, SRC_R + " 表B", pattern=r"{v}店")
    b.add("jp.care.lo_n", comma(n_int(lo[2])), n_int(lo[2]), "店", B_JP, L_JP, SRC_R + " 表B", pattern=r"{v}店")
    b.add("jp.care.hi_reviews", f"{int(n_float(hi[4]))}件", int(n_float(hi[4])), "件", B_JP, L_JP, SRC_R + " 表B（5個以上・口コミ件数の中央値）",
          pattern=r"{v}[^。\n]{0,10}53件|{v}\s*vs")
    b.add("jp.care.lo_reviews", f"{int(n_float(lo[4]))}件", int(n_float(lo[4])), "件", B_JP, L_JP, SRC_R + " 表B（0〜2個・口コミ件数の中央値）")
    b.add("jp.care.ratio", ratio_txt(hp, lp), round(hp / lp, 1), "倍", B_JP, L_JP, SRC_R + " 表B（月あたりの比）")

    # C. 口コミの速さと星
    C = T["C"]
    for lab, k in (("月1件未満", "lt1"), ("月1〜5件", "1to5"), ("月5件以上", "ge5")):
        r = row(C, "全業種", lab)
        b.add(f"jp.speed.{k}_star", dec(n_float(r[5])), n_float(r[5]), "星", B_JP, L_JP, SRC_R + f" 表C（{lab}・星の中央値）")
        b.add(f"jp.speed.{k}_n", comma(n_int(r[2])), n_int(r[2]), "店", B_JP, L_JP, SRC_R + f" 表C（{lab}）", pattern=r"{v}店")
        b.add(f"jp.speed.{k}_pos", f"{int(n_float(r[6]))}位", int(n_float(r[6])), "位", B_JP, L_JP, SRC_R + f" 表C（{lab}・一覧の位置の中央値）")

    # D. 口コミの中身（速い店＝月3件以上・遅い店＝月1件未満）
    D = T["D"]
    fast = next(r for r in D if r[0] == "全業種" and r[1].startswith("速い店"))
    slow = next(r for r in D if r[0] == "全業種" and r[1].startswith("遅い店"))
    fn_, sn_ = int(re.search(r"(\d+)店", fast[1]).group(1)), int(re.search(r"(\d+)店", slow[1]).group(1))
    b.add("jp.pace.fast_n", comma(fn_), fn_, "店", B_JP, L_JP, SRC_R + " 表D（月3件以上）", pattern=r"{v}店")
    b.add("jp.pace.slow_n", comma(sn_), sn_, "店", B_JP, L_JP, SRC_R + " 表D（月1件未満）", pattern=r"{v}店")
    b.add("jp.access.fast", f"{n_float(fast[4])}%", n_float(fast[4]), "%", B_JP, L_JP, SRC_R + " 表D（行き方の話）",
          pattern=r"行き方[^。\n]{0,20}{v}")
    b.add("jp.access.slow", f"{n_float(slow[4])}%", n_float(slow[4]), "%", B_JP, L_JP, SRC_R + " 表D（行き方の話）",
          pattern=r"{v}")

    # E. 返信
    E = T["E"]
    ry, rn = row(E, "全業種", "返信あり"), row(E, "全業種", "返信なし")
    ryn, rnn = n_int(ry[2]), n_int(rn[2])
    b.add("jp.reply.none_share", f"{pct(rnn, ryn + rnn)}%", pct(rnn, ryn + rnn), "%", B_JP, L_JP, SRC_R + " 表E",
          pattern=r"返信[^。\n]{0,12}{v}")
    b.add("jp.reply.yes_share", f"{pct(ryn, ryn + rnn)}%", pct(ryn, ryn + rnn), "%", B_JP, L_JP, SRC_R + " 表E",
          pattern=r"返信[^。\n]{0,12}{v}")
    b.add("jp.reply.yes_n", comma(ryn), ryn, "店", B_JP, L_JP, SRC_R + " 表E", pattern=r"{v}店")
    b.add("jp.reply.no_n", comma(rnn), rnn, "店", B_JP, L_JP, SRC_R + " 表E", pattern=r"{v}店")
    b.add("jp.reply.yes_star", dec(n_float(ry[5])), n_float(ry[5]), "星", B_JP, L_JP, SRC_R + " 表E（星の中央値）",
          pattern=r"星[^。\n]{0,6}{v}")
    b.add("jp.reply.no_star", dec(n_float(rn[5])), n_float(rn[5]), "星", B_JP, L_JP, SRC_R + " 表E（星の中央値）",
          pattern=r"{v}")
    f7, s30 = row(E, "全業種", "返信が7日以内"), row(E, "全業種", "返信が30日超")
    b.add("jp.reply.fast_pace", dec(n_float(f7[3])), n_float(f7[3]), "件/月", B_JP, L_JP, SRC_R + " 表E（7日以内）")
    b.add("jp.reply.slow_pace", dec(n_float(s30[3])), n_float(s30[3]), "件/月", B_JP, L_JP, SRC_R + " 表E（30日超）")
    b.add("jp.reply.fast_n", comma(n_int(f7[2])), n_int(f7[2]), "店", B_JP, L_JP, SRC_R + " 表E（7日以内）", pattern=r"{v}店")
    b.add("jp.reply.slow_n", comma(n_int(s30[2])), n_int(s30[2]), "店", B_JP, L_JP, SRC_R + " 表E（30日超）", pattern=r"{v}店")
    sy, sn = row(E, "整体", "返信あり"), row(E, "整体", "返信なし")
    b.add("jp.reply.seitai_yes_pace", dec(n_float(sy[3])), n_float(sy[3]), "件/月", B_JP, L_JP, SRC_R + " 表E（整体）")
    b.add("jp.reply.seitai_no_pace", dec(n_float(sn[3])), n_float(sn[3]), "件/月", B_JP, L_JP, SRC_R + " 表E（整体）")
    b.add("jp.reply.seitai_yes_n", comma(n_int(sy[2])), n_int(sy[2]), "店", B_JP, L_JP, SRC_R + " 表E（整体）", pattern=r"{v}店")
    b.add("jp.reply.seitai_no_n", comma(n_int(sn[2])), n_int(sn[2]), "店", B_JP, L_JP, SRC_R + " 表E（整体）", pattern=r"{v}店")
    for ind, k in IND_KEYS.items():
        y, n = n_int(row(E, ind, "返信あり")[2]), n_int(row(E, ind, "返信なし")[2])
        b.add(f"jp.reply.share.{k}", f"{pct(y, y + n)}%", pct(y, y + n), "%", B_JP, L_JP, SRC_R + f" 表E（{ind}）",
              pattern=IND_NAMES[ind][:2] + r"[^。\n、・]{0,8}{v}")

    # 業種ごと・群ごとの「一覧の位置」「月あたり」（広告の事実カード・業種の投稿で使う）
    def cellv(tab, ind, lab, col):
        return n_float(row(tab, ind, lab)[col])
    b.add("jp.reply.fast_pos", f"{int(cellv(E, '全業種', '返信が7日以内', 6))}位", int(cellv(E, '全業種', '返信が7日以内', 6)), "位", B_JP, L_JP, SRC_R + " 表E（一覧の位置・中央値）")
    b.add("jp.reply.slow_pos", f"{int(cellv(E, '全業種', '返信が30日超', 6))}位", int(cellv(E, '全業種', '返信が30日超', 6)), "位", B_JP, L_JP, SRC_R + " 表E（一覧の位置・中央値）")
    # 業種ごとの店数・投稿あり／なし（表A）・手入れ 0〜2個／5個以上（表B）
    for ind, k in IND_KEYS.items():
        ya_, na_ = row(A, ind, "投稿あり"), row(A, ind, "投稿なし")
        b.add(f"jp.ind.n.{k}", comma(n_int(ya_[2]) + n_int(na_[2])), n_int(ya_[2]) + n_int(na_[2]), "店", B_JP, L_JP, SRC_R + f" 表A（{ind}の店数）", pattern=r"{v}店")
        for lab, side, r_ in (("投稿あり", "yes", ya_), ("投稿なし", "no", na_)):
            b.add(f"jp.post.{side}_n.{k}", comma(n_int(r_[2])), n_int(r_[2]), "店", B_JP, L_JP, SRC_R + f" 表A（{ind}・{lab}）", pattern=r"{v}店")
            b.add(f"jp.post.{side}_pace.{k}", dec(n_float(r_[3])), n_float(r_[3]), "件/月", B_JP, L_JP, SRC_R + f" 表A（{ind}・{lab}）")
        for lab, side in (("0〜2個", "lo"), ("5個以上", "hi")):
            r_ = row(Bt, ind, lab)
            b.add(f"jp.care.{side}_n.{k}", comma(n_int(r_[2])), n_int(r_[2]), "店", B_JP, L_JP, SRC_R + f" 表B（{ind}・{lab}）", pattern=r"{v}店")
            b.add(f"jp.care.{side}_pace.{k}", dec(n_float(r_[3])), n_float(r_[3]), "件/月", B_JP, L_JP, SRC_R + f" 表B（{ind}・{lab}）")
    b.add("jp.post.biyou_yes_pos", f"{int(cellv(A, '美容室', '投稿あり', 6))}位", int(cellv(A, '美容室', '投稿あり', 6)), "位", B_JP, L_JP, SRC_R + " 表A（美容室・一覧の位置）")
    b.add("jp.post.biyou_no_pos", f"{int(cellv(A, '美容室', '投稿なし', 6))}位", int(cellv(A, '美容室', '投稿なし', 6)), "位", B_JP, L_JP, SRC_R + " 表A（美容室・一覧の位置）")
    b.add("jp.speed.izakaya_ge5_pos", f"{int(cellv(C, '居酒屋', '月5件以上', 6))}位", int(cellv(C, '居酒屋', '月5件以上', 6)), "位", B_JP, L_JP, SRC_R + " 表C（居酒屋・一覧の位置）")
    b.add("jp.speed.izakaya_lt1_pos", f"{int(cellv(C, '居酒屋', '月1件未満', 6))}位", int(cellv(C, '居酒屋', '月1件未満', 6)), "位", B_JP, L_JP, SRC_R + " 表C（居酒屋・一覧の位置）")

    # F. 店名の売り文句
    F = T["F"]
    hy = row(F, "全業種", "売り文句入り")
    hn, hall = n_int(hy[2]), n_int(hy[2]) + n_int(hy[6])
    b.add("jp.name.hype_n", f"{hn}", hn, "店", B_JP, L_JP, SRC_R + " 表F（売り文句入り）", pattern=r"{v}店")
    sc = row(F, "整体", "業種語入り")
    b.add("jp.name.seitai_cat_pos", f"{int(n_float(sc[5]))}位", int(n_float(sc[5])), "位", B_JP, L_JP, SRC_R + " 表F（整体・業種語入り・一覧の位置）")
    b.add("jp.name.seitai_nocat_pos", f"{int(n_float(sc[9]))}位", int(n_float(sc[9])), "位", B_JP, L_JP, SRC_R + " 表F（整体・業種語なし・一覧の位置）")
    b.add("jp.name.hype_share", f"{100 * hn / hall:.1f}%", round(100 * hn / hall, 1), "%", B_JP, L_JP, SRC_R + " 表F")

    # G. 祝日の営業時間（detail.py の special_hours＝営業時間表に「時間変更の可能性」等の表示がある＝祝日の時間をまだ確かめていない）
    G = T["G"]
    gy, gn = row(G, "全業種", "祝日の時間が未確認（時間変更の可能性）"), row(G, "全業種", "祝日の表示なし（確認済み）")
    uy, un = n_int(gy[2]), n_int(gn[2])
    B_HOL = B_JP + f"のうち営業時間表を読めた{comma(uy + un)}店"
    b.add("jp.holiday.unconfirmed_share", f"{pct(uy, uy + un)}%", pct(uy, uy + un), "%", B_HOL, L_JP,
          SRC_R + " 表G（special_hours＝営業時間表に「時間変更の可能性」）", pattern=r"祝日[^。\n]{0,30}{v}",
          note="detail.py の special_hours（営業時間表に「時間変更の可能性」の表示）＝まだ確かめていない店。10/10 の読み方（77%＝未確認）と同じ向き。表Gの旧見出し「祝日の特別営業時間あり／祝日の設定なし」は 2026-10-18 に直した")
    b.add("jp.holiday.unconfirmed_n", comma(uy), uy, "店", B_HOL, L_JP, SRC_R + " 表G", pattern=r"{v}店")
    b.add("jp.holiday.confirmed_n", comma(un), un, "店", B_HOL, L_JP, SRC_R + " 表G（表示なし＝確かめ済み・設定済み）", pattern=r"{v}店",
          note="「祝日の設定なし」と書かない（表示が出ていない側＝確かめ済みの店）")
    b.add("jp.holiday.unconfirmed_pos", f"{int(n_float(gy[6]))}位", int(n_float(gy[6])), "位", B_HOL, L_JP, SRC_R + " 表G（一覧の位置・中央値）")
    b.add("jp.holiday.confirmed_pos", f"{int(n_float(gn[6]))}位", int(n_float(gn[6])), "位", B_HOL, L_JP, SRC_R + " 表G（一覧の位置・中央値）")

    # 写真の枚数 × 口コミ件数（detail の photos・frame の reviews）／写真200枚以上の店の割合
    D_ = []
    for cid, d in raw["detail"].items():
        f = raw["uniq"].get(cid, {})
        if d.get("photos") is None:
            continue
        D_.append((d["industry"], d["photos"], f.get("reviews") or d.get("list_reviews")))
    hi_rv = [rv for _, p, rv in D_ if p >= 200 and rv is not None]
    lo_rv = [rv for _, p, rv in D_ if p <= 9 and rv is not None]
    B_PH = B_JP + f"のうち写真の枚数を読めた{comma(len(D_))}店"
    b.add("jp.photo.hi_reviews", f"{int(st.median(hi_rv))}件", int(st.median(hi_rv)), "件", B_PH, L_JP, SRC_RAW + "（写真200枚以上・口コミ件数の中央値）",
          pattern=r"200枚[^。\n]{0,30}{v}")
    b.add("jp.photo.lo_reviews", f"{int(st.median(lo_rv))}件", int(st.median(lo_rv)), "件", B_PH, L_JP, SRC_RAW + "（写真9枚以下・口コミ件数の中央値）",
          pattern=r"9枚[^。\n]{0,20}{v}")
    b.add("jp.photo.hi_n", comma(len(hi_rv)), len(hi_rv), "店", B_PH, L_JP, SRC_RAW, pattern=r"{v}店")
    b.add("jp.photo.lo_n", comma(len(lo_rv)), len(lo_rv), "店", B_PH, L_JP, SRC_RAW, pattern=r"{v}店")
    b.add("jp.photo.base_n", comma(len(D_)), len(D_), "店", B_PH, L_JP, SRC_RAW, pattern=r"{v}店")
    by = collections.defaultdict(list)
    for ind, p, _ in D_:
        by[ind].append(p >= 200)
    shares = {}
    for ind, k in IND_KEYS.items():
        v = pct(sum(by[ind]), len(by[ind]))
        shares[ind] = v
        b.add(f"jp.photo200.share.{k}", f"{v}%", v, "%", B_PH, L_JP, SRC_RAW + f"（{ind}・写真200枚以上の店の割合）")
    b.add("jp.photo200.range", f"{min(shares.values())}〜{max(shares.values())}%", None, "%", B_PH, L_JP, SRC_RAW + "（業種ごとの割合の幅）")

    # 3) 上位10%の物差し（yardstick.py → sales-automation の data/meo_top10_yardstick.json）
    y = json.load(open(os.path.join(SA, "data", "meo_top10_yardstick.json"), encoding="utf-8"))
    B_Y = f"上位10%の物差し（日本語の全国調査 {comma(pop)}店・同じ都市×業種の一覧の先頭1割・{len(y['by_city'])}組・中央値）"
    SRC_Y = "meo-research/yardstick.py → sales-automation data/meo_top10_yardstick.json"
    b.add("top10.pairs", str(len(y["by_city"])), len(y["by_city"]), "組", B_Y, L_JP, SRC_Y, at=y.get("made", TODAY), pattern=r"{v}組")
    b.add("top10.n", comma(y["all"]["n"]), y["all"]["n"], "店", B_Y, L_JP, SRC_Y, at=y.get("made", TODAY), pattern=r"{v}店")
    b.add("top10.rest_n", comma(y["rest"]["n"]), y["rest"]["n"], "店", B_Y, L_JP, SRC_Y, at=y.get("made", TODAY), pattern=r"{v}店")
    for k in ("reviews", "per_month", "star", "photos"):
        u = {"reviews": "件", "per_month": "件/月", "star": "星", "photos": "枚"}[k]
        for side in ("all", "rest"):
            v = y[side][k]
            b.add(f"top10.{'top' if side == 'all' else 'rest'}_{k}", str(v), v, u, B_Y, L_JP, SRC_Y, at=y.get("made", TODAY))
    for side in ("all", "rest"):
        v = int(y[side]["reply_rate"] * 100 + 0.5)
        b.add(f"top10.{'top' if side == 'all' else 'rest'}_reply_rate", f"{v}%", v, "%", B_Y, L_JP, SRC_Y, at=y.get("made", TODAY))

    # 4) 観光地の日英（analyze_gap.py → inb_gap_latest.md）
    inb = os.path.join(DATA, "inb_gap_latest.md")
    ih = open(inb, encoding="utf-8").readline()
    m = re.search(r"検索\s*(\d+)\s*件.*詳しく見た店\s*(\d+)\s*店", ih)
    isr, ist = int(m.group(1)), int(m.group(2))
    ifr = [r for r in read_jsonl(os.path.join(DATA, "inb_frame60.jsonl")) if r.get("cid")]
    icities, iinds = {r["city"] for r in ifr}, {r["industry"] for r in ifr}
    IT = md_tables(inb)
    B_INB = f"観光地の日英調査（{len(icities)}都市×{len(iinds)}業種・日本語と英語で{isr}回検索・{comma(ist)}店）"
    L_INB = f"観光地の{comma(ist)}店の調査"
    SRC_I = "meo-research/analyze_gap.py → data/inb_gap_latest.md"
    b.add("inb.searches", str(isr), isr, "回", B_INB, L_INB, SRC_I, pattern=r"{v}回")
    b.add("inb.stores", comma(ist), ist, "店", B_INB, L_INB, SRC_I, pattern=r"{v}店")
    b.add("inb.cities", str(len(icities)), len(icities), "都市", B_INB, L_INB, "meo-research/data/inb_frame60.jsonl")
    b.add("inb.industries", str(len(iinds)), len(iinds), "業種", B_INB, L_INB, "meo-research/data/inb_frame60.jsonl")
    t1 = {r[0]: r for r in IT["1"]}
    for k in ("0", "1", "2", "3"):
        b.add(f"inb.care{k}_top10", t1[k][2], n_int(t1[k][2]), "%", B_INB, L_INB, SRC_I + f" 表1（英語の対策{k}個・英語で上位10）",
              pattern=r"{v}")
        b.add(f"inb.care{k}_n", comma(n_int(t1[k][1])), n_int(t1[k][1]), "店", B_INB, L_INB, SRC_I + f" 表1（英語の対策{k}個）")

    t3 = {r[0]: r for r in IT["3"]}
    for item, k in (("英語で返信している", "reply_en"), ("最新20件のうち30日以内", "n30")):
        r_ = t3[item]
        unit = "%" if r_[1].endswith("%") else "件"
        for col, side in ((1, "top"), (2, "low")):
            v = r_[col]
            b.add(f"inb.cared.{k}_{side}", v if unit == "%" else f"{int(n_float(v))}件", n_float(v), unit, B_INB + "（英語の対策を2つ以上している店・上位597店／下位448店）",
                  L_INB, SRC_I + f" 表3（{item}）")

    # 5) AI（ai_visibility.py → ai_vis_latest.md・ai_vis_raw.jsonl）
    ai = os.path.join(DATA, "ai_vis_latest.md")
    txt = open(ai, encoding="utf-8").read()
    m = re.search(r"聞いた回数\s*(\d+)回／都市×業種\s*(\d+)組／対象の店\s*(\d+)店／モデル\s*(\S+)／([\d-]+)", txt)
    aq, ap, ast_, amodel, aat = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4), m.group(5)
    B_AI = f"AIへの質問（ChatGPT {amodel}・ウェブ検索つき・4言語で{aq}回・{ap}組・{ast_}店・{aat}）"
    L_AI = f"ChatGPTに{aq}回聞いた調査"
    SRC_A = "meo-research/ai_visibility.py → data/ai_vis_latest.md"
    b.add("ai.questions", str(aq), aq, "回", B_AI, L_AI, SRC_A, at=aat, pattern=r"{v}回")
    b.add("ai.pairs", str(ap), ap, "組", B_AI, L_AI, SRC_A, at=aat)
    b.add("ai.stores", str(ast_), ast_, "店", B_AI, L_AI, SRC_A, at=aat, pattern=r"{v}店")
    rows_ai = {}
    for line in txt.splitlines():
        if line.startswith("| ") and "%" in line:
            c = [x.strip() for x in line.strip("|").split("|")]
            rows_ai[c[0]] = c[1:]
    langs = ["en", "ja", "ko", "zh"]
    def ai_cell(name, lang):
        return n_int(rows_ai[name][langs.index(lang)].split("%")[0])
    for lang in langs:
        b.add(f"ai.all_{lang}", f"{ai_cell('全部の店', lang)}%", ai_cell("全部の店", lang), "%", B_AI, L_AI, SRC_A + f"（全部の店・{lang}で聞いた）", at=aat)
    alls = [ai_cell("全部の店", lang) for lang in langs]
    b.add("ai.all_range", f"{min(alls)}〜{max(alls)}%", None, "%", B_AI, L_AI, SRC_A + "（全部の店・4言語で聞いたときの幅）", at=aat)
    for lang in ("en", "ja"):
        b.add(f"ai.top10_{lang}", f"{ai_cell('日本語のGoogleマップで上位10', lang)}%", ai_cell("日本語のGoogleマップで上位10", lang), "%", B_AI, L_AI,
              SRC_A + f"（日本語のGoogleマップで上位10の店・{lang}で聞いた）", at=aat)
        b.add(f"ai.rest_{lang}", f"{ai_cell('日本語で11位以下', lang)}%", ai_cell("日本語で11位以下", lang), "%", B_AI, L_AI,
              SRC_A + f"（日本語で11位以下の店・{lang}で聞いた）", at=aat)
    dom = collections.Counter()
    for r in read_jsonl(os.path.join(DATA, "ai_vis_raw.jsonl")):
        for u in r.get("urls") or []:
            mm = re.match(r"https?://(?:www\.)?([^/]+)", u or "")
            if mm:
                dom[mm.group(1)] += 1
    gm = sum(v for k, v in dom.items() if re.match(r"(maps\.google|google\.[a-z.]+$|maps\.app\.goo\.gl)", k))
    b.add("ai.sources", str(sum(dom.values())), sum(dom.values()), "件", B_AI, L_AI, SRC_A + "（答えの出典URLの数）", at=aat, pattern=r"{v}件")
    b.add("ai.sources_tabelog", str(dom.get("tabelog.com", 0)), dom.get("tabelog.com", 0), "回", B_AI, L_AI, SRC_A + "（出典が食べログ）", at=aat)
    b.add("ai.sources_gmaps", str(gm), gm, "回", B_AI, L_AI, SRC_A + "（出典がGoogleマップ）", at=aat)
    hpb = dom.get("beauty.hotpepper.jp", 0)
    b.add("ai.sources_hpb", str(hpb), hpb, "回", B_AI, L_AI, SRC_A + "（出典がホットペッパービューティー）", at=aat)

    # 4言語をまとめた割合（各言語の % × 店数 の合計 ÷ 店数の合計）。「4言語で75回」の文はこちら
    def ai_pooled(name):
        num = den = 0
        for cell in rows_ai[name]:
            mm = re.match(r"(\d+)%（([\d,]+)店）", cell)
            if mm:
                num += int(mm.group(1)) * n_int(mm.group(2))
                den += n_int(mm.group(2))
        return round(num / den) if den else 0
    for key, name, what in (("ai.top10_all", "日本語のGoogleマップで上位10", "日本語のGoogleマップで上位10の店"), ("ai.rest_all", "日本語で11位以下", "日本語で11位以下の店"),
                            ("ai.rv50_hi_all", "口コミ50件以上", "口コミ50件以上の店"), ("ai.rv50_lo_all", "口コミ50件未満", "口コミ50件未満の店")):
        v = ai_pooled(name)
        b.add(key, f"{v}%", v, "%", B_AI, L_AI, SRC_A + f"（{what}・4言語をまとめた割合）", at=aat)

    # 5b) 地方の市×業種（会長 2026-10-22 提案③「{市}の{業種}さん」・Threads の town 型が読む）
    town_facts(b, raw["detail"])

    # 6) 一回きりの集計（作る台本が無い・母数と出所と日付を書く）
    for key, f in FIXED.items():
        b.add(key, f["value"], f.get("num"), f.get("unit", ""), f["base"], f["label"], f["source"], kind="fixed", at=f["at"],
              pattern=f.get("pattern"), note=f.get("note"))
    return b.facts, {"result_head": head.strip(), "survey_stats_at": s["at"]}


# ── 一回きりの集計 ──────────────────────────────────────────────────────
OB = "Obsidian ✍️ 思考・下書き/"
B_INDIE = "日本語の全国調査のうち個人店13,804店（同じ屋号が3都市以上のチェーン680店を除く・2026-10-10 集計）"
SRC_INDIE = OB + "MEO_4980パック/18_全国5000店調査_結果_2026-10-10.md（集計の台本なし）"
B_TOP = "日本語の全国調査 14,504店を同じ都市×業種の中で数え直した集計（2026-10-12・340組）"
SRC_TOP = OB + "ToB発信ネタ帳_MEO.md N349〜N357（自社調査 14,504店・2026-10-12 再集計・集計の台本なし）"
L_JP_FIXED = "全国14,504店の調査"
B_RANK = "日本語の全国調査 14,491店（詳細を見られた店）を一覧の位置で分けた集計（1〜10位 3,390店・21位以下 7,712店・2026-10-24）"
L_RANK = "全国14,504店の調査"   # 外に出る文の店数は14,504に揃える（会長 2026-10-27「8を直して」・1つの文に2つの店数を出さない）
SRC_RANK = "meo-research/data/detail_*.jsonl を rank で分けて中央値（numbers_build.py FIXED jp.rank.*・2026-10-24）"
B_CNT = "日本語の全国調査 14,491店（詳細を見られた店）を一覧の星（list_rating）×口コミの数（list_reviews）で分けた集計（2026-10-25）"
SRC_CNT = "meo-research/data/detail_*.jsonl を list_rating と list_reviews で分けて rank の中央値と上位10の割合（numbers_build.py FIXED jp.cnt.*・2026-10-25）"
FIXED: dict[str, dict] = {
    # 10/24 一覧の位置（rank）で分けた状態（VIP の DM の1行・半年の約束の「上位10店の状態」が読む）
    "jp.rank.top10_photos": {"value": "155枚", "num": 155, "unit": "枚", "base": B_RANK, "label": L_RANK, "source": SRC_RANK + "（1〜10位の写真の枚数の中央値）", "at": "2026-10-24"},
    "jp.rank.low_photos": {"value": "95枚", "num": 95, "unit": "枚", "base": B_RANK, "label": L_RANK, "source": SRC_RANK + "（21位以下の写真の枚数の中央値）", "at": "2026-10-24"},
    "jp.rank.top10_reply": {"value": "50%", "num": 50, "unit": "%", "base": B_RANK, "label": L_RANK, "source": SRC_RANK + "（1〜10位の口コミ返信率の中央値）", "at": "2026-10-24"},
    "jp.rank.low_reply": {"value": "17%", "num": 17, "unit": "%", "base": B_RANK, "label": L_RANK, "source": SRC_RANK + "（21位以下の口コミ返信率の中央値）", "at": "2026-10-24"},
    # 10/25 星の高さ×口コミの数で分けた一覧の位置（会長 2026-10-24「悪い口コミを強みに」・Threads B・営業メール B・LP が読む）
    "jp.cnt.lo_many_pos": {"value": "31位", "num": 31, "unit": "位", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.0未満・口コミ300件以上 533店の位置の中央値）", "at": "2026-10-25"},
    "jp.cnt.lo_many_top10": {"value": "12%", "num": 12, "unit": "%", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.0未満・口コミ300件以上 533店のうち上位10に入る割合）", "at": "2026-10-25"},
    "jp.cnt.hi_few_pos": {"value": "33位", "num": 33, "unit": "位", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.5以上・口コミ30件未満 2,666店の位置の中央値）", "at": "2026-10-25"},
    "jp.cnt.hi_few_top10": {"value": "12%", "num": 12, "unit": "%", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.5以上・口コミ30件未満 2,666店のうち上位10に入る割合）", "at": "2026-10-25"},
    "jp.cnt.hi_many_pos": {"value": "9位", "num": 9, "unit": "位", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.5以上・口コミ300件以上 968店の位置の中央値）", "at": "2026-10-25"},
    "jp.cnt.hi_many_top10": {"value": "54%", "num": 54, "unit": "%", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.5以上・口コミ300件以上 968店のうち上位10に入る割合）", "at": "2026-10-25"},
    "jp.cnt.mid_few_pos": {"value": "39位", "num": 39, "unit": "位", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.0〜4.5・口コミ30件未満 563店の位置の中央値）", "at": "2026-10-25"},
    "jp.cnt.mid_many_pos": {"value": "16位", "num": 16, "unit": "位", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.0〜4.5・口コミ300件以上 1,582店の位置の中央値）", "at": "2026-10-25"},
    "jp.cnt.mid_few_top10": {"value": "6%", "num": 6, "unit": "%", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.0〜4.5・口コミ30件未満 563店のうち上位10に入る割合）", "at": "2026-10-25"},
    "jp.cnt.mid_many_top10": {"value": "35%", "num": 35, "unit": "%", "base": B_CNT, "label": L_RANK, "source": SRC_CNT + "（星4.0〜4.5・口コミ300件以上 1,582店のうち上位10に入る割合）", "at": "2026-10-25"},
    # 10/10 個人店13,804店
    "jp.indie": {"value": "13,804", "num": 13804, "unit": "店", "base": B_INDIE, "label": "個人店13,804店", "source": SRC_INDIE, "at": "2026-10-10", "pattern": r"{v}店"},
    "jp.grow.post_fast": {"value": "53%", "num": 53, "unit": "%", "base": B_INDIE + "のうち月3件以上の1,897店・月1件未満の9,135店",
                          "label": L_JP_FIXED, "source": SRC_INDIE + " §7・ネタ N307", "at": "2026-10-10", "pattern": r"{v}[^。\n]{0,20}5%"},
    "jp.grow.post_slow": {"value": "5%", "num": 5, "unit": "%", "base": B_INDIE + "のうち月1件未満の9,135店", "label": L_JP_FIXED, "source": SRC_INDIE + " §7・ネタ N307", "at": "2026-10-10"},
    "jp.grow.fast_n": {"value": "1,897", "num": 1897, "unit": "店", "base": B_INDIE, "label": L_JP_FIXED, "source": SRC_INDIE + " §7", "at": "2026-10-10", "pattern": r"{v}店"},
    "jp.grow.slow_n": {"value": "9,135", "num": 9135, "unit": "店", "base": B_INDIE, "label": L_JP_FIXED, "source": SRC_INDIE + " §7", "at": "2026-10-10", "pattern": r"{v}店"},
    "jp.floor.n": {"value": "2,475", "num": 2475, "unit": "店", "base": B_INDIE + "のうち住所に階が書いてある2,475店（1階1,035店・2階以上1,440店）",
                   "label": L_JP_FIXED, "source": SRC_INDIE + " §7・ネタ N314", "at": "2026-10-10", "pattern": r"{v}店"},
    "jp.floor.pace": {"value": "0.6", "num": 0.6, "unit": "件/月", "base": B_INDIE + "のうち住所に階が書いてある2,475店", "label": L_JP_FIXED, "source": SRC_INDIE + " §7・ネタ N314", "at": "2026-10-10"},
    "jp.floor.up_fast_nonlg": {"value": "91%", "num": 91, "unit": "%", "base": B_INDIE + "のうち2階以上で伸びている174店（口コミのうちローカルガイド以外の割合）",
                               "label": L_JP_FIXED, "source": SRC_INDIE + " §7・ネタ N315", "at": "2026-10-10"},
    "jp.floor.up_slow_nonlg": {"value": "72%", "num": 72, "unit": "%", "base": B_INDIE + "のうち2階以上で止まっている店（口コミのうちローカルガイド以外の割合）",
                               "label": L_JP_FIXED, "source": SRC_INDIE + " §7・ネタ N315", "at": "2026-10-10"},
    "jp.desc.pos_yes": {"value": "23位", "num": 23, "unit": "位", "base": B_INDIE + "（紹介文あり4,122店／なし9,682店）", "label": L_JP_FIXED, "source": SRC_INDIE + " ⑩・ネタ N319", "at": "2026-10-10"},
    "jp.desc.pos_no": {"value": "24位", "num": 24, "unit": "位", "base": B_INDIE + "（紹介文あり4,122店／なし9,682店）", "label": L_JP_FIXED, "source": SRC_INDIE + " ⑩・ネタ N319", "at": "2026-10-10"},
    "jp.open1y.n": {"value": "309", "num": 309, "unit": "店", "base": B_INDIE + "のうち開業1年以内（最古の口コミが365日以内）の309店", "label": "開業1年以内の309店", "source": SRC_INDIE + " §8", "at": "2026-10-10", "pattern": r"{v}店"},
    "jp.open1y.reply7_top": {"value": "73%", "num": 73, "unit": "%", "base": "開業1年以内の個人店309店（上位10%＝30店）", "label": "開業1年以内の309店", "source": SRC_INDIE + " §8", "at": "2026-10-10"},
    "jp.open1y.reply7_rest": {"value": "53%", "num": 53, "unit": "%", "base": "開業1年以内の個人店309店（それ以外279店）", "label": "開業1年以内の309店", "source": SRC_INDIE + " §8", "at": "2026-10-10"},
    "jp.open1y.reserve_top": {"value": "50%", "num": 50, "unit": "%", "base": "開業1年以内の個人店309店（上位10%＝30店）", "label": "開業1年以内の309店", "source": SRC_INDIE + " §8", "at": "2026-10-10"},
    "jp.open1y.reserve_rest": {"value": "44%", "num": 44, "unit": "%", "base": "開業1年以内の個人店309店（それ以外279店）", "label": "開業1年以内の309店", "source": SRC_INDIE + " §8", "at": "2026-10-10"},
    # 10/12 上位10%の再集計（N349〜N357）
    "top.first_reviews": {"value": "234件", "num": 234, "unit": "件", "base": B_TOP, "label": L_JP_FIXED, "source": SRC_TOP + " N349", "at": "2026-10-12", "pattern": r"{v}[^。\n]{0,6}74件"},
    "top.last_reviews": {"value": "74件", "num": 74, "unit": "件", "base": B_TOP, "label": L_JP_FIXED, "source": SRC_TOP + " N349", "at": "2026-10-12"},
    "top.rv_low_pos": {"value": "75%", "num": 75, "unit": "%", "base": B_TOP + "（口コミ件数の下位1割・15件以下・1,443店）", "label": L_JP_FIXED, "source": SRC_TOP + " N350", "at": "2026-10-12"},
    "top.rv_high_pos": {"value": "33%", "num": 33, "unit": "%", "base": B_TOP + "（口コミ件数の上位1割・603件以上・1,443店）", "label": L_JP_FIXED, "source": SRC_TOP + " N350", "at": "2026-10-12"},
    "top.pace_high_pos": {"value": "35%", "num": 35, "unit": "%", "base": B_TOP + "（新しい口コミが月5件以上の上位1割）", "label": L_JP_FIXED, "source": SRC_TOP + " N351", "at": "2026-10-12",
                          "pattern": r"{v}[^。\n]{0,30}72%"},
    "top.pace_low_pos": {"value": "72%", "num": 72, "unit": "%", "base": B_TOP + "（新しい口コミが月1件未満の下位1割）", "label": L_JP_FIXED, "source": SRC_TOP + " N351", "at": "2026-10-12"},
    "top.pace_high_in": {"value": "17%", "num": 17, "unit": "%", "base": B_TOP + "（月5件以上の店が上位10%に入る割合）", "label": L_JP_FIXED, "source": SRC_TOP + " N351", "at": "2026-10-12"},
    "top.pace_low_in": {"value": "3%", "num": 3, "unit": "%", "base": B_TOP + "（月1件未満の店が上位10%に入る割合）", "label": L_JP_FIXED, "source": SRC_TOP + " N351", "at": "2026-10-12"},
    "top.post_top": {"value": "18%", "num": 18, "unit": "%", "base": B_TOP + "（上位10% 1,566店）", "label": L_JP_FIXED, "source": SRC_TOP + " N352", "at": "2026-10-12"},
    "top.post_rest": {"value": "14%", "num": 14, "unit": "%", "base": B_TOP + "（それ以外 12,938店）", "label": L_JP_FIXED, "source": SRC_TOP + " N352", "at": "2026-10-12"},
    "top.photo10_top": {"value": "79%", "num": 79, "unit": "%", "base": B_TOP + "（上位10% 1,566店）", "label": L_JP_FIXED, "source": SRC_TOP + " N352", "at": "2026-10-12"},
    "top.photo10_rest": {"value": "78%", "num": 78, "unit": "%", "base": B_TOP + "（それ以外 12,938店）", "label": L_JP_FIXED, "source": SRC_TOP + " N352", "at": "2026-10-12"},
    "top.reply_zero_pos": {"value": "60%", "num": 60, "unit": "%", "base": B_TOP + "（最新20件に返信ゼロの6,440店）", "label": L_JP_FIXED, "source": SRC_TOP + " N353", "at": "2026-10-12",
                           "pattern": r"{v}[^。\n]{0,20}47%"},
    "top.reply_all_pos": {"value": "47%", "num": 47, "unit": "%", "base": B_TOP + "（最新20件の全部に返信している4,149店）", "label": L_JP_FIXED, "source": SRC_TOP + " N353", "at": "2026-10-12"},
    "top.star_high_pos": {"value": "45%", "num": 45, "unit": "%", "base": B_TOP + "（星4.6〜4.8の4,146店）", "label": L_JP_FIXED, "source": SRC_TOP + " N354", "at": "2026-10-12"},
    "top.star_low_pos": {"value": "65%", "num": 65, "unit": "%", "base": B_TOP + "（星4.2以下の3,915店）", "label": L_JP_FIXED, "source": SRC_TOP + " N354", "at": "2026-10-12"},
    "top.all3_pos": {"value": "40%", "num": 40, "unit": "%", "base": B_TOP + "（月3件以上＋返信あり＋投稿ありの439店）", "label": L_JP_FIXED, "source": SRC_TOP + " N355", "at": "2026-10-12"},
    "top.none3_pos": {"value": "65%", "num": 65, "unit": "%", "base": B_TOP + "（どれも無い4,177店）", "label": L_JP_FIXED, "source": SRC_TOP + " N355", "at": "2026-10-12"},
    "top.all3_in": {"value": "14%", "num": 14, "unit": "%", "base": B_TOP + "（439店）", "label": L_JP_FIXED, "source": SRC_TOP + " N355", "at": "2026-10-12"},
    "top.none3_in": {"value": "5%", "num": 5, "unit": "%", "base": B_TOP + "（4,177店）", "label": L_JP_FIXED, "source": SRC_TOP + " N355", "at": "2026-10-12"},
    "top.reply_share": {"value": "56%", "num": 56, "unit": "%", "base": B_TOP + "（8,064／14,438店）", "label": L_JP_FIXED, "source": SRC_TOP + " N357", "at": "2026-10-12",
                        "note": "最新の表E（jp.reply.yes_share）と同じ事実の古い集計。新しい文には jp.reply.yes_share を使う"},
    # 9/27 全国218店（Google投稿）
    "post218.n": {"value": "218", "num": 218, "unit": "店", "base": "Google投稿の全国調査 218店（2026-09-27）", "label": "全国218店の調査",
                  "source": OB + "ToB発信ネタ帳_MEO.md N086・N221（Google投稿_全国調査_2026-09-27.md）", "at": "2026-09-27", "pattern": r"{v}店"},
    "post218.shown": {"value": "34%", "num": 34, "unit": "%", "base": "Google投稿の全国調査 218店（2026-09-27）", "label": "全国218店の調査", "source": OB + "ToB発信ネタ帳_MEO.md N086", "at": "2026-09-27"},
    "post218.d30": {"value": "22%", "num": 22, "unit": "%", "base": "Google投稿の全国調査 218店（2026-09-27）", "label": "全国218店の調査", "source": OB + "ToB発信ネタ帳_MEO.md N086", "at": "2026-09-27"},
    "post218.d7": {"value": "17%", "num": 17, "unit": "%", "base": "Google投稿の全国調査 218店（2026-09-27）", "label": "全国218店の調査", "source": OB + "ToB発信ネタ帳_MEO.md N086", "at": "2026-09-27",
                   "pattern": r"7日以内[^。\n]{0,20}{v}", "note": "「14,504店で」と書かない（218店の調査・F7）"},
    # 9/27 同時期開業のカフェ（記録149店→比べたのは132店）
    "cafe132.n": {"value": "132", "num": 132, "unit": "店", "base": "同じ時期（約7か月前）に開業したカフェ 132店（記録149店から別店・閉業を除く・2026-09-27）",
                  "label": "同じ時期に開業したカフェ132店", "source": OB + "ToB発信ネタ帳_MEO.md N222・N096〜N104（同時期開業_人気店と停滞店_比較調査_2026-09-27.md）", "at": "2026-09-27",
                  "pattern": r"カフェ[^。\n]{0,6}{v}店", "note": "比べた店数は132店。149店は記録した数（F11）"},
    "cafe132.recorded": {"value": "149", "num": 149, "unit": "店", "base": "同じ時期に開業したカフェを記録した数（2026-09-27）", "label": "記録したカフェ149店",
                         "source": OB + "ToB発信ネタ帳_MEO.md N222", "at": "2026-09-27", "note": "調べ方の文（149店を記録し132店で比べた）だけに使う"},
    "cafe132.gap": {"value": "30倍", "num": 30, "unit": "倍", "base": "同じ時期に開業したカフェ132店（人気 月18.1件／停滞 月0.5件・中央値）", "label": "同じ時期に開業したカフェ132店",
                    "source": OB + "ToB発信ネタ帳_MEO.md N096", "at": "2026-09-27"},
    "cafe132.hot_pace": {"value": "18.1", "num": 18.1, "unit": "件/月", "base": "同じ時期に開業したカフェ132店のうち人気店（新しい口コミ・月あたり中央値）", "label": "同じ時期に開業したカフェ132店",
                         "source": OB + "ToB発信ネタ帳_MEO.md N096", "at": "2026-09-27"},
    "cafe132.cold_pace": {"value": "0.5", "num": 0.5, "unit": "件/月", "base": "同じ時期に開業したカフェ132店のうち停滞店（新しい口コミ・月あたり中央値）", "label": "同じ時期に開業したカフェ132店",
                          "source": OB + "ToB発信ネタ帳_MEO.md N096", "at": "2026-09-27"},
    "cafe132.star": {"value": "4.8", "num": 4.8, "unit": "星", "base": "同じ時期に開業したカフェ132店（人気店・停滞店とも中央値4.8）", "label": "同じ時期に開業したカフェ132店",
                     "source": OB + "ToB発信ネタ帳_MEO.md N097", "at": "2026-09-27"},
    "cafe132.cold_limited": {"value": "29%", "num": 29, "unit": "%", "base": "同じ時期に開業したカフェ132店のうち停滞店（営業日が限られる店＝間借り・週2〜3日・不定期など・7店）", "label": "同じ時期に開業したカフェ132店",
                             "source": OB + "ToB発信ネタ帳_MEO.md N105", "at": "2026-09-27"},
    "cafe132.cold_quiet90": {"value": "29%", "num": 29, "unit": "%", "base": "同じ時期に開業したカフェ132店のうち停滞店（直近90日に口コミが1件もない店）", "label": "同じ時期に開業したカフェ132店",
                             "source": OB + "ToB発信ネタ帳_MEO.md N123", "at": "2026-09-27"},
    # 9/28 2階以上のカフェ（記録399店→集計381店）
    "upcafe.n": {"value": "381", "num": 381, "unit": "店", "base": "2階以上のカフェの調査（全国20都市・記録399店から集計381店・2026-09）", "label": "全国381店（2階以上のカフェ）",
                 "source": OB + "ToB発信ネタ帳_MEO.md B-7・N223（das 2階以上カフェ_全国調査・20都市）", "at": "2026-09-28", "pattern": r"{v}店"},
    # 10/16 観光地 日本語上位10 → 英語で消える
    "inb.ja10_n": {"value": "688", "num": 688, "unit": "軒", "base": "観光地の日英調査のうち、日本語で上位10に入る地方のお店（2026-10-16 の集計）", "label": "観光地の688軒",
                   "source": OB + "MEO_4980パック/04_note追加章_英語の画面とAI_2026-10-16.md（集計の台本なし・inb_frame.jsonl から658軒／331軒になり再現できない）", "at": "2026-10-16", "pattern": r"{v}軒"},
    "inb.ja10_lost": {"value": "335", "num": 335, "unit": "軒", "base": "観光地の688軒（日本語で上位10）のうち英語で上位10に入らない店", "label": "観光地の688軒",
                      "source": OB + "MEO_4980パック/04_note追加章_英語の画面とAI_2026-10-16.md", "at": "2026-10-16", "pattern": r"{v}軒"},
    "inb.reply_total": {"value": "13,244", "num": 13244, "unit": "件", "base": "観光地の日英調査で読んだ地方のお店の口コミ返信（2026-10-12〜13）", "label": "地方のお店の返信13,244件",
                        "source": OB + "ToB発信ネタ帳_MEO.md N369（inb_detail60.jsonl・集計の台本なし）", "at": "2026-10-13", "pattern": r"{v}件"},
    "inb.reply_translated": {"value": "1,402", "num": 1402, "unit": "件", "base": "地方のお店の返信13,244件のうち英語に訳されて出たもの（2026-10-12〜13）", "label": "地方のお店の返信13,244件",
                             "source": OB + "ToB発信ネタ帳_MEO.md N369", "at": "2026-10-13", "pattern": r"{v}件"},
    "inb.post30_base": {"value": "2,207", "num": 2207, "unit": "軒", "base": "観光地の日英調査で英語の画面を開いた地方のお店（2026-10-12〜13）", "label": "地方のお店2,207軒",
                        "source": OB + "ToB発信ネタ帳_MEO.md N371（inb_detail60.jsonl・集計の台本なし）", "at": "2026-10-13", "pattern": r"{v}軒"},
    "inb.post30_en": {"value": "56", "num": 56, "unit": "軒", "base": "地方のお店2,207軒のうち、30日以内に英語でお知らせを出していた店", "label": "地方のお店2,207軒",
                      "source": OB + "ToB発信ネタ帳_MEO.md N371", "at": "2026-10-13"},
    # 10/12 上位10%の再集計 N350（口コミ件数で10等分）
    "top.rv_low_in": {"value": "2%", "num": 2, "unit": "%", "base": B_TOP + "（口コミ件数の下位1割・15件以下の店が上位10%に入る割合）", "label": L_JP_FIXED, "source": SRC_TOP + " N350・hitotsunagi-hq/knowledge/DECISIONS.md D20261012-2800", "at": "2026-10-12"},
    "top.rv_high_in": {"value": "17%", "num": 17, "unit": "%", "base": B_TOP + "（口コミ件数の上位1割・603件以上の店が上位10%に入る割合）", "label": L_JP_FIXED, "source": SRC_TOP + " N350・hitotsunagi-hq/knowledge/DECISIONS.md D20261012-2800", "at": "2026-10-12"},
    "top.rv_low_cut": {"value": "15件", "num": 15, "unit": "件", "base": B_TOP + "（口コミ件数の下位1割の上限）", "label": L_JP_FIXED, "source": SRC_TOP + " N350", "at": "2026-10-12"},
    "top.rv_high_cut": {"value": "603件", "num": 603, "unit": "件", "base": B_TOP + "（口コミ件数の上位1割の下限）", "label": L_JP_FIXED, "source": SRC_TOP + " N350", "at": "2026-10-12"},
    # 9/28 2階以上のカフェ 381店：公式サイトのリンク
    "upcafe.link_hi": {"value": "57%", "num": 57, "unit": "%", "base": "2階以上のカフェの調査 381店のうち口コミ300件以上の店（公式サイトのリンクあり・2026-09）", "label": "全国381店（2階以上のカフェ）",
                       "source": OB + "MEO_4980パック/16_期待値の根拠_2026-10-09.md（公式リンク）・ToB発信ネタ帳_MEO.md N118", "at": "2026-09-28"},
    "upcafe.link_lo": {"value": "28%", "num": 28, "unit": "%", "base": "2階以上のカフェの調査 381店のうち口コミ30件未満の店（公式サイトのリンクあり・2026-09）", "label": "全国381店（2階以上のカフェ）",
                       "source": OB + "MEO_4980パック/16_期待値の根拠_2026-10-09.md（公式リンク）・ToB発信ネタ帳_MEO.md N118・SNS日次ログ.md 20261006-S-02", "at": "2026-09-28"},
    # 10/17 観光地 日本語上位10 の英字の店名
    "inb.ja10_all": {"value": "1,828", "num": 1828, "unit": "軒", "base": "観光地の日英調査で日本語の上位10に入る店（2026-10-17 の集計）", "label": "観光地の1,828軒",
                     "source": "hitotsunagi-hq/knowledge/DECISIONS.md D20261017-1200（集計の台本なし）", "at": "2026-10-17", "pattern": r"{v}軒"},
    "inb.latin_no_top10": {"value": "31%", "num": 31, "unit": "%", "base": "観光地の1,828軒のうち英語の画面で英字で出ない464軒が英語の上位10に入る割合（143軒）", "label": "観光地の1,828軒",
                           "source": "hitotsunagi-hq/knowledge/DECISIONS.md D20261017-1200（集計の台本なし）", "at": "2026-10-17"},
    "inb.latin_yes_top10": {"value": "56%", "num": 56, "unit": "%", "base": "観光地の1,828軒のうち英字で出る1,364軒が英語の上位10に入る割合", "label": "観光地の1,828軒",
                            "source": "hitotsunagi-hq/knowledge/DECISIONS.md D20261017-1200（集計の台本なし）", "at": "2026-10-17"},
    # 10/01 AI検索（3つのAIに22問×66回）
    "ai66.asked": {"value": "66", "num": 66, "unit": "回", "base": "3つのAI検索に同じ22問ずつ計66回（2026-10-01）", "label": "AI検索66回の調査", "source": OB + "ToB発信ネタ帳_MEO.md N227・N165", "at": "2026-10-01"},
    "ai66.name_hit": {"value": "26", "num": 26, "unit": "回", "base": "店名や店の事実を聞いた30回（2026-10-01）", "label": "AI検索66回の調査", "source": OB + "ToB発信ネタ帳_MEO.md N165", "at": "2026-10-01"},
}

# 前から写しに残っている古い値（この版より前の正本の値）。fix=false は意味ごと違うので --fix で置き換えない
SEED_HISTORY: dict[str, list[dict]] = {
    "jp.searches": [{"value": "339", "until": "2026-10-18", "base": "手書きの写し（frame.jsonl の検索語は68都市×5業種＝340）", "fix": True}],
    "jp.reviews": [{"value": "3,517,404", "until": "2026-10-18", "base": "2026-10-12 再集計（N356・detail の list_reviews の合計と見られる）", "fix": True}],
    "jp.reviews_man": [{"value": "351万", "until": "2026-10-18", "base": "2026-10-12 再集計（N356）", "fix": True}],
    "jp.detail": [{"value": "14,484", "until": "2026-10-18", "base": "result_latest.md 2026-10-10 版（詳細14,484店）", "fix": True}],
    "jp.holiday.unconfirmed_share": [{"value": "77%", "until": "2026-10-18", "base": "個人店13,543店（2026-10-10 集計・10,525店）", "fix": True}],
    "jp.holiday.unconfirmed_n": [{"value": "10,525", "until": "2026-10-18", "base": "個人店13,543店（2026-10-10 集計）", "fix": True}],
    "jp.holiday.confirmed_n": [{"value": "3,114", "until": "2026-10-18", "base": "result_latest.md 2026-10-10 版（表G「祝日の設定なし」＝本当は表示なし＝確かめ済みの店）", "fix": False,
                                "note": "「祝日の設定なし3,114店」は向きが逆。jp.holiday.unconfirmed_share（未確認の割合）の文に書き直す"},
                               {"value": "3,018", "until": "2026-10-18", "base": "個人店13,543店（2026-10-10 集計）", "fix": True}],
    "jp.reply.seitai_no_n": [{"value": "507", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計・N310）", "fix": True}],
    "jp.reply.seitai_yes_n": [{"value": "2,667", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計・N310）", "fix": True}],
    "jp.reply.fast_n": [{"value": "6,278", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計・N311）", "fix": True}],
    "jp.reply.slow_n": [{"value": "650", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計・N311）", "fix": True}],
    "jp.speed.lt1_n": [{"value": "9,135", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計・N308）", "fix": False,
                        "note": "9,135 は jp.grow.slow_n（個人店・53%/5% の母数）でもある。置き換えは文で判断"}],
    "jp.speed.1to5_n": [{"value": "3,139", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計・N308）", "fix": True}],
    "jp.speed.ge5_n": [{"value": "1,438", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計・N308）", "fix": True}],
    "jp.photo.hi_reviews": [{"value": "206件", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計・5,798店）", "fix": True}],
    "jp.photo.hi_n": [{"value": "5,798", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計）", "fix": True}],
    "jp.photo.lo_n": [{"value": "1,959", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計）", "fix": True}],
    "jp.photo200.share.seitai": [{"value": "9%", "until": "2026-10-18", "base": "src/meo_photo200.py の手書き（13,657店・再現できない）", "fix": False}],
    "jp.photo200.share.biyou": [{"value": "17%", "until": "2026-10-18", "base": "src/meo_photo200.py の手書き（13,657店・再現できない）", "fix": False}],
    "jp.photo200.share.izakaya": [{"value": "56%", "until": "2026-10-18", "base": "src/meo_photo200.py の手書き（13,657店・再現できない）", "fix": False}],
    "jp.photo200.share.cafe": [{"value": "57%", "until": "2026-10-18", "base": "src/meo_photo200.py の手書き（13,657店・再現できない）", "fix": False}],
    "jp.photo200.share.ramen": [{"value": "78%", "until": "2026-10-18", "base": "src/meo_photo200.py の手書き（13,657店・再現できない）", "fix": False}],
    "jp.photo200.range": [{"value": "9〜78%", "until": "2026-10-18", "base": "src/meo_photo200.py の手書き（13,657店）", "fix": True}],
    "jp.photo.base_n": [{"value": "13,657", "until": "2026-10-18", "base": "src/meo_photo200.py の手書き（再現できない）", "fix": True}],
    "cafe132.n": [{"value": "149", "until": "2026-10-18", "base": "記録した数（比べたのは132店）", "fix": False,
                   "note": "比べた結果の文では132店。調べ方の文（149店を記録）だけ cafe132.recorded"}],
    "ai.questions": [{"value": "31", "until": "2026-10-18", "base": "survey_stats.json の ai_questions（2026-10-16 途中）", "fix": False}],
    "jp.access.slow": [{"value": "5.3%", "until": "2026-10-18", "base": "result_latest.md 2026-10-10 版", "fix": True}],
    "jp.post.share.cafe": [{"value": "24%", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計）", "fix": False}],
    "jp.post.share.seitai": [{"value": "1%", "until": "2026-10-18", "base": "個人店13,804店（2026-10-10 集計）", "fix": False}],
}


def merge_history(old: dict, new_facts: dict, seed_old_facts: dict | None) -> dict:
    hist = {k: list(v) for k, v in (old.get("history") or {}).items()}

    def push(k, entry):
        lst = hist.setdefault(k, [])
        if entry["value"] == new_facts[k]["value"]:
            return
        if any(e["value"] == entry["value"] for e in lst):
            return
        lst.append(entry)

    for k, lst in SEED_HISTORY.items():
        if k in new_facts:
            for e in lst:
                push(k, dict(e))
    for src in (seed_old_facts or {}), (old.get("facts") or {}):
        for k, f in src.items():
            if k in new_facts and f.get("value") != new_facts[k]["value"]:
                push(k, {"value": f["value"], "until": TODAY, "base": f.get("base", ""), "fix": True})
    return {k: v for k, v in hist.items() if v}


def run(cmd: list[str], out: str | None = None) -> None:
    if out:
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            subprocess.run(cmd, cwd=HERE, stdout=fh, check=True)
        os.replace(tmp, out)
    else:
        subprocess.run(cmd, cwd=HERE, check=True, stdout=subprocess.DEVNULL)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-run", action="store_true", help="analyze.py・survey_stats.py を回し直さない")
    ap.add_argument("--seed-old", help="前の版の result_latest.md（値が変わった事実を history に入れる）")
    a = ap.parse_args()
    if not a.no_run:
        run([sys.executable, "analyze.py"], os.path.join(DATA, "result_latest.md"))
        run([sys.executable, "survey_stats.py"])
    facts, meta = build()
    seed = None
    if a.seed_old:
        # 前の版の表で作り直し、変わった値を history に（表から作る事実だけ）
        cur = os.path.join(DATA, "result_latest.md")
        bak = cur + ".numbers_build_bak"
        os.replace(cur, bak)
        try:
            import shutil
            shutil.copy(a.seed_old, cur)
            seed, _ = build()
        finally:
            os.replace(bak, cur)
    old = {}
    if os.path.exists(OUT_MAIN):
        old = json.load(open(OUT_MAIN, encoding="utf-8"))
    out = {k: v for k, v in old.items() if k not in ("meta", "facts", "history")}    # offer など他の人の欄はそのまま
    out["meta"] = {"built_at": datetime.now().isoformat(timespec="seconds"), "builder": "meo-research/numbers_build.py",
                   "rule": "店に見せる調査の数字はここだけから読む（src/numbers.py）。結果の数字は label の母数で書き、合計の店数（total.stores）を母数にしない。"
                           "変えるのは meo-research で numbers_build.py を回すことだけ（手で書き換えない・fixed は一回きりの集計を書き写した物）",
                   **meta}
    out["facts"] = dict(sorted(facts.items()))
    out["history"] = dict(sorted(merge_history(old, facts, seed).items()))
    js = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    for p in (OUT_MAIN, OUT_COPY):
        tmp = p + ".tmp"
        open(tmp, "w", encoding="utf-8").write(js)
        os.replace(tmp, p)
    print(f"{len(facts)} facts（fixed {sum(1 for f in facts.values() if f['kind'] == 'fixed')}）・history {len(out['history'])} keys → {OUT_MAIN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
