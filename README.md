## CMPE273-LAB 1- ANH HOANG(013765908)


1. What makes this distributed?

    This homework is an example of a distributed system because two services A and B run independently even though they run on the same machine, and they communicate with each other through HTTP. Service B calls service A through an API endpoint, and each service runs on its own port. Service A and B don’t share memories, they interact through the network. Therefore, each service is expected to start, run, crash or delay without directly crashing the other service. In this case, service B gracefully handles the failure of network, timeout or other connection failures. These characteristics including independent processes, network-based communication and separate failure domains are the main keys of a distributed system. 
2. What happens on timeout?

    When a timeout occurs, Service B stops waiting for a response from Service A after a fixed amount of time. If Service A takes too long to respond, Service B logs a timeout error and returns an HTTP 503 Sercive A timeout response to the client. Service A may still finish processing the request, but Service B doesn't wait for it and won't crash. This will help Service B stay responsive when Service A is slow.
3. What happens if Service A is down?

    When Service A is down, Service B can't reach it. Service B receive a connection error, log the failure, and return an HTTP 503 Service A unavailable to the client. Service A won't produce any logs because it isn't running and doesn't receive any request. Service B continues to run normally and handles the failure without crashing.

4. What do your logs show, and how would you debug?

    What the logs show:
    - Timestamp for each log
    - Log level (INFO or ERROR)
    - Which service handled the request(Service A or B)
    - Which endpoint was called
    - Whether the request is successful or failed
    - The latency of the request
    - The type of failure (timeout, connection error, HTTP error)

    How would I debug:
    - First of all, I will check the Service B logs to identify the failure
        + timeout: Service A responds slowly
        + ConnectionError: Service A is down or running on wrong port
        + HTTPError: 500: Service A responded but failed internally
    - Second, I will verify if Service A is running:
        + Health check on service A: curl http://127.0.0.1:8080/health
        + Check if Service A running on correct port
        + Check the latency in Service A log and compare with Service B log
        + If it an HTTP error, inspect Service A logs to locate the cause of failure


## 1. Running Two Services on Separate Ports

This project consists of two independent services running as separate processes on different ports.

- **Service A** runs on `localhost:8080`
- **Service B** runs on `localhost:8081`

Each service is started in its own terminal window.

## Service Endpoints

| Service | Port | Endpoint | Method | Description |
|--------|------|----------|--------|-------------|
| Service A | 8080 | `/health` | GET | Returns the health status of Service A |
| Service A | 8080 | `/echo` | GET | Returns the message provided in the `msg` query parameter |
| Service A | 8080 | `/foo` | GET | Returns HTTP 500 to simulate an internal server error |
| Service B | 8081 | `/health` | GET | Returns the health status of Service B |
| Service B | 8081 | `/call-echo` | GET | Calls Service A `/echo` and returns a combined response |
| Service B | 8081 | `/call-foo` | GET | Calls Service A `/foo` to test upstream HTTP error handling |


### Running Service A and health check

```bash
cd service-a
python3 -m venv .venv
source .venv/bin/activate
pip install flask requests
python app_a.py
```
Expected Output

```bash
(.venv) anhhoang@Anhs-MacBook-Pro service-a % python app_a.py                                                              
 * Serving Flask app 'app_a'
 * Debug mode: off
2026-02-04 22:59:09,813 INFO WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8080
2026-02-04 22:59:09,813 INFO Press CTRL+C to quit
```
Curl Command to Verify Service A running 
```bash
curl http://127.0.0.1:8080/health
```
Curl Output
```bash
(.venv) anhhoang@Anhs-MacBook-Pro CMPE273-LAB1 % curl http://127.0.0.1:8080/health
{"status":"ok"}
```
### Running Service B and health check
```bash
cd service-b
python3 -m venv .venv
source .venv/bin/activate
pip install flask requests
python app_b.py
```
Expected Output

```bash
(.venv) anhhoang@Anhs-MacBook-Pro service-b % python app_b.py                                                              
 * Serving Flask app 'app_b'
 * Debug mode: off
2026-02-04 23:01:54,083 INFO WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8081
2026-02-04 23:01:54,083 INFO Press CTRL+C to quit
```
Curl command to Verify Service B running 
```bash
curl http://127.0.0.1:8081/health
```
Curl Output
```bash
(.venv) anhhoang@Anhs-MacBook-Pro CMPE273-LAB1 % curl http://127.0.0.1:8081/health
{"status":"ok"}
```

## 2. Service B calls Service A

### Preconditions
- Service A is running on `localhost:8080`
- Service B is running on `localhost:8081`

### Steps
Open a terminal and run the following command:

```bash
curl "http://127.0.0.1:8081/call-echo?msg=hello"
```
Curl Output
```bash
(.venv) anhhoang@Anhs-MacBook-Pro CMPE273-LAB1 % curl "http://127.0.0.1:8081/call-echo?msg=hello"
{"service_a":{"echo":"hello"},"service_b":"ok"}
```

Service B Log 
```bash
2026-02-04 23:10:51,358 INFO service = B endpoint = /call-echo status=ok latency_ms=3
2026-02-04 23:10:51,358 INFO 127.0.0.1 - - [04/Feb/2026 23:10:51] "GET /call-echo?msg=hello HTTP/1.1" 200 -
```

Service A Log
```bash
2026-02-04 23:10:51,357 INFO service=A endpoint=/echo status=ok latency_ms=0
2026-02-04 23:10:51,357 INFO service=A endpoint=/echo status=ok latency_ms=0
2026-02-04 23:10:51,357 INFO 127.0.0.1 - - [04/Feb/2026 23:10:51] "GET /echo?msg=hello HTTP/1.1" 200 -
```


