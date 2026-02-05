from flask import Flask, request, jsonify, abort
import time
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)

def log_request(endpoint: str, status: str, start_time: float):
    latency_ms = int((time.time() - start_time) * 1000)
    logging.info(
        f"service=A endpoint={endpoint} status={status} latency_ms={latency_ms}"
    )

@app.get("/health")
def health():
    start = time.time()
    log_request("/health", "ok", start)
    return jsonify(status="ok")

@app.get("/echo")
def echo():
    start = time.time()

    # Uncommented during timeout testing 
    #time.sleep(2.0)
    msg = request.args.get("msg", "")
    log_request("/echo", "ok", start)
    logging.info(
        f"service=A endpoint=/echo status=ok latency_ms={int((time.time()-start)*1000)}"
    )
    return jsonify(echo=msg)

@app.get("/foo")
def foo():
    start = time.time()
    logging.error(
        f"service=A endpoint=/foo status=error latency_ms={int((time.time()-start)*1000)}"
    )
    abort(500)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)
