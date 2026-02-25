.PHONY: daily weekly all clean

daily:
	python3 scripts/run_daily_pipeline.py

weekly:
	python3 scripts/run_weekly_review.py

all: daily weekly

clean:
	rm -f data/outputs/daily_report.md data/outputs/run_summary.json data/outputs/weekly_review.md data/processed/features.csv data/processed/predictions.csv
