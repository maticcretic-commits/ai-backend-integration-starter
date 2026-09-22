"""
Example: calling an existing Node.js/PHP service from Python.

The gradual-modernization pattern: keep the legacy service running,
put Python in front, and migrate endpoint by endpoint.

Legacy side (Node/Express sketch — not executed here):
    app.post('/legacy/price', (req, res) => res.json({total: req.body.qty * 99}));

Python side (this file):
    total = legacy_price_calculator(qty=3)  # -> 297
"""

import json
import urllib.request

LEGACY_BASE_URL = "http://localhost:3000"  # your Node/PHP service


def legacy_price_calculator(qty):
    payload = json.dumps({"qty": qty}).encode()
    req = urllib.request.Request(
        f"{LEGACY_BASE_URL}/legacy/price", data=payload,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())["total"]


if __name__ == "__main__":
    print("Legacy service must be running on :3000 for this demo.")
