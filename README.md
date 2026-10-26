# MediDirectory Cleaner
AI-assisted automation that turns messy, publicly listed healthcare practice data into a clean, validated,
de-duplicated directory plus an HTML quality report. Built for the Gokul Infocare Task 1 (Automation / Data Intelligence).

## Problem
Collected practice listings arrive with inconsistent names, phone formats, missing area codes, bad emails,
wrong postcodes and duplicates. Cleaning by hand is slow and error-prone.

## What it does
- Normalises names (Dr prefixes, O'Brien-style casing) and Australian phone numbers (+61, 04xx, landlines, 13/1300)
- Infers missing area codes from the state, flags what can't be fixed
- Validates emails and postcode-vs-state
- Merges duplicates, keeping the higher quality record; gives each record a 0-100 quality score
- Classifies free-text services into standard categories: **LLM via Groq** if `GROQ_API_KEY` is set, keyword rules otherwise
- Outputs `output/clean_directory.csv` and `output/report.html`

## Run
    python directory_cleaner.py                      # uses sample_data/practices_raw.csv
    python directory_cleaner.py my_data.csv out_dir  # your own CSV (same columns)
    export GROQ_API_KEY=...                          # optional: enables the AI classifier

Sample data is fictional. For real data, use only publicly listed business contact details and respect each
source's terms and Australian privacy/spam rules.
