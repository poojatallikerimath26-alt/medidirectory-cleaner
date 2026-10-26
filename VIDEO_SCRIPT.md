# Video script (~2.5 min) - record yourself on screen + voice
**0:00 Intro (15s)** "Hi, I'm Pooja Tallikerimath. For Task 1 I built MediDirectory Cleaner, an AI-assisted automation that turns messy public healthcare practice listings into a clean, validated directory."
**0:15 Problem (20s)** "Listings come with inconsistent phone formats, bad emails, wrong postcodes and duplicates. Cleaning them manually is slow, so I automated it."
**0:35 AI tools (25s)** "I used Claude to plan and write the code and tests, and Groq's Llama model inside the tool to classify free-text services into categories. I chose Claude for structured code generation and Groq because it's fast and free to start."
**1:00 Prompt engineering (30s)** "My first prompts were vague, so I added the exact inputs, outputs, constraints and a fallback when no API key is set. I also asked for deliberately messy test data. After running it I found two bugs, a wrong category order and O'Brien casing, and fixed them with targeted follow-up prompts."
**1:30 Demo (40s)** SCREEN: run `python directory_cleaner.py`, open output/report.html. "10 raw rows became 8 clean records, 2 duplicates merged, 5 flagged for review. Each record has a quality score and the issues found."
**2:10 Challenges (15s)** "Handling Australian phone formats and missing area codes was the hardest part. I solved it by inferring the area code from the state and flagging what can't be fixed."
**2:25 Close (10s)** "Everything is on GitHub with a README and prompt documentation. Thank you."
Tip: my own experience building Python/FastAPI projects shaped the standard-library-only choice so reviewers can run it instantly. Say this in your own words if it's true for you.
