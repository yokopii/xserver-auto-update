#VPS上で事前に作成しておく。1度作ればOK

# 1. スワップファイルを作成（256MB）
sudo fallocate -l 1024M /swapfile

# 2. パーミッションを設定（セキュリティ上必須）
sudo chmod 600 /swapfile

# 3. スワップ領域として初期化
sudo mkswap /swapfile

# 4. スワップを有効化
sudo swapon /swapfile
