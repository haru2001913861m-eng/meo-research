# -*- coding: utf-8 -*-
"""LINE の「英語の順位」依頼を拾って調べ、LINE で返す（Mac・launchd で10分ごと）。
依頼の置き場: Notion「💬 MEO LINE 状態」の状態JSON の en_req（Railway の meo_bot が書く）。
  en_req = {"status": "pending", "id": "<日時>", "text": "店名 町", "industry": "寿司", "town": "町"}
済んだ依頼は data/en_rank_done.json に id で残す（同じ依頼に2回返さない）。結果は data/en_rank_log.jsonl。
実行: python3 en_rank_watch.py [--dry]   … --dry は LINE に送らず表示だけ
"""
from __future__ import annotations
import fcntl, json, os, sys, time
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("GMAPS_PROFILE", os.path.join(HERE, ".gprofile"))
import en_rank  # noqa: E402
SA = os.path.expanduser("~/sales-automation")
sys.path.insert(0, SA); os.chdir(SA)
import config  # noqa: E402
import requests  # noqa: E402
from src.notion_client import get_client  # noqa: E402

DRY = "--dry" in sys.argv
DONE = os.path.join(HERE, "data", "en_rank_done.json")
LOG = os.path.join(HERE, "data", "en_rank_log.jsonl")
LOCK = os.path.join(HERE, "data", "en_rank_watch.lock")
TRIES = os.path.join(HERE, "data", "en_rank_tries.json")   # 送れなかった回数（依頼ごと）。MAX_TRIES で止めて会長へ（2026-10-23: 鍵が無く41回やり直し続けた）
MAX_TRIES = 3
LOGIN_NEEDED = os.path.join(HERE, "data", "line_login_needed")   # 読み取り用 Chrome のログイン切れの印。line_login.py が消すまで実物を開かない（2026-10-26: 2分ごとに溝井歯科医院の画面が会長の画面に出続けた）


def pending() -> list[tuple[str, dict]]:
    n = get_client(); since = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    out, cursor = [], None
    while True:
        kw = {"database_id": config.MEO_STATE_DB_ID, "page_size": 100,
              "filter": {"property": "更新", "date": {"on_or_after": since}}}
        if cursor:
            kw["start_cursor"] = cursor
        res = n.databases.query(**kw)
        for p in res["results"]:
            uid = "".join(t["plain_text"] for t in p["properties"]["ユーザーID"]["title"])
            raw = "".join(t["plain_text"] for t in p["properties"]["状態JSON"]["rich_text"])
            try:
                s = json.loads(raw)
            except Exception:
                continue
            quiet = s.get("hold") or s.get("blocked")   # hold＝会長が「何も送らない」と決めた人（2026-10-26 溝井歯科医院）
            q = s.get("detail_req") or {}   # 実物の読み取り（説明文・最新の口コミ・返事・オーナー確認）・2026-10-26。送るかは本番が決める（hold の人には送らない）
            if q.get("status") == "pending" and q.get("place_id"):
                out.append((uid, {**q, "kind": "detail"}))
            if quiet:   # ここから下は Mac が店に直接送る依頼
                continue
            q = s.get("en_req") or {}
            if q.get("status") == "pending" and q.get("text"):
                out.append((uid, q))
            q = s.get("screens_req") or {}   # 無料点検の残り2つの画面（英語の地図・AI）・2026-10-17
            if q.get("status") == "pending" and q.get("text"):
                out.append((uid, {**q, "kind": "screens"}))
        if not res.get("has_more"):
            return out
        cursor = res["next_cursor"]


def detail_one(uid: str, q: dict) -> tuple[dict, bool]:
    """実物を読み（line_detail.measure）、本番の /meo/detail-result に渡す。本番が店に送る。(結果, 済んだか)"""
    import hashlib, hmac
    import line_detail
    m = line_detail.measure(q["place_id"], q.get("shop") or "")
    if not m.get("ok"):
        return {"ok": False, "why": m.get("why")}, False
    body = json.dumps({"user_id": uid, "id": q["id"], "obs": m["obs"], "limited": m.get("limited")}, ensure_ascii=False).encode("utf-8")
    if DRY:
        print(body.decode()); return {**m, "result": "dry"}, True
    sig = hmac.new(config.MEO_LINE_CHANNEL_ACCESS_TOKEN.encode(), body, hashlib.sha256).hexdigest()
    r = requests.post(config.PUBLIC_BASE_URL.rstrip("/") + "/meo/detail-result", data=body, timeout=30,
                      headers={"Content-Type": "application/json", "X-Hito-Sig": sig})
    res = (r.json() or {}).get("result") if r.ok else f"http {r.status_code}"
    return {**m, "result": res}, res in ("sent", "quiet", "skip", "fail")


def push(uid: str, text: str) -> bool:
    if DRY:
        print(f"--- {uid[:8]}\n{text}"); return True
    r = requests.post("https://api.line.me/v2/bot/message/push", timeout=20,
                      headers={"Authorization": f"Bearer {config.MEO_LINE_CHANNEL_ACCESS_TOKEN}", "Content-Type": "application/json"},
                      json={"to": uid, "messages": [{"type": "text", "text": text[:4900]}]})
    return r.status_code == 200


