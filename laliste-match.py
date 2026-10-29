#!/usr/bin/env python3
"""La Liste 2026 + World's/Asia's 50 Best の収集店と saved-list.md / 既存4プールの突合。
入力: laliste-collected.tsv (name_jp \t name_en \t city \t source \t detail)
出力: laliste-match-result.json と集計を標準出力へ。
突合方法は既存成果物（award2026.md / hyakumeiten-raw/match.py）と同一:
正規化(NFKC・スペース/中黒/記号除去・異体字統一)して完全一致=既存、
包含・支店サフィックス除去一致・編集距離<=2 = 要確認、それ以外=新規。
収集行は先に店舗単位へ名寄せし（キーは英語名正規化を優先）、店舗ごとに1回だけ分類する。
新規については4プールの新規店名と正規化完全一致で重複フラグを付ける。
"""
import json
import os
import re
import unicodedata
from collections import Counter

BASE = os.path.expanduser("~/workspace/tabelog-to-google-maps")

VARIANTS = str.maketrans({
    "髙": "高", "﨑": "崎", "德": "徳", "廣": "広", "櫻": "桜",
    "龍": "竜", "澤": "沢", "邊": "辺", "齋": "斎", "齊": "斉",
    "嶋": "島", "瀨": "瀬",
})


def normalize(name: str) -> str:
    s = unicodedata.normalize("NFKC", name)
    s = s.translate(VARIANTS)
    s = s.lower()
    s = re.sub(r"[\s　・･\-‐−–—―'’‘\"“”()（）\[\]「」&＆/.,、]", "", s)
    return s


def edit_distance(a: str, b: str) -> int:
    if abs(len(a) - len(b)) > 2:
        return 99
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            cur = dp[j]
            dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + (ca != cb))
            prev = cur
    return dp[len(b)]


SUFFIXES = ["本店", "総本店", "支店", "離れ", "別館", "新館", "本館"]


def strip_suffix(n: str) -> str:
    changed = True
    while changed:
        changed = False
        for suf in SUFFIXES:
            if n.endswith(suf) and len(n) > len(suf) + 1:
                n = n[: -len(suf)]
                changed = True
    return n


def load_saved():
    pat = re.compile(r"^\d+\.\s+(.+?)\s+―")
    names = []
    with open(os.path.join(BASE, "saved-list.md"), encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.strip())
            if m:
                names.append(m.group(1).strip())
    return names


def after_section(fname, startpat):
    names, on = [], False
    with open(os.path.join(BASE, fname), encoding="utf-8") as f:
        for line in f:
            if re.match(startpat, line):
                on = True
                continue
            if on:
                if line.startswith("## ") and not re.match(startpat, line):
                    break
                m = re.match(r"- (.+?)｜", line)
                if m:
                    names.append(m.group(1).strip())
    return names


def hyaku(fname):
    names, on = [], False
    with open(os.path.join(BASE, fname), encoding="utf-8") as f:
        for line in f:
            if line.startswith("### 新規"):
                on = True
                continue
            if (line.startswith("### ") or line.startswith("## ")) and not line.startswith("### 新規"):
                on = False
            if on:
                m = re.match(r"- (.+?)｜", line)
                if m:
                    names.append(m.group(1).strip())
    return names


def load_pools():
    return {
        "アワード2026新規": after_section("award2026.md", r"^## 新規"),
        "ミシュラン東京2026新規": after_section("michelin-tokyo2026.md", r"^## 新規"),
        "百名店2026新規": hyaku("hyakumeiten-2026-new.md"),
        "百名店旧年版新規": hyaku("hyakumeiten-older-new.md"),
    }


def has_jp(s: str) -> bool:
    return any(ord(c) > 0x2FF for c in s)


def main():
    saved = load_saved()
    saved_norm = {}
    for disp in saved:
        saved_norm.setdefault(normalize(disp), []).append(disp)
    pools = load_pools()
    pool_norm = {k: {normalize(n) for n in v} for k, v in pools.items()}
    for k, v in pools.items():
        print(f"pool {k}: {len(v)}")
    print(f"saved parsed: {len(saved)}")

    raw_rows = []
    with open(os.path.join(BASE, "laliste-collected.tsv"), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            while len(parts) < 5:
                parts.append("")
            raw_rows.append({
                "name_jp": parts[0].strip(), "name_en": parts[1].strip(),
                "city": parts[2].strip(), "source": parts[3].strip(),
                "detail": parts[4].strip(),
            })
    print(f"collected rows: {len(raw_rows)}")

    # 店舗単位に名寄せ（キーは英語名正規化を優先、無ければ日本語名正規化）
    def store_key(r):
        return normalize(r["name_en"]) if r["name_en"] else normalize(r["name_jp"])

    grouped = {}
    for r in raw_rows:
        k = store_key(r)
        g = grouped.setdefault(k, {"name_jp": "", "name_en": "", "city": "", "sources": []})
        if not g["name_en"] and r["name_en"]:
            g["name_en"] = r["name_en"]
        if r["name_jp"] and (not g["name_jp"] or (has_jp(r["name_jp"]) and not has_jp(g["name_jp"]))):
            g["name_jp"] = r["name_jp"]
        if r["source"] == "LaListe2026" or not g["city"]:
            g["city"] = r["city"]
        g["sources"].append(f"{r['source']}:{r['detail']}")
    rows = list(grouped.values())
    print(f"unique stores: {len(rows)}")

    results = []
    for r in rows:
        key_name = r["name_jp"] or r["name_en"]
        n = normalize(key_name)
        n_alt = normalize(r["name_en"]) if r["name_en"] else ""
        cls, cand = None, ""
        if n in saved_norm or (n_alt and n_alt in saved_norm):
            cls = "既存"
            cand = (saved_norm.get(n) or saved_norm.get(n_alt))[0]
        else:
            cands = []
            ns = strip_suffix(n)
            for sn, sdisp in saved_norm.items():
                if len(n) >= 3 and len(sn) >= 3 and (n in sn or sn in n):
                    cands.append((sdisp[0], "包含"))
                elif ns == strip_suffix(sn) and ns != n:
                    cands.append((sdisp[0], "接尾辞除去一致"))
                elif len(n) >= 4 and len(sn) >= 4 and edit_distance(n, sn) <= 2:
                    cands.append((sdisp[0], "編集距離<=2"))
            if cands:
                cls, cand = "要確認", "; ".join(f"{c}({w})" for c, w in cands[:3])
            else:
                cls = "新規"
        flags = []
        if cls == "新規":
            for pk, pset in pool_norm.items():
                if n in pset or (n_alt and n_alt in pset):
                    flags.append(pk)
        r2 = dict(r)
        r2.update({"class": cls, "candidate": cand, "pool_flags": flags})
        results.append(r2)

    print(Counter(r["class"] for r in results))
    print("pool overlap counts:", Counter(f for r in results for f in r["pool_flags"]))
    with open(os.path.join(BASE, "laliste-match-result.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
