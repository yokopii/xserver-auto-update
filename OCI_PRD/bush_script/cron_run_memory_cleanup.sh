#!/bin/bash

#############################################################
# 再起動後に流すための軽量スクリプト（swap有効化のみ）
#############################################################

LOG="/var/log/memory_cleanup_after_boot.log"
SWAPFILE="/swapfile"

echo "[$(date)] ===== Boot-Time Memory Cleanup Start =====" >> "$LOG"
free -h >> "$LOG"

# キャッシュのクリア
sync
echo 3 > /proc/sys/vm/drop_caches

# スワップファイルの有効化（事前に作成済み前提）
if [ -f "$SWAPFILE" ]; then
  if swapon --show | grep -q "$SWAPFILE"; then
    echo "[$(date)] Swapfile already active. No action needed." >> "$LOG"
  else
    echo "[$(date)] Activating existing swapfile..." >> "$LOG"
    chmod 600 "$SWAPFILE"
    mkswap "$SWAPFILE"
    swapon "$SWAPFILE"
    echo "[$(date)] Swapfile activated." >> "$LOG"
  fi
else
  echo "[$(date)] Swapfile not found. Skipping swap activation." >> "$LOG"
fi

echo "[$(date)] After cleanup:" >> "$LOG"
free -h >> "$LOG"
echo "[$(date)] ===== Cleanup Complete =====" >> "$LOG"
echo "" >> "$LOG"