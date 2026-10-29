#!/usr/bin/env python3
"""Match GM 2026 raw entries vs saved-list; classify 新規/既存/要確認; flag pool overlaps."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from gm_match import norm  # importing gm_match re-runs pool parse (harmless, regenerates gm-pools.json)

BASE = Path.home() / "workspace/tabelog-to-google-maps"
data = json.loads((BASE / "gm-pools.json").read_text(encoding="utf-8"))
saved = data["saved"]; pools = data["pools"]

# ---------- load GM raw ----------
gm = []
for f in sorted((BASE / "gm-raw").glob("*.txt")):
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line: continue
        parts = line.split("|")
        assert len(parts) == 6, f"{f.name}: {line}"
        name, pref, area, toque, score, genre = [p.strip() for p in parts]
        gm.append({"name": name, "pref": pref, "area": area, "toque": toque,
                   "score": score, "genre": genre, "norm": norm(name), "src": f.name})
print(f"GM raw total: {len(gm)}")

# dedupe within GM by (norm, pref)
seen = {}
dups = []
for g in gm:
    k = (g["norm"], g["pref"])
    if k in seen: dups.append(g)
    else: seen[k] = g
gm = list(seen.values())
print(f"GM after dedupe: {len(gm)} (dups removed: {len(dups)})")
for d in dups: print("  DUP:", d["name"], d["pref"])

# ---------- indexes ----------
from collections import defaultdict, Counter
saved_by_norm = defaultdict(list)
for s in saved: saved_by_norm[s["norm"]].append(s)
pool_by_norm = {k: defaultdict(list) for k in pools}
for k, lst in pools.items():
    for p in lst: pool_by_norm[k][p["norm"]].append(p)

def edit_dist(a, b, cap=2):
    if abs(len(a) - len(b)) > cap: return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        lo = cap + 1
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + (ca != cb))
            lo = min(lo, cur[j])
        if lo > cap: return cap + 1
        prev = cur
    return prev[len(b)]

ALIASES = {norm("4000 Chinese Restaurant"): [norm("ヨンセン チャイニーズ レストラン")],
           norm("PAUL"): [norm("ポール")]}
def all_norms(g):
    return [g["norm"]] + ALIASES.get(g["norm"], [])

# count-aware exact matching: GM entries per norm vs saved count per norm
gm_norm_counts = Counter(g["norm"] for g in gm)
results = []
for g in gm:
    cands = []
    for n in all_norms(g):
        cands += saved_by_norm.get(n, [])
    entry = dict(g)
    if cands and gm_norm_counts[g["norm"]] <= len(cands):
        entry["status"] = "既存"
        entry["saved"] = [{"name": s["name"], "stations": s["stations"], "genre": s["genre"]} for s in cands]
    elif cands:
        entry["status"] = "要確認"
        entry["reason"] = "同名が保存側件数を超過"
        entry["saved"] = [{"name": s["name"], "stations": s["stations"], "genre": s["genre"]} for s in cands]
    else:
        # near match search
        near = []
        gn = g["norm"]
        for s in saved:
            sn = s["norm"]
            if not sn or not gn: continue
            if len(gn) >= 3 and len(sn) >= 3 and (gn in sn or sn in gn):
                near.append((0, s))
            elif len(gn) >= 4 and edit_dist(gn, sn) <= 2:
                near.append((1, s))
        if near:
            near.sort(key=lambda x: x[0])
            entry["status"] = "要確認"
            entry["reason"] = "店名が類似する保存店あり"
            entry["saved"] = [{"name": s["name"], "stations": s["stations"], "genre": s["genre"]} for _, s in near[:3]]
        else:
            entry["status"] = "新規"
            flags = [k for k in pools if any(n in pool_by_norm[k] for n in all_norms(g))]
            entry["pools"] = flags
    results.append(entry)

st = Counter(r["status"] for r in results)
print("status:", dict(st))
new = [r for r in results if r["status"] == "新規"]
pool_overlap = Counter()
for r in new:
    for p in r["pools"]: pool_overlap[p] += 1
print("新規の他プール重複:", dict(pool_overlap))
print("新規で他プールと重複する店数:", sum(1 for r in new if r["pools"]))
json.dump({"results": results, "dups": dups}, open(BASE / "gm-match-results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote gm-match-results.json")
