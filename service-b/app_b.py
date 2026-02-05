from flask import Flask, request, jsonify
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)

SERVICE_A_BASE = "http://127.0.0.1:8080"
TIMEOUT_SECONDS = 1.0

#Information logs display service, endpoint, status, latency
def log_info(endpoint: str, status: str, start_time: float):
    latency_ms = int((time.time() - start_time) * 1000)
    logging.info(f"service = B endpoint = {endpoint} status={status} latency_ms={latency_ms}")

def log_error(endpoint: str, status: str, start_time: float, err: str):
    latency_ms = int((time.time() - start_time) * 1000)
    logging.error(
        f"service=B endpoint={endpoint} status={status} latency_ms={latency_ms} error={err}"
    )

@app.get("/health")
def health():
    start = time.time()
    log_info("/health", "ok", start)
    return jsonify(status="ok")

@app.get("/call-echo")
def call_echo():
    start = time.time()
    msg = request.args.get("msg", "")

    try:
        r = requests.get(
            f"{SERVICE_A_BASE}/echo",
            params={"msg": msg},
            timeout=TIMEOUT_SECONDS,
        )
        r.raise_for_status()

        data = r.json()
        log_info("/call-echo", "ok", start)

        return jsonify(
            service_b="ok",
            service_a=data,
        )
    
    except requests.Timeout as e:
        log_error("/call-echo", "timeout", start, type(e).__name__)
        return jsonify(error="Service A timeout"), 503

    # requirement: stop Service A -> Service B returns 503 and logs an error
    except requests.ConnectionError as e:
        log_error("/call-echo", "unavailable", start, type(e).__name__)
        return jsonify(error="Service A unavailable"), 503

    except requests.HTTPError as e:
        log_error("/call-echo", "error", start, f"HTTPError:{e.response.status_code}")
        return jsonify(error="Service A returned error"), 503

@app.get("/call-foo")
def call_boom():
    start = time.time()
    url = f"{SERVICE_A_BASE}/foo"

    try:
        r = requests.get(url, timeout=1.0)
        r.raise_for_status()   # <-- REQUIRED to trigger HTTPError
        return jsonify(service_b="ok"), 200

    except requests.HTTPError as e:
        log_error(
            "/call-foo",
            "error",
            start,
            f"HTTPError:{e.response.status_code}"
        )
        return jsonify(error="Service A returned error"), 503




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=False, use_reloader=False)