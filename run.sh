#!/usr/bin/env bash
set -e
if [ ! -d ".venv" ]; then python3.11 -m venv .venv; fi
source .venv/bin/activate
pip install -r requirements.txt
if [ ! -f ".env" ]; then cp .env.example .env; fi
uvicorn app.main:app --reload
