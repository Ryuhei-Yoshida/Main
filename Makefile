PYTHON ?= python3

.PHONY: daily weekly run-all

daily:
	$(PYTHON) scripts/run_daily_pipeline.py

weekly:
	$(PYTHON) scripts/run_weekly_review.py

run-all: daily weekly
