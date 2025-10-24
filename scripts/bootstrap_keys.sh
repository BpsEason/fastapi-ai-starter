#!/usr/bin/env bash
# 說明: 產生一組本機測試用 API key 並輸出

python - <<'PY'
import secrets
key = secrets.token_hex(32)
print("Generated API key:", key)
print("You can export it with:")
print(f"export APP_API_KEY={key}")
PY
