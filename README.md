project/
├── auth-service/                    # Port 8000
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── session.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── tenant.py         # SHARED SCHEMA ⭐
│   │   │   ├── user.py
│   │   │   └── api_key.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── auth.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── auth.py           # JWT generation, verification
│   │   │
│   │   └── api/
│   │       ├── __init__.py
│   │       └── v1/
│   │           ├── __init__.py
│   │           └── auth.py       # /register, /login, /verify
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env
│   └── README.md
│
└── ai-service/                      # Port 8002
    ├── app/
    │   ├── __init__.py
    │   ├── main.py                 # NO AUTH ROUTER ⚠️
    │   ├── config.py               # + AUTH_SERVICE_URL ⚠️
    │   │
    │   ├── agent/                  # ✅ YOUR CORE AI LOGIC
    │   │   ├── agent.py
    │   │   ├── graph.py
    │   │   ├── nodes/
    │   │   ├── prompts/
    │   │   ├── state/
    │   │   └── tools/
    │   │
    │   ├── api/
    │   │   └── v1/
    │   │       └── chat.py         # UPDATED: No message insert ⚠️
    │   │
    │   ├── models/
    │   │   ├── tenant.py           # SHARED SCHEMA ⭐
    │   │   ├── message.py          # Reference only
    │   │   ├── credit.py           # ✅ YOU OWN
    │   │   ├── tool_log.py         # ✅ YOU OWN
    │   │   └── ...
    │   │
    │   ├── schemas/
    │   │   └── chat.py             # + AIInboundRequest, AIResponse ⚠️
    │   │
    │   ├── services/
    │   │   ├── auth.py             # MINIMIZED: only verify_token ⚠️
    │   │   ├── llm_client.py       # ✅ YOU OWN
    │   │   ├── vector_store.py     # ✅ YOU OWN
    │   │   ├── cache.py            # ✅ YOU OWN
    │   │   ├── tool_executor.py    # ✅ YOU OWN
    │   │   └── billing.py          # ✅ YOU OWN
    │   │
    │   └── db/
    │       └── session.py
    │
    ├── requirements.txt
    ├── Dockerfile
    ├── .env                        # + AUTH_SERVICE_URL ⚠️
    └── README.md

    