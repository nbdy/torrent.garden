FROM python:3.14-trixie

WORKDIR /app

# Build context will be the project root
COPY . .

RUN pip install uv
RUN uv sync

STOPSIGNAL SIGKILL

ENTRYPOINT ["bash", "manage.sh"]
