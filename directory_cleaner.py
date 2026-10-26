#!/usr/bin/env python3
"""MediDirectory Cleaner - turns messy, publicly listed healthcare practice data
into a clean, validated, de-duplicated directory with an HTML quality report.
AI step (optional): set GEMINI_API_KEY (or GROQ_API_KEY) to classify free-text services with an LLM;
without a key a keyword classifier is used, so the tool always runs offline."""
import csv, html, json, os, re, sys, urllib.request
from pathlib import Path

CATEGORIES = ["General Practice", "Paediatrics", "Women's Health", "Dermatology",
              "Mental Health", "Chronic Disease", "Remote/Telehealth", "Other"]
KEYWORDS = {"General Practice": ["gp", "general"], "Paediatrics": ["paediatric", "child"], "Women's Health": ["women", "antenatal"],
            "Dermatology": ["dermat", "skin"], "Mental Health": ["mental"],
            "Chronic Disease": ["diabetes", "chronic"], "Remote/Telehealth": ["remote", "telehealth"]}
AREA = {"NSW": "02", "ACT": "02", "VIC": "03", "TAS": "03", "QLD": "07", "SA": "08", "WA": "08", "NT": "08"}
RANGES = {"NSW": [(1000, 2599), (2619, 2899), (2921, 2999)], "ACT": [(2600, 2618), (2900, 2920)],
          "VIC": [(3000, 3999)], "QLD": [(4000, 4999)], "SA": [(5000, 5799)],
          "WA": [(6000, 6797)], "TAS": [(7000, 7799)], "NT": [(800, 899)]}

def title(s):
    s = re.sub(r"\s+", " ", s.strip())
    s = re.sub(r"\b([A-Za-z])([A-Za-z']*)", lambda m: m.group(1).upper() + m.group(2).lower(), s)
    return re.sub(r"\b([OD]')([a-z])", lambda m: m.group(1) + m.group(2).upper(), s)

def fix_doctor(s):
    s = title(s)
    return re.sub(r"^Dr\.?\s*", "Dr ", s)

def clean_phone(raw, state):
    d = re.sub(r"\D", "", raw or "")
    if d.startswith("61") and len(d) == 11: d = "0" + d[2:]
    if len(d) == 8 and state in AREA: d = AREA[state] + d; note = "area code inferred from state"
    else: note = ""
    if re.fullmatch(r"04\d{8}", d): return f"{d[:4]} {d[4:7]} {d[7:]}", note
    if re.fullmatch(r"0[2378]\d{8}", d): return f"({d[:2]}) {d[2:6]} {d[6:]}", note
    if re.fullmatch(r"1[38]00\d{6}", d): return f"{d[:4]} {d[4:7]} {d[7:]}", note
    return "", "invalid phone"

def valid_email(e):
    return bool(re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", e or ""))

def postcode_ok(state, pc):
    return pc.isdigit() and any(a <= int(pc) <= b for a, b in RANGES.get(state, []))

def classify_rules(text):
    t = text.lower()
    for cat, kws in KEYWORDS.items():
        if any(k in t for k in kws): return cat
    return "Other"

_warned = False

def _warn(msg):
    global _warned
    if not _warned:
        print("AI step failed, using keyword rules instead:", msg, file=sys.stderr); _warned = True

def _ask_llm(prompt):
    """Returns the model's text reply. Uses Gemini if GEMINI_API_KEY is set, else Groq if GROQ_API_KEY is set."""
    if os.getenv("GEMINI_API_KEY"):
        model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            data=json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                             "generationConfig": {"temperature": 0}}).encode(),
            headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
        data = json.load(urllib.request.urlopen(req, timeout=30))
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps({"model": "llama-3.1-8b-instant", "temperature": 0,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}", "Content-Type": "application/json",
                 "User-Agent": "medidirectory-cleaner"})
    return json.load(urllib.request.urlopen(req, timeout=20))["choices"][0]["message"]["content"].strip()

