#!/bin/zsh
# 業種を広げた標本調査（13業種×10都市）: 母集団 → 抜けた検索をもう一度 → 上位20位の詳細 2並列 → 集計
# ログインなしだと「表示が制限されています」になるため、調査用アカウントでログイン済みの .gprofile のコピー（_w0, _w1）を使う
# 出力は ind_* だけ（既存5業種の frame.jsonl / detail_*.jsonl には書かない）。調査中はMacを眠らせない
cd ~/meo-research
export GMAPS_PROFILE=$HOME/meo-research/.gprofile_wsample_w0 GMAPS_PROFILE_BASE=$HOME/meo-research/.gprofile_wsample
export FRAME_OUT=ind_frame.jsonl FRAME_DONE=ind_frame_done.json
export DETAIL_OUT=ind_detail.jsonl DETAIL_REDO=1 DETAIL_MAX_RANK=20
caffeinate -i python3 -u frame.py --sample >> data/ind_sample.log 2>&1
caffeinate -i python3 -u frame.py --sample >> data/ind_sample.log 2>&1
unset GMAPS_PROFILE   # 詳細は並列ごとに _w0/_w1
caffeinate -i python3 -u detail.py --workers 2 >> data/ind_sample.log 2>&1
python3 analyze.py --sample > data/result_industries_sample.md 2>> data/ind_sample.log
echo "[chain] 完了 $(date '+%F %T')" >> data/ind_sample.log
