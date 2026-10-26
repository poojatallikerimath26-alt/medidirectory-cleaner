# Prompt Documentation - MediDirectory Cleaner
Tool used: Claude (Anthropic) for design, code and testing; Groq (Llama 3.1) is used inside the project for service classification.

## 1. Task framing
**Prompt:** "I'm applying for an AI Growth & Automation role. Here is the assessment brief and job description. Pick ONE area and propose a project that is runnable by reviewers with no setup, uses AI meaningfully, and relates to healthcare."
**Why:** Giving the full brief and constraints (no setup, healthcare, AI must matter) steers the AI toward a feasible scope instead of a generic idea.
**Result:** Chose Automation + Data Intelligence: a cleaning pipeline for public practice listings.

## 2. Build prompt
**Prompt:** "Write a Python CLI using only the standard library that reads a CSV of healthcare practices and: normalises names and Australian phone numbers, infers missing area codes from the state, validates email and postcode-vs-state, merges duplicates, scores quality 0-100, and writes a clean CSV plus an HTML report. Add an optional LLM step (Groq API) that classifies services into fixed categories and falls back to keyword rules when no API key is set."
**Why:** Specific inputs, outputs, constraints and a fallback requirement make the result testable.

## 3. Test-data prompt
**Prompt:** "Generate 10 fictional practice rows with deliberate problems: mixed casing, +61 and local phone formats, a missing area code, a bad email, a wrong postcode, an invalid phone, and two duplicates."
**Why:** Deliberately messy fictional data tests every rule without using anyone's real details.

## 4. Revisions after running it (real issues found)
| Problem seen in output | Follow-up prompt | Fix |
|---|---|---|
| "General practice; child health" was classified as Paediatrics | "Check category priority - a clinic listing general practice first should be General Practice." | Reordered keyword rules |
| "O'Brien" became "O'brien" | "Fix name casing for O' and D' surnames." | Added apostrophe-capitalisation rule |

## 5. Add your own
Add any extra prompts you wrote yourself (e.g. for the video script or the report styling) here, with what you changed and why. Reviewers value your own iteration.
