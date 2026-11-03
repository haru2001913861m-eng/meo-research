# -*- coding: utf-8 -*-
"""いつもの Chrome を使うコマンドを、順番待ちの鍵（maps_chrome.LOCK）を持ったまま実行する（2026-10-31）.
claude -p --chrome は同時に1つしか Chrome の道具を受け取れないため、note-pv・夜の口コミ読み・無料点検で鍵を共有する。
使い方: python3 chrome_lock.py <コマンド> [引数...]   （15分待っても空かなければ終了コード 75）"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maps_chrome  # noqa: E402

# --not-google: Google のページを開かない用（note の閲覧数など）。hitotsunagi861 の止め札（google_hold）があっても通す（2026-11-03）。
# 11/1〜2 は note の閲覧数がこの止め札で読めず「PV 行 0」のまま、会長には「読めませんでした」だけが届いていた
args = sys.argv[1:]
google = True
if args and args[0] == "--not-google":
    google, args = False, args[1:]
if google and os.path.exists(os.path.expanduser("~/.config/hitotsunagi/google_hold")):
    print("[chrome_lock] hitotsunagi861 のログインが止められているので Chrome を開かない（google_hold）", file=sys.stderr)
    sys.exit(76)
lk = maps_chrome._chrome_lock(google=google)
if lk is None:
    print("[chrome_lock] 15分待っても Chrome が空かない", file=sys.stderr)
    sys.exit(75)
try:
    r = subprocess.run(args)
    sys.exit(r.returncode)
finally:
    lk.close()
