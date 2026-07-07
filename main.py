"""Lightweight AgentKit runtime for the SSO frontend demo.

This project is intentionally using AgentkitSimpleApp instead of the full veADK
agent server so the first SSO frontend deployment has a much smaller dependency
tree and can clear the cloud image build step reliably.
"""

from agentkit.apps import AgentkitSimpleApp

from assistant import handle_message


app = AgentkitSimpleApp()


@app.ping
def ping() -> str:
    return "ok"


@app.entrypoint
async def invoke(payload: dict) -> dict:
    message = _extract_message(payload)
    return {
        "message": handle_message(message),
        "input": message,
        "runtime": "agentkit-simple-app",
    }


def _extract_message(payload: dict) -> str:
    if not isinstance(payload, dict):
        return str(payload or "")

    message = payload.get("message")
    if isinstance(message, str):
        return message

    messages = payload.get("messages")
    if isinstance(messages, list) and messages:
        last = messages[-1]
        if isinstance(last, str):
            return last
        if isinstance(last, dict):
            for key in ("content", "text", "message"):
                value = last.get(key)
                if isinstance(value, str):
                    return value

    return str(payload) if payload else ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