def classify_ai(text):
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY")):
        return classify_rules(text), "rules"
    prompt = (f"Classify these clinic services into exactly one of {CATEGORIES}. "
              f"Reply with the category name only.\nServices: {text}")
    try:
        out = _ask_llm(prompt).strip().strip(".")
        if out in CATEGORIES: return out, "ai"
        _warn(f"unexpected reply: {out!r}")
    except Exception as e:
        _warn(str(e))
    return classify_rules(text), "rules"

def process(rows):
    cleaned, seen, dupes = [], {}, 0
    for r in rows:
        state = r["state"].strip().upper()
        phone, pnote = clean_phone(r["phone"], state)
        email = r["email"].strip().lower()
        pc = r["postcode"].strip().zfill(4)
        issues = [x for x in [pnote] if x]
        if not valid_email(email): issues.append("missing/invalid email" if not email else "invalid email"); email = ""
        if not postcode_ok(state, pc): issues.append("postcode/state mismatch")
        cat, how = classify_ai(r["services"])
        rec = {"practice": title(r["practice_name"]), "doctor": fix_doctor(r["doctor_name"]), "phone": phone,
               "email": email, "suburb": title(r["suburb"]), "state": state, "postcode": pc,
               "category": cat, "classified_by": how}
        rec["score"] = max(0, 100 - 25 * sum(i in ("invalid phone", "postcode/state mismatch") for i in issues)
                           - 15 * sum("email" in i for i in issues) - 5 * (pnote != "" and "invalid" not in pnote))
        rec["issues"] = "; ".join(issues)
        key = (rec["practice"].lower(), rec["doctor"].lower(), rec["postcode"])
        if key in seen:
            dupes += 1
            if rec["score"] > seen[key]["score"]: seen[key].update(rec)
            continue
        seen[key] = rec; cleaned.append(rec)
    return cleaned, dupes

def report(cleaned, total, dupes, path):
    cats = {}
    for r in cleaned: cats[r["category"]] = cats.get(r["category"], 0) + 1
    flagged = sum(1 for r in cleaned if r["issues"])
    rows = "".join(f"<tr><td>{html.escape(r['practice'])}</td><td>{html.escape(r['doctor'])}</td><td>{r['phone']}</td>"
                   f"<td>{html.escape(r['email'])}</td><td>{html.escape(r['suburb'])} {r['state']} {r['postcode']}</td>"
                   f"<td>{html.escape(r['category'])}</td><td>{r['score']}</td><td>{html.escape(r['issues'])}</td></tr>" for r in cleaned)
    catli = "".join(f"<li>{html.escape(k)}: {v}</li>" for k, v in sorted(cats.items()))
    Path(path).write_text(f"""<!doctype html><meta charset=utf-8><title>MediDirectory report</title>
<style>body{{font:15px system-ui;margin:2rem auto;max-width:1000px;padding:0 1rem}}table{{border-collapse:collapse;width:100%}}
td,th{{border:1px solid #ccc;padding:6px;text-align:left}}th{{background:#eef}}.k{{display:flex;gap:1rem}}.k div{{background:#f4f6fa;padding:1rem;border-radius:8px}}</style>
<h1>MediDirectory Cleaner - Quality Report</h1>
<div class=k><div><b>{total}</b><br>raw rows</div><div><b>{dupes}</b><br>duplicates merged</div>
<div><b>{len(cleaned)}</b><br>clean records</div><div><b>{flagged}</b><br>need review</div></div>
<h3>By category</h3><ul>{catli}</ul><table><tr><th>Practice<th>Doctor<th>Phone<th>Email<th>Location<th>Category<th>Score<th>Issues</tr>{rows}</table>""", encoding="utf-8")

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "sample_data/practices_raw.csv"
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "output"); out.mkdir(exist_ok=True)
    with open(src, newline="", encoding="utf-8") as f: rows = list(csv.DictReader(f))
    cleaned, dupes = process(rows)
    with open(out / "clean_directory.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cleaned[0])); w.writeheader(); w.writerows(cleaned)
    report(cleaned, len(rows), dupes, out / "report.html")
    print(f"{len(rows)} rows -> {len(cleaned)} clean ({dupes} duplicates merged, "
          f"{sum(1 for r in cleaned if r['issues'])} flagged). See {out}/")

if __name__ == "__main__": main()
