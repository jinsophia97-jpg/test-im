"""Lightweight HTTP runtime for the AgentKit SSO frontend demo."""

import time

import uvicorn
from fastapi import FastAPI, Request

from assistant import handle_message


app = FastAPI()


@app.get("/ping")
def ping() -> dict:
    return {"status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "timestamp": time.time(), "service": "agent-service"}


@app.get("/readiness")
def readiness() -> dict:
    return {"status": "success", "timestamp": time.time(), "service": "agent-service"}


@app.get("/liveness")
def liveness() -> dict:
    return {"status": "success", "timestamp": time.time(), "service": "agent-service"}


@app.post("/invoke")
async def invoke(request: Request) -> dict:
    payload = await request.json()
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
