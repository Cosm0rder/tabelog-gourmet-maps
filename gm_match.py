#!/usr/bin/env python3
"""Gault&Millau 2026 matching: parse pools, verify counts; match GM raw vs saved+pools."""
import json, re, sys, unicodedata
from pathlib import Path

BASE = Path.home() / "workspace/tabelog-to-google-maps"

def expand_iteration(s: str) -> str:
    out = []
    for ch in s:
        if ch in "ゝヽ" and out:
            out.append(out[-1])
        elif ch in "ゞヾ" and out:
            prev = out[-1]
            voiced = unicodedata.normalize("NFC", prev + "゙")
            out.append(voiced if len(voiced) == 1 else prev)
        else:
            out.append(ch)
    return "".join(out)

VAR = str.maketrans({
    "ヶ": "ケ", "ヵ": "カ", "ゎ": "わ",
    "﨑": "崎", "嵜": "崎", "齋": "斉", "齊": "斉",
    "櫻": "桜", "龍": "竜", "嶋": "島", "槇": "槙",
})
def norm(name: str) -> str:
    s = unicodedata.normalize("NFKC", name)
    s = expand_iteration(s)
    s = s.translate(VAR)
    s = re.sub(r"[\s　・·‐\-\―—/／'’\"\"「」『』()（）\[\]]", "", s)
    return s.lower()

# ---------- saved-list ----------
def parse_saved():
    saved, section = [], "main"
    for line in (BASE / "saved-list.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## コレクション"): section = "collection"
        elif line.startswith("## 行ったお店"): section = "visited"
        elif line.startswith("## 保存リスト"): section = "main"
        m = re.match(r"^(\d+)\. (.+?) ― (.+?) ― (.+)$", line)
        if m:
            no, name, area, rating = m.groups()
            parts = area.split("／")
            saved.append({"no": int(no), "section": section, "name": name,
                          "stations": parts[0], "genre": parts[1] if len(parts) > 1 else "",
                          "rating": rating, "norm": norm(name)})
    return saved

# ---------- pool parsers: collect names under 新規 headings ----------
def pool_names_award():
    names, in_new = [], False
    for line in (BASE / "award2026.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## 新規"): in_new = True; continue
        if in_new and line.startswith("## "): break
        if in_new and line.startswith("- "):
            f = line[2:].split("｜")
            if len(f) >= 2: names.append(f[0].strip())
    return names

def pool_names_heading_files(fname):
    """michelin / hyakumeiten files: '- name｜...' lines under any heading containing 新規."""
    names, in2, in3 = [], False, False
    for line in (BASE / fname).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in2 = line[3:].startswith("新規"); in3 = False; continue
        if line.startswith("### "):
            in3 = "新規" in line; continue
        if line.startswith("#"):
            continue
        if (in2 or in3) and line.startswith("- "):
            body = line[2:].strip()
            if body.startswith("※"): continue
            f = body.split("｜")
            nm = f[0].strip()
            nm = re.sub(r"\s*【.+】$", "", nm)
            if nm: names.append(nm)
    return names

if __name__ == "__main__":
    saved = parse_saved()
    print(f"saved: {len(saved)}")
    pools = {
        "award": pool_names_award(),
        "michelin": pool_names_heading_files("michelin-tokyo2026.md"),
        "hyaku2026": pool_names_heading_files("hyakumeiten-2026-new.md"),
        "hyakuolder": pool_names_heading_files("hyakumeiten-older-new.md"),
    }
    for k, v in pools.items():
        print(f"{k}: {len(v)}")
    json.dump({"pools": {k: [{"name": n, "norm": norm(n)} for n in v] for k, v in pools.items()},
               "saved": saved}, open(BASE / "gm-pools.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("wrote gm-pools.json")
