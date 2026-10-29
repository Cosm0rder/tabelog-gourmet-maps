#!/usr/bin/env python3
"""Prepare parsed data for Michelin Kyoto-Osaka 2026 matching."""
import json, re, unicodedata
from pathlib import Path

BASE = Path.home() / "workspace/tabelog-to-google-maps"

# ---------- normalization ----------
def expand_iteration(s: str) -> str:
    out = []
    for ch in s:
        if ch in "ゝヽ" and out:
            out.append(out[-1])
        elif ch in "ゞヾ" and out:
            prev = out[-1]
            # add dakuten roughly: map via unicodedata normalize trick
            voiced = unicodedata.normalize("NFC", prev + "゙")
            out.append(voiced if len(voiced) == 1 else prev)
        else:
            out.append(ch)
    return "".join(out)

VAR = str.maketrans({
    "ヶ": "ケ", "ヵ": "カ", "ゎ": "わ",
    "﨑": "崎", "嵜": "崎", "齋": "斉", "齊": "斉",
    "櫻": "桜", "龍": "竜", "嶋": "島", "槇": "槙",
    "遥": "遙",  # keep? risky; leave as-is instead
})
def norm(name: str) -> str:
    s = unicodedata.normalize("NFKC", name)
    s = expand_iteration(s)
    s = s.translate(VAR)
    s = re.sub(r"[\s　・·‐\-―—/／'’\"\"「」『』()（）\[\]]", "", s)
    return s.lower()

# ---------- parse saved-list.md ----------
saved = []
section = "main"
for line in (BASE / "saved-list.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## コレクション"):
        section = "collection"
    elif line.startswith("## 行ったお店"):
        section = "visited"
    elif line.startswith("## 保存リスト"):
        section = "main"
    m = re.match(r"^(\d+)\. (.+?) ― (.+?) ― (.+)$", line)
    if m:
        no, name, area, rating = m.groups()
        parts = area.split("／")
        stations = parts[0]
        genre = parts[1] if len(parts) > 1 else ""
        saved.append({
            "no": int(no), "section": section, "name": name,
            "stations": stations, "genre": genre, "rating": rating,
            "norm": norm(name),
        })
print(f"saved parsed: {len(saved)}")

# ---------- parse award2026.md 新規 section ----------
award_new = []
in_new = False
for line in (BASE / "award2026.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## 新規"):
        in_new = True
        continue
    if in_new and line.startswith("## "):
        break
    if in_new and line.startswith("- "):
        body = line[2:]
        fields = [f.strip() for f in body.split("｜")]
        if len(fields) >= 4:
            award_new.append({"name": fields[0], "genre": fields[1],
                              "pref": fields[2], "award": fields[3],
                              "norm": norm(fields[0])})
print(f"award new parsed: {len(award_new)}")

(BASE / "match-prep.json").write_text(json.dumps(
    {"saved": saved, "award_new": award_new}, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote match-prep.json")
