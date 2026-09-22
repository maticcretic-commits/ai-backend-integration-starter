#!/usr/bin/env python3
"""
AI Backend Integration Starter — portfolio practice project.

Template for the "$3,000 budget" Python AI-integration gig pattern:
REST API + webhooks + AI endpoint + tests, production-shaped.

Endpoints (Flask):
  * GET/POST /api/leads        — lead CRUD over SQLite
  * POST /webhooks/incoming    — generic webhook receiver with a
                                 shared-secret check (x-webhook-secret)
  * POST /api/ai/summarize     — OpenAI summarization with a graceful
                                 fallback when no API key is set
  * GET /health                — liveness probe

Also includes examples/node_bridge.py: the pattern for calling an
existing Node.js/PHP service from Python (HTTP bridge), so legacy
components can be modernized gradually without rewrites.

Usage:
    pip install -r requirements.txt
    python app.py                    # http://localhost:5000
    python tests/test_app.py         # full API test suite
"""

import hashlib
import hmac
import json
import os
import sqlite3
import sys
from pathlib import Path

from flask import Flask, g, jsonify, request

BASE = Path(__file__).resolve().parent
DB_PATH = os.environ.get("LEADS_DB", str(BASE / "leads.db"))
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "dev-secret-change-me")

# TODO(learn): add Alembic-style migrations once the schema grows past
# one table; write a test that migrates an old DB file forward.

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    service TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
"""


def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.executescript(SCHEMA)
    return db


def summarize_with_ai(text):
    """Summarize via OpenAI; fall back to extractive summary without a key."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system",
                       "content": "Summarize in two sentences or fewer."},
                      {"role": "user", "content": text}],
        )
        return {"summary": resp.choices[0].message.content, "engine": "openai"}
    sentences = [s.strip() for s in text.replace("!", ".").split(".") if s.strip()]
    return {"summary": ". ".join(sentences[:2]) + ("." if sentences else ""),
            "engine": "fallback"}


def verify_signature(body, signature):
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")


app = Flask(__name__)


@app.teardown_appcontext
def close_db(_exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/leads")
def list_leads():
    rows = get_db().execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/leads")
def create_lead():
    data = request.get_json(force=True)
    for field in ("name", "email", "service"):
        if not data.get(field):
            return {"error": f"missing field: {field}"}, 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO leads (name, email, service, score) VALUES (?, ?, ?, ?)",
        (data["name"], data["email"], data["service"], int(data.get("score", 0))),
    )
    db.commit()
    lead = db.execute("SELECT * FROM leads WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(lead)), 201


@app.post("/webhooks/incoming")
def webhook_incoming():
    body = request.get_data()
    if not verify_signature(body, request.headers.get("x-webhook-secret")):
        return {"error": "bad signature"}, 401
    event = request.get_json(force=True, silent=True) or {}
    # TODO(learn): route event["type"] to handlers; log to a table.
    return {"received": True, "event_type": event.get("type", "unknown")}


@app.post("/api/ai/summarize")
def ai_summarize():
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("text"):
        return {"error": "missing field: text"}, 400
    return jsonify(summarize_with_ai(data["text"]))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
