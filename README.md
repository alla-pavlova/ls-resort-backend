# LS Resort Backend

Backend for a wellness-oriented web platform built with FastAPI.
Includes services, reviews, contact forms, authentication, admin routes, and search.

This repository contains the FastAPI backend for a wellness-oriented web platform.
It includes public-facing routes, reviews, contact forms, authentication, admin features, and API documentation.

## Project Purpose

Backend supports:
- Authentication (JWT)
- Google OAuth login
- Admin bootstrap logic
- Contact forms and service endpoints
- Body restoration studio infrastructure

Frontend demo: https://lebedi.pages.dev

## Tech Stack
- FastAPI
- Uvicorn
- Pydantic
- Async SQLAlchemy (aiosqlite)
- SQLite (development)
- JWT Authentication

## Quick start (Windows)

```bash
git clone https://github.com/alla-pavlova/ls-resort-backend.git
cd ls-resort-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run (choose the correct entrypoint)
uvicorn app.main:app --reload
# OR if entrypoint is in root main.py:
# uvicorn main:app --reload
