#!/usr/bin/env python3
"""Match TRY Ramen Award shops against saved-list and the 4 new-shop pools. v2"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from prep_match import norm as base_norm

def norm(s):
    # extend shared normalization with ramen-specific glyph variants
    return base_norm(s).replace("㐂", "喜").replace("髙", "高")

BASE = Path.home() / "workspace/tabelog-to-google-maps"
prep = json.loads((BASE / "match-prep.json").read_text(encoding="utf-8"))
saved = prep["saved"]
for s in saved:
    s["norm"] = norm(s["name"])
award_new = prep["award_new"]
for a in award_new:
    a["norm"] = norm(a["name"])

def edit_dist(a, b, cap=2):
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        lo = cap + 1
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
            lo = min(lo, cur[j])
        if lo > cap:
            return cap + 1
        prev = cur
    return prev[len(b)]

def parse_bracket_new(path):
    """'- name｜area' lines inside '### 新規' subsections (hyakumeiten style)."""
    out = {}
    in_new = False
    for line in (BASE / path).read_text(encoding="utf-8").splitlines():
        if line.startswith("### 新規"):
            in_new = True
            continue
        if line.startswith("## ") or line.startswith("### "):
            in_new = False
        if in_new and line.startswith("- "):
            parts = line[2:].split("｜")
            if len(parts) >= 2:
                nm = parts[0].strip()
                out.setdefault(norm(nm), {"name": nm, "area": parts[1].strip()})
    return out

def parse_michelin_new():
    """Michelin file: everything between '## 新規' and '## 付記' (has ### subsections)."""
    out = {}
    in_new = False
    for line in (BASE / "michelin-tokyo2026.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## 新規"):
            in_new = True
            continue
        if in_new and line.startswith("## "):
            in_new = False
        if in_new and line.startswith("- "):
            parts = line[2:].split("｜")
            if len(parts) >= 2:
                nm = parts[0].strip()
                out.setdefault(norm(nm), {"name": nm, "area": parts[1].strip()})
    return out

def parse_full_area(path, area_idx):
    out = {}
    for line in (BASE / path).read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and "｜" in line:
            parts = line[2:].split("｜")
            if len(parts) > area_idx:
                nm = parts[0].strip()
                ar = re.sub(r"\s*【.+?】\s*$", "", parts[area_idx].strip())
                k = norm(nm)
                if k not in out:
                    out[k] = ar
    return out

michelin_new = parse_michelin_new()
hyaku26_new = parse_bracket_new("hyakumeiten-2026-new.md")
hyakuold_new = parse_bracket_new("hyakumeiten-older-new.md")
award_new_by_norm = {a["norm"]: a for a in award_new}
print("pool sizes:", len(michelin_new), len(hyaku26_new), len(hyakuold_new), len(award_new_by_norm))

award_area = parse_full_area("award2026.md", 2)
michelin_area = parse_full_area("michelin-tokyo2026.md", 1)
ramen_area = {}
for line in (BASE / "hyakumeiten-raw/raw-ramen.md").read_text(encoding="utf-8").splitlines():
    if "｜" in line and not line.startswith("#"):
        nm, pref = line.split("｜", 1)
        ramen_area.setdefault(norm(nm.strip()), pref.strip())

saved_by_norm = {}
for s in saved:
    saved_by_norm.setdefault(s["norm"], []).append(s)

entries = []
for line in (BASE / "try-raw.tsv").read_text(encoding="utf-8").splitlines()[1:]:
    if not line.strip():
        continue
    f = line.split("\t")
    f += [""] * (6 - len(f))
    ed, grp, cat, rank, name, area_note = f[:6]
    entries.append({"edition": int(ed), "group": grp, "category": cat,
                    "rank": rank, "name": name.strip(), "area_note": area_note.strip(),
                    "norm": norm(name)})

ALIAS = {norm("べんてん"): norm("中華そば べんてん")}
shops = {}
for e in entries:
    key = ALIAS.get(e["norm"], e["norm"])
    sh = shops.setdefault(key, {"key": key, "names": [], "results": [], "area_note": ""})
    if e["name"] not in sh["names"]:
        sh["names"].append(e["name"])
    sh["results"].append(e)
    if e["area_note"] and not sh["area_note"]:
        sh["area_note"] = e["area_note"]

def pool_hits(key):
    hits = []
    if key in award_new_by_norm:
        hits.append(("アワード2026新規", award_new_by_norm[key]["pref"]))
    if key in michelin_new:
        hits.append(("ミシュラン東京2026新規", "東京都" + michelin_new[key]["area"]))
    if key in hyaku26_new:
        hits.append(("百名店2026新規", hyaku26_new[key]["area"]))
    if key in hyakuold_new:
        hits.append(("百名店旧年版新規", hyakuold_new[key]["area"]))
    return hits

def pool_near(key):
    pools = [("アワード2026新規", award_new_by_norm), ("ミシュラン東京2026新規", michelin_new),
             ("百名店2026新規", hyaku26_new), ("百名店旧年版新規", hyakuold_new)]
    out = []
    for label, pool in pools:
        if key in pool:
            continue
        for pk, pv in pool.items():
            pname = pv["name"] if isinstance(pv, dict) else pk
            if len(key) >= 4 and len(pk) >= 4 and (key in pk or pk in key):
                out.append((label, pname))
                break
    return out

def area_for(sh, key):
    if sh["area_note"]:
        return sh["area_note"]
    for src in (award_area, michelin_area, ramen_area):
        if key in src:
            return src[key]
    hits = pool_hits(key)
    if hits:
        return hits[0][1]
    return ""

# manual review: algorithmic near-hits in saved that are actually different shops -> force 新規
FORCE_NEW = {
    norm("ラーメン 星印"), norm("麺処 ら塾"), norm("ラーメン 郷"),
    norm("麺処 一笑"), norm("ラーメン 男盛"), norm("らーめん 文蔵"),
}

results = []
for key, sh in shops.items():
    disp = sh["names"][0]
    cands = saved_by_norm.get(key, [])
    rec = {"shop": sh, "display": disp, "key": key}
    if cands:
        rec["status"] = "既存"
        rec["saved"] = cands
    else:
        near = []
        if key not in FORCE_NEW:
            for sn, ss in saved_by_norm.items():
                if len(key) >= 3 and len(sn) >= 3 and (key in sn or sn in key):
                    near.append((ss[0], "包含"))
                elif len(key) >= 4 and edit_dist(key, sn, 2) <= 2:
                    near.append((ss[0], "近接"))
        if near:
            rec["status"] = "要確認"
            seen = set(); uniq = []
            for s0, why in near:
                if s0["name"] not in seen:
                    seen.add(s0["name"]); uniq.append((s0, why))
            rec["near"] = uniq[:3]
        else:
            rec["status"] = "新規"
            rec["pools"] = pool_hits(key)
            rec["pool_near"] = pool_near(key)
            rec["area"] = area_for(sh, key)
    results.append(rec)

json.dump({"entries": entries,
           "shops": [{"display": r["display"], "status": r["status"],
                      "names": r["shop"]["names"],
                      "results": [{"edition": e["edition"], "group": e["group"], "category": e["category"], "rank": e["rank"]} for e in r["shop"]["results"]],
                      "saved": [{"name": s["name"], "stations": s["stations"], "genre": s["genre"]} for s in r.get("saved", [])],
                      "near": [s0["name"] for s0, _ in r.get("near", [])],
                      "pools": [p for p, _ in r.get("pools", [])],
                      "pool_near": r.get("pool_near", []),
                      "area": r.get("area", "")} for r in results]},
          open(BASE / "try-match.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

from collections import Counter
n27 = len({ALIAS.get(e["norm"], e["norm"]) for e in entries if e["edition"] == 27})
n26 = len({ALIAS.get(e["norm"], e["norm"]) for e in entries if e["edition"] == 26})
c = Counter(r["status"] for r in results)
print(f"entries: {len(entries)} (27th: {sum(1 for e in entries if e['edition']==27)}, 26th: {sum(1 for e in entries if e['edition']==26)})")
print(f"unique shops: total {len(results)} (27th {n27}, 26th {n26})")
print("status:", dict(c))
for r in results:
    if r["status"] == "新規" and r.get("pools"):
        print("  POOL:", r["display"], "->", r["pools"])
print("--- confirm ---")
for r in results:
    if r["status"] == "要確認":
        print(" ", r["display"], "->", [(s0["name"], w) for s0, w in r["near"]])
print("--- new pool-near (containment) ---")
for r in results:
    if r["status"] == "新規" and r.get("pool_near"):
        print(" ", r["display"], "->", r["pool_near"])
print("--- existing ---")
for r in results:
    if r["status"] == "既存":
        print(" ", r["display"], "->", [s["name"] for s in r["saved"]])
miss = [r["display"] for r in results if r["status"] == "新規" and not r.get("area")]
print("new area missing:", len(miss))
print(miss)
