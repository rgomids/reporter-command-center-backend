PYTHON ?= python3
PIP ?= pip3

.PHONY: setup run dev test lint typecheck cc quality openapi

setup:
	$(PIP) install -r requirements.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port $$PORT --proxy-headers

dev:
	UVICORN_WORKERS=1 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -q --cov=app --cov-report=term-missing --cov-report=xml:reports/coverage.xml

lint:
	ruff check app tests

typecheck:
	mypy app

cc:
	@mkdir -p reports
	radon cc -s -a app | tee reports/cc.txt
	radon cc -n 10 app | tee reports/cc_fail.txt
	@test ! -s reports/cc_fail.txt || (echo "Complexidade > 10 detectada" && exit 1)

quality: lint typecheck test cc

openapi:
	curl -s http://localhost:8000/openapi.json -o reports/openapi.json

