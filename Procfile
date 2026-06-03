release: alembic upgrade head && python -m webapp.seed
web: uvicorn webapp.server:app --host 0.0.0.0 --port $PORT
