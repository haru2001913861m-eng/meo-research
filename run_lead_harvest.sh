#!/bin/zsh
# 営業リストを作り続ける（launchd: com.hitotsunagi.lead-harvest・KeepAlive）
cd "$HOME/meo-research" || exit 1
export GMAPS_PROFILE="$HOME/meo-research/.gprofile_harvest"
exec caffeinate -i /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -u lead_harvest.py >> logs/lead_harvest.log 2>&1
