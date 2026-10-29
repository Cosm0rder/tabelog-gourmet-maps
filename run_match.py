#!/usr/bin/env python3
"""Match Michelin Kyoto-Osaka 2026 raw lists against saved-list and award-new."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from prep_match import norm  # reuse normalization

BASE = Path.home() / "workspace/tabelog-to-google-maps"
prep = json.loads((BASE / "match-prep.json").read_text(encoding="utf-8"))
saved = prep["saved"]
award_new = prep["award_new"]

saved_by_norm = {}
for s in saved:
    saved_by_norm.setdefault(s["norm"], []).append(s)
award_by_norm = {}
for a in award_new:
    award_by_norm.setdefault(a["norm"], []).append(a)

def parse_raw(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        f = line.split("|")
        assert len(f) == 4, f"bad line: {line}"
        rows.append({"name": f[0], "kubun": f[1], "area": f[2], "genre": f[3],
                     "norm": norm(f[0])})
    return rows

kyoto = parse_raw(BASE / "michelin-raw-kyoto.txt")
osaka = parse_raw(BASE / "michelin-raw-osaka.txt")
for r in kyoto: r["city"] = "京都"
for r in osaka: r["city"] = "大阪"
allm = kyoto + osaka
print(f"michelin total: {len(allm)}")

def edit_dist(a, b, cap=3):
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        lo = cap + 1
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + (ca != cb))
            lo = min(lo, cur[j])
        if lo > cap:
            return cap + 1
        prev = cur
    return prev[len(b)]

KANSAI_HINT = re.compile(r"京都|大阪|梅田|北新地|祇園|心斎橋|難波|なんば|天王寺|京橋|江坂|茨木|高槻|西宮|芦屋|宝塚|堺|三宮|神戸|奈良|烏丸|四条|河原町|先斗町|木屋町|上本町|鶴橋|福島|中之島|淀屋橋|本町|阿倍野|住吉|吹田|豊中|枚方|寝屋川|八尾|東大阪|岸和田|姫路|尼崎|西ノ宮|栗東|草津|大津|宇治|伏見|嵐山|長岡京|向日|高槻|池田|箕面|門真|守口|大東|松原|羽曳野|藤井寺|富田林|泉佐野|貝塚|和泉|高石|阪南|摂津|交野|四條畷")

results = []
for r in allm:
    cands = saved_by_norm.get(r["norm"], [])
    entry = dict(r)
    if len(cands) == 1:
        entry["status"] = "exact1"
        entry["saved"] = cands
    elif len(cands) > 1:
        entry["status"] = "exact_multi"
        entry["saved"] = cands
    else:
        # near matches: containment or small edit distance
        near = []
        for s in saved:
            sn = s["norm"]
            if not sn or not r["norm"]:
                continue
            if (sn in r["norm"] or r["norm"] in sn) and abs(len(sn) - len(r["norm"])) <= 8:
                near.append((0, s))
            elif abs(len(sn) - len(r["norm"])) <= 2 and edit_dist(sn, r["norm"], 2) <= 2:
                near.append((edit_dist(sn, r["norm"], 2), s))
        near.sort(key=lambda t: t[0])
        entry["status"] = "near" if near else "new"
        entry["saved"] = [s for _, s in near[:4]]
    results.append(entry)

from collections import Counter
print(Counter(e["status"] for e in results))

# dump review table
with open(BASE / "match-review.tsv", "w", encoding="utf-8") as fh:
    for e in results:
        sv = " ;; ".join(f"No.{s['no']}({s['section']}) {s['name']} ― {s['stations']}／{s['genre']}" for s in e["saved"])
        fh.write(f"{e['status']}\t{e['city']}\t{e['kubun']}\t{e['name']}\t{e['area']}\t{e['genre']}\t{sv}\n")
print("wrote match-review.tsv")
json.dump(results, open(BASE / "match-results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
