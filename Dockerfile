FROM python:3.14-alpine


ENV GSEEKBOT_LOG_FILE=/data/bot.log

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_SYSTEM_PYTHON=1


RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,target=/build_src,ro \
    uv pip install /build_src
    
    
CMD [ "gseek-bot" ]