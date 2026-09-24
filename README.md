# AI Backend Integration Starter

[![GitHub stars](https://img.shields.io/github/stars/maticcretic-commits/ai-backend-integration-starter?style=social)](https://github.com/maticcretic-commits/ai-backend-integration-starter/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/maticcretic-commits/ai-backend-integration-starter)](https://github.com/maticcretic-commits/ai-backend-integration-starter/commits/main)
[![Cost: Free](https://img.shields.io/badge/cost-%E2%82%B90-brightgreen)](https://github.com/maticcretic-commits/ai-backend-integration-starter)


A portfolio practice project: a **production-shaped Python backend template** —
the pattern behind "$3,000 budget" AI-integration gigs (REST API, webhooks,
AI endpoints, QA test suite, legacy interop).

> Template/study project — set real secrets and a managed database before
> any production use.

## What's inside

| Endpoint | Purpose |
|---|---|
| `GET /health` | liveness probe |
| `GET/POST /api/leads` | lead CRUD over SQLite |
| `POST /webhooks/incoming` | webhook receiver with HMAC shared-secret check |
| `POST /api/ai/summarize` | OpenAI summarization, graceful fallback without a key |
| `examples/node_bridge.py` | pattern for calling an existing Node.js/PHP service from Python |

## Run

```bash
pip install -r requirements.txt
cp .env.example .env        # optional: OPENAI_API_KEY, WEBHOOK_SECRET
python app.py               # http://localhost:5000
python tests/test_app.py    # full API suite, no network needed
```

Try it:

```bash
curl -X POST localhost:5000/api/leads \
  -H 'Content-Type: application/json' \
  -d '{"name":"Asha","email":"a@b.com","service":"audit","score":80}'

curl -X POST localhost:5000/api/ai/summarize \
  -H 'Content-Type: application/json' \
  -d '{"text":"RAG retrieves relevant chunks before answering. This grounds the model in your data. It reduces hallucinations a lot."}'
```

## What I'd build next (learning roadmap)

- [ ] Swap SQLite for Postgres/MySQL via SQLAlchemy
- [ ] JWT auth on the API
- [ ] Alembic-style migrations
- [ ] Event-type router + dead-letter table for webhooks

## ❤️ Support My Work

> If you find this project useful, please consider supporting my work with a Bitcoin donation:
>
> **₿ `BC1Q6Q75K8ZJXVW7W02LMDPRPY6XX6QK4LZZ2RMVAY`**

## ☕ Support my work
If this project was useful, you can support it with Bitcoin: `bc1q6q75k8zjxvw7w02lmdprpy6xx6qk4lzz2rmvay`
