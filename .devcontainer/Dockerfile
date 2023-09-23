FROM python:slim
# FROM python:3.10.2-slim

RUN apt update \
    && apt install -y --no-install-recommends \
    apt-utils \
    git \
    gcc \
    build-essential \
    ca-certificates \
    procps \
    && pip install --no-cache-dir \
    autopep8 \
    flake8 \
    pytest \
    && apt autoremove -y \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/*
