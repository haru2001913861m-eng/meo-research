# -*- coding: utf-8 -*-
"""Business Profile API の承認を毎日確かめ、下りた日に本番（Render）の GBP_ENABLED=true を入れる（会長 2026-10-17「全部やって自動で動かしていい」）.

2026-10-28: 1回目の申請（ケース 4-5844000041982）は却下（申請のウェブサイトの URL がプロフィールの URL と一致しない）。再申請の後も同じ見張りで待つ。
  鍵の作り直し（Railway 事件）で古い鍵が invalid_client になり、毎回エラーで止まっていた → 鍵が古い時は会長に「鍵を取る1行」を週1回。
  書き込み先は Railway（削除済み）→ Render の API（~/.config/hitotsunagi/render_api_key）に変えた。

申請: 2026-10-17 ケース ID 4-5844000041982（プロジェクト hito-sales・番号 155094317546・審査 7〜10 営業日）。
鍵: ~/.config/hitotsunagi/gbp_token.json（scripts/gbp_auth.py --yes が作る。会長が1回だけ実行）。
動き:
  鍵が無い → 10/28 以降、週1回だけ会長の LINE に「鍵を取る1行」を出す
  鍵がある → accounts 一覧を呼ぶ。200 = 承認 → Render の GBP_TOKEN_JSON・GBP_ENABLED=true を入れてデプロイ → 会長 LINE に1回
             429／quota = 承認待ち（黙ってログだけ）。それ以外 = 会長 LINE に1日1回
終わったら data/gbp_approved.json を書き、以後は何もしない。
実行: python3 gbp_approve_watch.py [--dry]。毎日の呼び出し: run_client_watch.sh の先頭（launchd com.hitotsunagi.meo-client-watch・05:00／06:30／13:00）
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.expanduser("~/sales-automation")
sys.path.insert(0, SA); os.chdir(SA)

DRY = "--dry" in sys.argv
TOKEN_FILE = os.path.expanduser("~/.config/hitotsunagi/gbp_token.json")
DONE = os.path.join(HERE, "data", "gbp_approved.json")
RENDER_KEY = os.path.expanduser("~/.config/hitotsunagi/render_api_key")
RENDER_SVC = "srv-dbcq6bgm7kps73ciqm4g"
ACCT = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
SCOPE = ["https://www.googleapis.com/auth/business.manage"]
REMIND_FROM = date(2026, 10, 28)   # 審査 7 営業日の目安
CASE = "4-5844000041982"
KEY_CMD = "cd ~/sales-automation && git pull origin master && python3 scripts/gbp_auth.py --yes"


def notify_ceo_once(text: str, key: str) -> None:
    mark = os.path.join(HERE, "data", "ceo_notice_" + datetime.now().strftime("%Y%m%d") + ".txt")
    if os.path.exists(mark) and key in open(mark, encoding="utf-8").read():
        return
    open(mark, "a", encoding="utf-8").write(key + "\n")
    if DRY:
        print("[ceo]", text); return
    try:
        from src import line_notifier
        line_notifier.send(text)
    except Exception as e:
        print(f"[gbp_approve_watch] 会長通知失敗: {e}")


def set_render_env(values: dict) -> None:
    """本番（Render）の環境変数を足して、デプロイし直す。値は表に出さない"""
    import requests
    key = open(RENDER_KEY, encoding="utf-8").read().strip()
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    for k, v in values.items():
        r = requests.put(f"https://api.render.com/v1/services/{RENDER_SVC}/env-vars/{k}", headers=h, json={"value": v}, timeout=30)
        r.raise_for_status()
    requests.post(f"https://api.render.com/v1/services/{RENDER_SVC}/deploys", headers=h, json={}, timeout=30).raise_for_status()


def check(token_json: str) -> tuple[str, str]:
    """('ok'|'wait'|'error', 詳細)"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import requests
    cr = Credentials.from_authorized_user_info(json.loads(token_json), SCOPE)
    if not cr.valid:
        try:
            cr.refresh(Request())
        except Exception as e:   # invalid_client（鍵の作り直しで古くなった）など → 鍵の取り直し
            return "stale", str(e)[:160]
    r = requests.get(ACCT, headers={"Authorization": f"Bearer {cr.token}"}, timeout=20)
    if r.status_code == 200:
        return "ok", r.text[:2000]
    if r.status_code == 429 or "quota" in r.text.lower():
        return "wait", f"{r.status_code} {r.text[:120]}"
    if r.status_code == 403 and ("not been used" in r.text or "disabled" in r.text):   # プロジェクトで API が未有効（承認前の状態）
        return "wait", f"403 API 未有効: {r.text[:100]}"
    return "error", f"{r.status_code} {r.text[:200]}"


