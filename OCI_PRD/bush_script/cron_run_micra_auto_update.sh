#!/bin/bash

# ログ出力先（任意で変更可能）
LOG_FILE="/tmp/micra_cron.log"

# 仮想環境とスクリプトのパス
VENV_PATH="/home/opc/myenv"
SCRIPT_PATH="/home/opc/micra_auto_update.py"

# cron環境用の最低限の環境変数
export PATH="/usr/local/bin:/usr/bin:/bin"
export HOME="/home/opc"

# ログディレクトリがなければ作成
mkdir -p "$(dirname "$LOG_FILE")"

# 仮想環境の python を直接使ってスクリプト実行
"${VENV_PATH}/bin/python" "${SCRIPT_PATH}" >> "${LOG_FILE}" 2>&1
