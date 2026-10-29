#!/usr/bin/env python3
"""Second pass: plausible near candidates + unmatched Kansai saved entries."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from prep_match import norm
from run_match import edit_dist, KANSAI_HINT  # noqa

BASE = Path.home() / "workspace/tabelog-to-google-maps"
prep = json.loads((BASE / "match-prep.json").read_text(encoding="utf-8"))
saved = prep["saved"]
results = json.loads((BASE / "match-results.json").read_text(encoding="utf-8"))

def bigrams(s):
    return {s[i:i+2] for i in range(len(s) - 1)} if len(s) > 1 else {s}

matched_saved_keys = set()
rows = []
for e in results:
    if e["status"] == "exact1":
        matched_saved_keys.add((e["saved"][0]["no"], e["saved"][0]["section"]))
        continue
    mn = e["norm"]
    cands = []
    for s in saved:
        sn = s["norm"]
        if not sn or not mn:
            continue
        cont = (sn in mn or mn in sn)
        d = edit_dist(sn, mn, 2) if abs(len(sn) - len(mn)) <= 2 else 99
        bg = bigrams(sn) & bigrams(mn)
        jac = len(bg) / max(1, len(bigrams(sn) | bigrams(mn)))
        if cont or d <= 1 or (d == 2 and jac >= 0.4):
            cands.append((0 if cont else d, -jac, s))
    cands.sort(key=lambda t: (t[0], t[1]))
    if cands:
        rows.append((e, [c[2] for c in cands[:4]]))

print(f"== plausible-near rows: {len(rows)} ==")
for e, cs in rows:
    sv = " ;; ".join(f"No.{s['no']}({s['section']}) {s['name']} ― {s['stations']}／{s['genre']}" for s in cs)
    print(f"{e['city']}\t{e['kubun']}\t{e['name']}\t{e['area']}\t{e['genre']}\t{sv}")

print()
print("== unmatched saved entries with Kansai-looking stations ==")
unmatched = [s for s in saved
             if (s["no"], s["section"]) not in matched_saved_keys
             and KANSAI_HINT.search(s["stations"])]
# remove ones already appearing as near candidates above is overkill; print all
for s in unmatched:
    print(f"No.{s['no']}({s['section']}) {s['name']} ― {s['stations']}／{s['genre']}")
print(f"count: {len(unmatched)}")