def notify_ceo_once(text: str) -> None:
    """同じ日に同じ知らせは1回だけ（会長の LINE）。"""
    mark = os.path.join(HERE, "data", "ceo_notice_" + datetime.now().strftime("%Y%m%d") + ".txt")
    if os.path.exists(mark) and text[:30] in open(mark, encoding="utf-8").read():
        return
    open(mark, "a", encoding="utf-8").write(text[:30] + "\n")
    if DRY:
        print("[ceo]", text); return
    try:
        from src import line_notifier
        line_notifier.send(text)
    except Exception as e:
        print(f"[en_rank_watch] 会長通知失敗: {e}")


def main():
    os.makedirs(os.path.dirname(DONE), exist_ok=True)
    lk = open(LOCK, "w")
    try:
        fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("[en_rank_watch] 前の回がまだ動いている"); return
    done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
    tries = json.load(open(TRIES)) if os.path.exists(TRIES) else {}
    todo = [(u, q) for u, q in pending() if f"{u}|{q.get('id')}" not in done and tries.get(f"{u}|{q.get('id')}", 0) < MAX_TRIES]
    print(f"[en_rank_watch] {datetime.now():%m-%d %H:%M} 依頼 {len(todo)} 件", flush=True)
    if todo and not DRY and not config.MEO_LINE_CHANNEL_ACCESS_TOKEN:   # 送れないのに Chrome で調べ直さない
        notify_ceo_once("【MEO 要対応】英語の順位・無料点検の依頼を店に返せません（Mac の .env に MEO_LINE_CHANNEL_ACCESS_TOKEN が無い）。"
                        f"依頼 {len(todo)} 件は待たせています")
        return
    limited_seen = os.path.exists(LOGIN_NEEDED)   # ログイン切れの間は、どの店でも Chrome を開かない
    for uid, q in todo:
        if q.get("kind") == "detail":
            if limited_seen:
                continue
            r, ok = detail_one(uid, q)
            limited_seen = bool(r.get("limited") and r.get("result") == "limited")
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps({"uid": uid[:10], "req": q, "res": r, "sent": ok}, ensure_ascii=False) + "\n")
            if limited_seen:
                open(LOGIN_NEEDED, "w").write(datetime.now().isoformat())
                notify_ceo_once("【MEO 要対応】Googleマップの実物を読む Chrome のログインが切れています。"
                                "店の口コミの日付と返事を数えられないため、点検の続きを店に送れていません。"
                                "Mac で python3 ~/meo-research/line_login.py を実行し、hitotsunagi861 でログインしてください")
            if ok and not DRY:
                done.add(f"{uid}|{q.get('id')}"); json.dump(sorted(done), open(DONE, "w"))
            continue
        if q.get("kind") == "screens":
            import screens
            try:
                r = screens.check(q["text"], q.get("industry", ""), who=uid[:10])
            except Exception as e:
                r = {"ok": False, "why": str(e)[:100]}
            if r.get("ok") and not (r.get("ai") or {}).get("ok"):
                notify_ceo_once(f"【MEO 要確認】無料点検の ChatGPT に聞けませんでした（{(r.get('ai') or {}).get('why')}）。聞かない版で返しています。OpenAI の残高を確認してください")
            ok = push(uid, screens.message(r, f"「{q.get('shop') or r.get('name_ja') or 'お店'}」"))
        else:
            try:
                r = en_rank.report(q["text"], q.get("industry") or "その他", q.get("town", ""))
            except Exception as e:
                r = {"ok": False, "why": str(e)[:100]}
            label = q["text"].split()[0] if r.get("ok") else "お店"
            ok = push(uid, en_rank.message(r, f"「{label}」"))
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"uid": uid[:10], "req": q, "res": r, "sent": ok}, ensure_ascii=False) + "\n")
        if ok and not DRY:
            done.add(f"{uid}|{q.get('id')}"); json.dump(sorted(done), open(DONE, "w"))
        elif not DRY:   # 送れなかった: 回数を数え、MAX_TRIES で止めて会長へ（同じ依頼で Chrome を回し続けない）
            k = f"{uid}|{q.get('id')}"
            tries[k] = tries.get(k, 0) + 1; json.dump(tries, open(TRIES, "w"))
            if tries[k] >= MAX_TRIES:
                notify_ceo_once(f"【MEO 要対応】「{q.get('shop') or q.get('text', '')[:20]}」の依頼を{MAX_TRIES}回返せず止めました（LINE の送信に失敗）。鍵か宛先を確認してください")
        time.sleep(3)


def weekly_neta() -> None:
    """月曜に1回: 無料点検で ChatGPT に聞いた先週の結果をネタ帳と Notion へ（free_check_neta.py・会長 2026-10-17）。"""
    wk = datetime.now().strftime("%G-W%V")
    mark = os.path.join(HERE, "data", "free_check_neta_week.txt")
    if datetime.now().weekday() != 0 or (os.path.exists(mark) and open(mark).read().strip() == wk):
        return
    try:
        import free_check_neta
        free_check_neta.write(import_=not DRY)
        if not DRY:
            open(mark, "w").write(wk)
    except Exception as e:
        print(f"[en_rank_watch] 無料点検のネタの書き出しに失敗: {e}")


if __name__ == "__main__":
    main()
    weekly_neta()
