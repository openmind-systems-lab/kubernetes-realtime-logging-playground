import json, os, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

APP = os.getenv("APP_NAME", "sample")
PORT = int(os.getenv("PORT", "8080"))
PAYMENTS_URL = os.getenv("PAYMENTS_URL", "http://payments-api:8080/charge")

def emit(event, **fields):
    print(json.dumps({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": fields.pop("level", "INFO"), "service": APP,
        "pod": os.getenv("HOSTNAME", "local"), "event": event, **fields},
        separators=(",", ":")), flush=True)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass
    def respond(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == "/health": return self.respond(200, {"status":"ok","service":APP})
        return self.respond(200, {"service":APP,"pod":os.getenv("HOSTNAME","local")})
    def do_POST(self):
        length = int(self.headers.get("Content-Length","0"))
        try: data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError: return self.respond(400, {"error":"invalid_json"})
        cid = self.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        if APP == "orders-api" and self.path == "/orders":
            emit("order_received", correlation_id=cid, item=data.get("item","demo"), quantity=data.get("quantity",1))
            req = Request(PAYMENTS_URL, data=json.dumps({"order_id":str(uuid.uuid4()),"amount":19.99}).encode(),
                headers={"Content-Type":"application/json","X-Correlation-ID":cid}, method="POST")
            try:
                with urlopen(req, timeout=4) as response: payment = json.loads(response.read())
                emit("payment_completed", correlation_id=cid, payment_status=payment.get("status"))
                return self.respond(200, {"status":"accepted","correlation_id":cid,"payment":payment})
            except (URLError, HTTPError, TimeoutError) as exc:
                emit("payment_failed", level="ERROR", correlation_id=cid, error=str(exc))
                return self.respond(502, {"status":"payment_unavailable","correlation_id":cid})
        if APP == "payments-api" and self.path == "/charge":
            emit("payment_authorized", correlation_id=cid, order_id=data.get("order_id"), amount=data.get("amount"))
            return self.respond(200, {"status":"authorized","payment_id":str(uuid.uuid4())})
        return self.respond(404, {"error":"not_found"})

def worker():
    i=0
    while True:
        i+=1; emit("background_job_completed", job_id=f"job-{i}", records_processed=i%7+1); time.sleep(5)

if APP == "background-worker": threading.Thread(target=worker, daemon=True).start()
emit("application_started", port=PORT)
ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
