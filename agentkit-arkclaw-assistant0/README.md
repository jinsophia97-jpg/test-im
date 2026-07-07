# agentkit-arkclaw-assistant0

An **internal employee & IT service-desk** agent ([VeADK](https://github.com/volcengine/veadk-python)),
scaffolded with `agentkit init`. It runs as the ADK API server and is delivered
through a **public SSO-login frontend**: `agentkit deploy` builds the runtime and
a frontend BFF where employees log in via your Volcengine user pool, then chat
with the agent — their identity is forwarded end-to-end (no shared API key).

The agent (`assistant/agent.py`) answers from an internal knowledge base and can
create/track support tickets and check leave balances. Every backend is an
in-memory mock — replace each tool's body with calls to your real IT/HR systems.

## Run it locally

```bash
pip install -r requirements.txt
cp .env.example .env        # set your Volcengine AK/SK
python main.py              # serves the ADK API on http://0.0.0.0:8000
```

Probe it: `curl localhost:8000/list-apps`.

## Deploy it (with the SSO frontend)

```bash
export USERPOOL_ID=... USERPOOL_CLIENT_ID=...
agentkit deploy
```

`frontend` is already enabled in `.agentkit/agentkit.yaml`, so `agentkit deploy`
also ships the public frontend and derives the runtime's `custom_jwt` auth from
the same user pool — no flags needed. See the docs for preparing the user pool
and a WEB client.

## Next steps

- Replace the mock tools in `assistant/agent.py` with your real ITSM/HR APIs.
- Tune the `instruction` for your company's tone and policies.
