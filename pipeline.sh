
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

JSON_FILE="mitm_get_results.jsonl"
MITM_PID=""

cleanup() {
    if [[ -n "$MITM_PID" ]]; then
        kill "$MITM_PID" 2>/dev/null || true
        wait "$MITM_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

echo "[1/3] Starting Minit network..."

mitmweb \
    --listen-host 0.0.0.0 \
    --listen-port 8080 \
    --web-host 127.0.0.1 \
    --web-port 8081 \
    -s "$PWD/token_grabber.py" &

MITM_PID=$!

echo "Waiting for proxy to initialize..."
sleep 2

if ! kill -0 "$MITM_PID" 2>/dev/null; then
    echo "Error: mitmweb exited unexpectedly."
    exit 1
fi

echo "[2/3] Waiting for JSON output..."
echo "Generate traffic through the proxy to populate $JSON_FILE."
echo "Press Ctrl+C when collection is complete."

# Wait for the user to finish collecting traffic.
while kill -0 "$MITM_PID" 2>/dev/null; do
    sleep 1
    if [[ -s "$JSON_FILE" ]]; then
        break
    fi
done

if [[ ! -s "$JSON_FILE" ]]; then
    echo "Error: JSON output was not generated or is empty."
    exit 1
fi

echo "[3/3] Running sender.py..."
python3 sender.py
rm -f "$JSON_FILE"
echo "Pipeline completed successfully."
