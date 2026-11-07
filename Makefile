PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e .

fmt:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check . --fix

test:
	$(PYTHON) -m pytest -q

run:
	$(PYTHON) -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

eval:
	$(PYTHON) -m evaluation

lab:
	$(PYTHON) -m lab
