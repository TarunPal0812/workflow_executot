run-dev:
	set APP_ENV=development && uv run fastapi dev --port 8000

run-prod:
	set APP_ENV=production && uv run fastapi dev --port 9090
