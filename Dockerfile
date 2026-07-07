# Cloud builds run inside Volcengine: they can't pull from Docker Hub, and a
# `# syntax=` directive would make BuildKit fetch the docker/dockerfile frontend
# from Docker Hub (401). So: no syntax directive, and base from a
# Volcengine-hosted image (which also ships `uv`).
FROM agentkit-prod-public-cn-beijing.cr.volces.com/base/py-simple:python3.12-bookworm-slim-latest

ENV UV_SYSTEM_PYTHON=1 PYTHONUNBUFFERED=1
WORKDIR /app

# The AgentKit base image already contains FastAPI and Uvicorn. Avoid network
# package installation here because CodePipeline package-source access is slow.
RUN python --version \
    && uv --version \
    && python -c "import fastapi, uvicorn; print('fastapi', fastapi.__version__, 'uvicorn', uvicorn.__version__)"

COPY . .

# The runtime probes :8000 for readiness; the server must listen here.
EXPOSE 8000
CMD ["python", "main.py"]