def v4_enabled(token_json: str, accounts_text: str) -> bool | None:
    """v4 が有効なら True、未有効（403 not been used/disabled）なら False、判断できなければ None（止めない）。"""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        import requests
        acct = ((json.loads(accounts_text) if accounts_text.startswith("{") else {}).get("accounts") or [{}])[0].get("name", "accounts/-")
        cr = Credentials.from_authorized_user_info(json.loads(token_json), SCOPE)
        if not cr.valid:
            cr.refresh(Request())
        r = requests.get(f"https://mybusiness.googleapis.com/v4/{acct}/locations/-/reviews",
                         headers={"Authorization": f"Bearer {cr.token}"}, timeout=20)
        if r.status_code == 403 and ("not been used" in r.text or "disabled" in r.text):
            return False
        return True
    except Exception as e:
        print(f"[gbp_approve_watch] v4 の確認ができず（止めない）: {e}")
        return None


def main() -> int:
    if os.path.exists(DONE):
        print("[gbp_approve_watch] 承認済み（何もしない）:", open(DONE, encoding="utf-8").read()[:80]); return 0
    if not os.path.exists(TOKEN_FILE):
        if date.today() >= REMIND_FROM and date.today().weekday() == 0:   # 月曜に週1回
            notify_ceo_once(f"【MEO】Google の API（ケース {CASE}）の鍵がまだです。Mac で1行:\n{KEY_CMD}\n（ブラウザで「許可」を押すだけ。承認前でも取れます）", "gbp_key")
        print("[gbp_approve_watch] 鍵なし"); return 0
    tok = open(TOKEN_FILE, encoding="utf-8").read()
    state, why = check(tok)
    print(f"[gbp_approve_watch] {state}: {why}")
    if state == "stale":
        if date.today().weekday() == 0 or "--now" in sys.argv:
            notify_ceo_once(f"【MEO】Google の API の鍵が古くなっています（引っ越しで作り直したため）。Mac で1行:\n{KEY_CMD}\n（ブラウザで「許可」を押すだけ）", "gbp_stale")
        return 0
    if state == "wait":
        return 0
    if state == "error":
        notify_ceo_once(f"【MEO 要確認】Google の API の確認でエラー: {why[:120]}", "gbp_err"); return 1
    # 承認が下りた。口コミ返信・投稿に使う v4（mybusiness.googleapis.com）は承認後にしかライブラリに出ないので、有効かを確かめてから切り替える
    v4 = v4_enabled(tok, why)
    if v4 is False:
        notify_ceo_once(f"【MEO 要対応】Google の API の承認が下りました（ケース {CASE}）。あと1つ、Cloud コンソールで「Google My Business API」を有効にしてください（1クリック）:\n"
                        "https://console.cloud.google.com/apis/library/mybusiness.googleapis.com?project=hito-sales\n有効にした翌朝に自動で切り替わります", "gbp_v4")
        return 0
    if not DRY:
        set_render_env({"GBP_TOKEN_JSON": tok, "GBP_ENABLED": "true"})
    json.dump({"at": datetime.now().isoformat(timespec="seconds"), "accounts": why}, open(DONE, "w", encoding="utf-8"), ensure_ascii=False)
    notify_ceo_once(f"【MEO】Google の Business Profile API の承認が下りました（ケース {CASE}）。本番に GBP_ENABLED=true を入れ、デプロイし直しました。"
                    "次のデプロイから、口コミ返信（★4〜5は自動・★1〜3は店の承認後）・お知らせ・説明文・招待の承認が自動になります。", "gbp_ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