## 3. Testing Error Handling Scenarios

This section describes how to test failure scenarios for **Service B** when calling **Service A**.

- Service A runs on `localhost:8080`
- Service B runs on `localhost:8081`

---

### Test 1: Connection Refused (Service A is down)

**Goal:** Verify Service B handles the case where Service A is not running.

### Steps
    1. Stop Service A (Ctrl+C).
    2. Ensure Service B is running.
    3. Call Service B with this command:

```bash
curl "http://127.0.0.1:8081/call-echo?msg=test"
```

Curl Output

```bash
anhhoang@Anhs-MacBook-Pro CMPE273-LAB1 % curl  "http://127.0.0.1:8081/call-echo?msg=test" 
{"error":"Service A unavailable"}
```
Service B Log Error

```bash
2026-02-04 22:15:58,286 ERROR service=B endpoint=/call-echo status=unavailable latency_ms=2 error=ConnectionError
2026-02-04 22:15:58,287 INFO 127.0.0.1 - - [04/Feb/2026 22:15:58] "GET /call-echo?msg=test HTTP/1.1" 503 -
```


### Test 2: Provider Unreachable (Wrong Host or Port)

**Goal:** Verify that Service B handles the case where Service A is configured with an incorrect address.

---

### Preconditions
- Service B is running on `localhost:8081`
- Service A is running, but **Service B is configured to call the wrong port or host**

---

### Setup

Modify Service B configuration to use an invalid Service A address.

Example (wrong port):

```python
SERVICE_A_BASE = "http://127.0.0.1:9999"
```
### Steps
    1. Ensure two services running on two terminal
    2. Open a terminal and call this command 

```bash
curl "http://127.0.0.1:8081/call-echo?msg=test"
```
Expected Output

```bash
anhhoang@Anhs-MacBook-Pro CMPE273-LAB1 % curl  "http://127.0.0.1:8081/call-echo?msg=test" 
{"error":"Service A unavailable"}
```
Service B Log Error

```bash
2026-02-04 22:27:22,966 ERROR service=B endpoint=/call-echo status=unavailable latency_ms=5 error=ConnectionError
2026-02-04 22:27:22,966 INFO 127.0.0.1 - - [04/Feb/2026 22:27:22] "GET /call-echo?msg=test HTTP/1.1" 503 -
```

## Test 3: Request Timeout (Service A Responds Slowly)

**Goal:** Verify that Service B correctly handles a timeout when Service A responds too slowly.

---

### Preconditions
- Service A is running on `localhost:8080`
- Service B is running on `localhost:8081`
- Service B is configured with a timeout (e.g., 1 second)

---

### Setup

Modify Service A to delay its response in the `/echo` endpoint.

Example:

```python
# Uncommented during timeout testing
time.sleep(2.0)
```
### Steps
1. Make sure to run Service A again. 
2. Ensure Service B timeout is configured `/call-echo` endpoint:

```python
        r = requests.get(
            f"{SERVICE_A_BASE}/echo",
            params={"msg": msg},
            timeout=TIMEOUT_SECONDS,
        )

```

Curl Output
```bash
anhhoang@Anhs-MacBook-Pro CMPE273-LAB1 % curl  "http://127.0.0.1:8081/call-echo?msg=test"
{"error":"Service A timeout"}
```

Service B Log Error
```bash
2026-02-04 22:40:56,004 ERROR service=B endpoint=/call-echo status=timeout latency_ms=1003 error=ReadTimeout
2026-02-04 22:40:56,004 INFO 127.0.0.1 - - [04/Feb/2026 22:40:56] "GET /call-echo?msg=test HTTP/1.1" 503 -
```

Service A Log Info
```bash
2026-02-04 22:40:57,006 INFO service=A endpoint=/echo status=ok latency_ms=2002
2026-02-04 22:40:57,006 INFO service=A endpoint=/echo status=ok latency_ms=2003
2026-02-04 22:40:57,007 INFO 127.0.0.1 - - [04/Feb/2026 22:40:57] "GET /echo?msg=test HTTP/1.1" 200 -
```

## Test 4: Upstream HTTP Error (Service A returns 500)

**Goal:** Verify that Service B handles non-2xx responses from Service A.

### Setup

Service A was modified to expose an endpoint that always returns HTTP 500.

```python
# Service A
from flask import abort

@app.get("/foo")
def foo():
    start = time.time()
    logging.error(
        f"service=A endpoint=/foo status=error latency_ms={int((time.time()-start)*1000)}"
    )
    abort(500)

```
Service B calls this endpoint using a dedicated route

```python
@app.get("/call-foo")
def call_boom():
    start = time.time()
    url = f"{SERVICE_A_BASE}/foo"
```
### Steps
    1. Keep 2 services running on two terminals
    2. Open a terminal and call this command:
```bash
curl "http://127.0.0.1:8081/call-foo"
```

Curl Output

```bash
anhhoang@Anhs-MacBook-Pro CMPE273-LAB1 % curl  "http://127.0.0.1:8081/call-foo"
{"error":"Service A returned error"}
```
Service B Log Error
```bash
2026-02-04 22:52:44,997 ERROR service=B endpoint=/call-foo status=error latency_ms=2 error=HTTPError:500
2026-02-04 22:52:44,998 INFO 127.0.0.1 - - [04/Feb/2026 22:52:44] "GET /call-foo HTTP/1.1" 503 -
```

Service A Log Error
```bash
2026-02-04 22:52:44,996 ERROR service=A endpoint=/foo status=error latency_ms=0
2026-02-04 22:52:44,997 INFO 127.0.0.1 - - [04/Feb/2026 22:52:44] "GET /foo HTTP/1.1" 500 -
```