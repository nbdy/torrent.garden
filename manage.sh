#!/bin/bash

uv run reflex db init
uv run reflex db makemigrations
uv run reflex db migrate
uv run reflex run --backend-only --env prod
