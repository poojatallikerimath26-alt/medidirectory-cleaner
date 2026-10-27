# Prompt Documentation - MediDirectory Cleaner

Task 1: AI Skills & Prompt Engineering Assessment - AI Growth & Automation Associate (Gokul Infocare)
Candidate: Pooja Tallikerimath

## AI tools used
- **Claude (Anthropic)**: planning, writing and testing the Python code, documentation and the video script.
- **Google Gemini API (gemini-3.1-flash-lite)**: runs inside the finished tool to classify clinic services into categories. Groq was my first choice for this step, but its sign-in was down, so I switched to Gemini.

## 1. Task framing
**Prompt (my words):** "i got this mail to do work complete this assignment and here this is the job i applied that job description here" - I attached the assessment email, the job description and the Task 1 PDF.

**Why:** I gave the AI the full brief and the job description together so the project would match the exact requirements (one project, healthcare/technology, AI used meaningfully, video + prompts + link).

**Result:** Claude noticed the task PDF was missing and asked for it instead of guessing, then proposed an Automation + Data Intelligence project: a tool that cleans, validates and categorises healthcare practice listings.

## 2. Checking requirements before building further
**Prompt:** "what they asked do that one... check what they ask to do and what we have to do tell me first and what to do next what remains after this all"

**Why:** I wanted to avoid being rejected for doing something different from the brief.

**Result:** A requirement-by-requirement checklist. It showed one weak point: the AI step only ran when an API key was set, so I decided to make it work and demonstrate it.

## 3. Making the AI step real - debugging with follow-up prompts

| What I saw | What I did / asked | Outcome |
|---|---|---|
| Groq sign-in showed a redirect-URL error (twice, Google and email login) | Shared screenshots and asked for another option | Switched the AI step to Google Gemini; the script supports Gemini and Groq |
| Gemini returned HTTP 404 Not Found | Shared the screenshot of the error | The old model name had been retired. Checked current model names and set gemini-3.1-flash-lite |
| Gemini returned HTTP 503 Service Unavailable | Waited and ran again | Google was briefly busy; the retry worked |
| Checked clean_directory.csv | Looked at the classified_by column | All rows show "ai", proving Gemini classified them |

## 4. Improvements found while testing
Running the tool on deliberately messy fictional data showed two problems, fixed with targeted follow-up changes:
- "General practice; child health" was classified as Paediatrics. Fix: General Practice now takes priority when listed first.
- "O'Brien" became "O'brien". Fix: added a casing rule for O' and D' surnames.
- The AI step now prints the reason if it fails, instead of failing silently, which made the 404 and 503 errors easy to diagnose.

## 5. What the final project does
Reads a messy CSV of practice listings; normalises names and Australian phone numbers; infers missing area codes from the state; validates emails and postcode-vs-state; merges duplicates; gives each record a 0-100 quality score; classifies services with Gemini (keyword rules as fallback); writes clean_directory.csv and an HTML quality report. On the sample data: 10 raw rows became 8 clean records, 2 duplicates merged, 5 flagged for review.

## What I learned about prompting
Giving the AI the complete brief, sharing the exact error screenshots, and asking it to check requirements before building made the results more accurate. Always verify AI output by running it: testing found real bugs and a retired model name that I would not have known otherwise.
