#!/usr/bin/env python3
"""再開収集分（2026-10-28夜）の突合スクリプト。
対象 = 今回新規収集した raw ファイルに現れ、既存 raw ファイル群のどこにも現れない店舗。
既知 = saved-list.md + 最新版raw全件 + 全プールファイル（match-archive.py の流儀）。
結果は標準出力と match-resume-result.json に出す。
"""
import glob
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

BASE = os.path.expanduser("~/workspace/tabelog-to-google-maps")
RAW_DIR = os.path.join(BASE, "hyakumeiten-raw")
SAVED = os.path.join(BASE, "saved-list.md")

NEW_FILES = [
    "raw-yoshoku-2020.md", "raw-yoshoku-2022.md", "raw-yoshoku-2023.md",
    "raw-udon-2017.md", "raw-udon-2018.md", "raw-udon-2019.md",
    "raw-udon-2020.md", "raw-udon-2022.md",
    "raw-yakiniku-2018.md", "raw-yakiniku-2019.md", "raw-yakiniku-2020.md",
    "raw-yakiniku-2021.md", "raw-yakiniku-2022.md", "raw-yakiniku-2023.md",
    "raw-yakiniku-2024.md",
    "raw-ramen-2020.md", "raw-ramen-2021.md", "raw-ramen-2022.md",
    "raw-ramen-2023.md", "raw-ramen-2024.md",
]

POOL_MD = [
    "award2026.md", "michelin-tokyo2026.md", "michelin-kyoto-osaka2026.md",
    "hyakumeiten-2026-new.md", "hyakumeiten-older-new.md",
    "hyakumeiten-archive-new.md",
    "gaultmillau.md", "destination-oad.md",
    "award-archive-new.md", "award-archive-silver-bronze-new.md",
    "try-ramen.md", "laliste-50best.md", "michelin-archive-new.md",
]


def normalize(name):
    s = unicodedata.normalize("NFKC", name)
    s = s.lower()
    s = re.sub(r"[\s　・･\-‐−–—―'’‘\"“”()（）\[\]【】「」&＆/]", "", s)
    return s


def load_saved():
    names = {}
    pat = re.compile(r"^\d+\.\s+(.+?)\s+―")
    with open(SAVED, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.strip())
            if m:
                nm = m.group(1).strip()
                names.setdefault(normalize(nm), nm)
    return names


def parse_raw_stores(path):
    genre = ""
    stores = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if ln.startswith("# ジャンル:"):
                genre = ln.split(":", 1)[1].strip()
            elif ln.startswith("#"):
                continue
            elif "｜" in ln:
                nm, area = ln.split("｜", 1)
                stores.append((nm.strip(), area.strip()))
    gm = re.match(r"^(.*?)\s*百名店\s*\d{4}$", genre)
    genre_name = gm.group(1) if gm else genre
    return genre_name, stores


def load_pool_md():
    names = {}
    for fname in POOL_MD:
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            print("プール無し: " + fname)
            continue
        cnt = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.startswith("- ") and "｜" in line:
                    nm = line[2:].split("｜", 1)[0].strip()
                    nm = re.sub(r"（[^）]*）$", "", nm).strip()
                    nm = re.sub(r"\([^)]*\)$", "", nm).strip()
                    nm = re.sub(r"【[^】]*】$", "", nm).strip()
                    nm = re.sub(r"（選出:.*$", "", nm).strip()
                    if nm and "：" not in nm and len(nm) <= 40:
                        names.setdefault(normalize(nm), nm)
                        cnt += 1
        print("プール {}: {}件".format(fname, cnt))
    return names


def main():
    saved_norm = load_saved()
    print("saved-list: {}件".format(len(saved_norm)))

    existing_norm = {}
    new_set = set(NEW_FILES)
    all_raw = sorted(glob.glob(os.path.join(RAW_DIR, "raw-*.md")))
    for path in all_raw:
        if os.path.basename(path) in new_set:
            continue
        _, stores = parse_raw_stores(path)
        for nm, _a in stores:
            existing_norm.setdefault(normalize(nm), nm)
    print("既存raw店名（ユニーク正規化）: {}件 / ファイル {}件".format(len(existing_norm), len(all_raw) - len(NEW_FILES)))

    pool_norm = load_pool_md()
    print("プールMD合計（ユニーク正規化）: {}件".format(len(pool_norm)))

    known = dict(existing_norm)
    for n, d in pool_norm.items():
        known.setdefault(n, d)

    occurrences = defaultdict(list)
    disp_of = {}
    total_new_entries = 0
    for fname in NEW_FILES:
        path = os.path.join(RAW_DIR, fname)
        m = re.match(r"^raw-(.+)-(\d{4})\.md$", fname)
        year = int(m.group(2))
        genre_name, stores = parse_raw_stores(path)
        total_new_entries += len(stores)
        for nm, area in stores:
            n = normalize(nm)
            if n in existing_norm:
                continue
            occurrences[n].append((genre_name, year))
            disp_of.setdefault(n, (nm, area))
    print("新規ファイル延べ: {} / 既存rawに無い候補（ユニーク）: {}".format(total_new_entries, len(occurrences)))

    cand_pool = list(saved_norm.items()) + [(n, d) for n, d in known.items() if n not in saved_norm]
    buckets = defaultdict(list)
    for nrm, dsp in cand_pool:
        if len(nrm) >= 3:
            buckets[nrm[0]].append((nrm, dsp))

    known_saved, known_pool, check, new = [], [], [], []
    for n, occ in occurrences.items():
        disp, area = disp_of[n]
        if n in saved_norm:
            known_saved.append((disp, area, occ))
            continue
        if n in known:
            known_pool.append((disp, area, occ))
            continue
        cands = []
        if len(n) >= 3:
            seen = set()
            for nrm, dsp in buckets.get(n[0], []):
                if (n in nrm or nrm in n) and dsp not in seen:
                    seen.add(dsp)
                    cands.append(dsp)
                if len(cands) >= 3:
                    break
            if not cands:
                for nrm, dsp in cand_pool:
                    if len(nrm) >= 3 and (n in nrm or nrm in n):
                        cands.append(dsp)
                    if len(cands) >= 3:
                        break
        if cands:
            check.append((disp, area, occ, cands))
        else:
            new.append((disp, area, occ))

    def occ_str(occ):
        by_g = defaultdict(list)
        for g, y in occ:
            by_g[g].append(y)
        return "、".join(
            "{} {}".format(g, "/".join(str(y) for y in sorted(set(ys))))
            for g, ys in sorted(by_g.items())
        )

    result = {
        "counts": {
            "new_file_entries": total_new_entries,
            "candidates": len(occurrences),
            "saved": len(known_saved),
            "pool": len(known_pool),
            "check": len(check),
            "new": len(new),
        },
        "new": [
            {"name": d, "area": a, "occ": occ_str(o)} for d, a, o in sorted(new)
        ],
        "check": [
            {"name": d, "area": a, "occ": occ_str(o), "cands": c} for d, a, o, c in sorted(check)
        ],
    }
    out_json = os.path.join(RAW_DIR, "match-resume-result.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    by_genre = defaultdict(int)
    for d, a, o in new:
        rep = max(o, key=lambda gy: gy[1])[0]
        by_genre[rep] += 1
    print("分類: 保存一致{} プール一致{} 要確認{} 真の増分{}".format(len(known_saved), len(known_pool), len(check), len(new)))
    print("増分ジャンル内訳: {}".format(dict(sorted(by_genre.items()))))
    print("結果JSON: {}".format(out_json))
    return 0


if __name__ == "__main__":
    sys.exit(main())
