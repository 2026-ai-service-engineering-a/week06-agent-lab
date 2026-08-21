# syntax=docker/dockerfile:1
# Day 1 실습 랩 이미지: Python + litellm + pydantic + pytest.
# compose가 저장소를 /app에 바인드 마운트하므로, 이미지는 의존성만 담는다.
FROM python:3.13-slim

WORKDIR /app

# 의존성 레이어 — requirements.txt가 바뀔 때만 다시 설치된다.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# /app을 sys.path에 올려 examples/·agent/·tests/ 가 어디서 실행해도 import 되게.
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1
