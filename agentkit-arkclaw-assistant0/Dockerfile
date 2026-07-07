# Cloud builds run inside Volcengine: they can't pull from Docker Hub, and a
# `# syntax=` directive would make BuildKit fetch the docker/dockerfile frontend
# from Docker Hub (401). So: no syntax directive, and base from a
# Volcengine-hosted image (which also ships `uv`).
FROM agentkit-prod-public-cn-beijing.cr.volces.com/base/py-simple:python3.12-bookworm-slim-latest

ARG PYPI_INDEX_URL=https://mirrors.ivolces.com/pypi/simple/
ARG PYPI_EXTRA_INDEX_URL=https://pypi.org/simple/

ENV UV_SYSTEM_PYTHON=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
COPY requirements.txt ./
RUN python --version \
    && uv --version \
    && uv pip install \
        --default-index "${PYPI_INDEX_URL}" \
        --index "${PYPI_EXTRA_INDEX_URL}" \
        --index-strategy unsafe-best-match \
        --only-binary=:all: \
        --no-binary=antlr4-python3-runtime \
        --no-binary=crcmod \
        --no-binary=tos \
        -r requirements.txt

COPY . .

# The runtime probes :8000 for readiness — the server must listen here.
EXPOSE 8000
CMD ["python", "main.py"]
