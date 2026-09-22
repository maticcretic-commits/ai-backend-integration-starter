"""API test suite for the backend integration starter (no network needed)."""
import hashlib
import hmac
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Point the app at a throwaway DB before importing it.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["LEADS_DB"] = _tmp.name
os.environ["WEBHOOK_SECRET"] = "test-secret"

import app as app_module
from app import app, verify_signature, summarize_with_ai


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health():
    assert client().get("/health").get_json() == {"ok": True}


def test_create_and_list_lead():
    c = client()
    resp = c.post("/api/leads", json={"name": "Asha", "email": "a@b.com",
                                      "service": "audit", "score": 80})
    assert resp.status_code == 201
    lead = resp.get_json()
    assert lead["name"] == "Asha" and lead["score"] == 80
    leads = c.get("/api/leads").get_json()
    assert any(l["email"] == "a@b.com" for l in leads)


def test_create_lead_validates_fields():
    resp = client().post("/api/leads", json={"name": "NoEmail"})
    assert resp.status_code == 400


def test_webhook_rejects_bad_signature():
    resp = client().post("/webhooks/incoming", json={"type": "ping"},
                         headers={"x-webhook-secret": "wrong"})
    assert resp.status_code == 401


def test_webhook_accepts_good_signature():
    body = json.dumps({"type": "ping"}).encode()
    sig = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
    resp = client().post("/webhooks/incoming", data=body,
                         content_type="application/json",
                         headers={"x-webhook-secret": sig})
    assert resp.status_code == 200
    assert resp.get_json()["received"] is True


def test_verify_signature_helper():
    assert verify_signature(b"hi", hmac.new(b"test-secret", b"hi",
                                            hashlib.sha256).hexdigest())
    assert not verify_signature(b"hi", "nope")


def test_summarize_fallback_without_key():
    os.environ.pop("OPENAI_API_KEY", None)
    out = summarize_with_ai("First sentence. Second sentence. Third one.")
    assert out["engine"] == "fallback"
    assert "First sentence" in out["summary"]
    assert "Third one" not in out["summary"]


def test_summarize_validates_input():
    assert client().post("/api/ai/summarize", json={}).status_code == 400


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
    print("All tests passed.")
