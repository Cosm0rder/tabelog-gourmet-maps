#!/usr/bin/env python3
"""La Liste 2026 確定113店（laliste-japan113.tsv）と先行突合済み98店の差分を抽出し、
差分店を saved-list.md ＋ 全プールと再突合する。
出力: laliste-rematch-result.json ＋ 標準出力サマリー。
分類基準は laliste-match.py と同一（正規化完全一致=既存、包含/接尾辞除去/編集距離<=2=要確認候補、それ以外=新規）。
プールについては全セクションから店名を抽出し、完全一致=含有フラグ、近接=候補として記録する。
"""
import importlib.util
import json
import os
import re

BASE = os.path.expanduser("~/workspace/tabelog-to-google-maps")
spec = importlib.util.spec_from_file_location("lm", os.path.join(BASE, "laliste-match.py"))
lm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lm)
normalize, edit_distance, strip_suffix = lm.normalize, lm.edit_distance, lm.strip_suffix


def clean_alt(alt: str) -> str:
    alt = re.sub(r"[？?].*$", "", alt)
    return alt.strip(" 、,")


def parse_tsv113():
    rows = []
    with open(os.path.join(BASE, "laliste-japan113.tsv"), encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    for ln in lines[1:]:  # ヘッダ除く
        parts = ln.split("\t")
        name_raw, score, city = parts[0].strip(), parts[1].strip(), parts[2].strip()
        m = re.match(r"^(.*?)[（(](.*)[）)]$", name_raw)
        if m:
            primary, alt = m.group(1).strip(), clean_alt(m.group(2))
        else:
            primary, alt = name_raw, ""
        variants = {normalize(primary)}
        if alt:
            variants.add(normalize(alt))
        variants.add(normalize(name_raw))
        rows.append({"name_raw": name_raw, "primary": primary, "alt": alt,
                     "score": score, "city": city, "variants": sorted(variants)})
    return rows


def extract_pool_names(fname):
    names = []
    path = os.path.join(BASE, fname)
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- "):
                t = s[2:]
                t = re.split(r"[｜→]", t)[0].strip()
                t = re.split(r"[（(]", t)[0].strip()
                t = t.strip("*＊ ").strip()
                if t and len(t) <= 50 and not t.startswith(("対象", "発売", "発行", "出典", "形式")):
                    names.append(t)
            elif s.startswith("|") and "---" not in s:
                cells = [c.strip() for c in s.strip().strip("|").split("|")]
                # destination-oad: | 年 or 順位 | 店名 | ...
                if len(cells) >= 3 and re.fullmatch(r"\d{1,4}", cells[0] or "x"):
                    nm = re.split(r"[（(]", cells[1])[0].strip()
                    if nm and nm != "店名":
                        names.append(nm)
                # michelin-archive 要確認表: | 店名 | エリア | ...
                elif len(cells) >= 4 and cells[0] and cells[0] not in ("店名",) and not cells[0].startswith(("区分", "ソース", "エリア", "年")):
                    names.append(cells[0])
    return names


POOL_FILES = {
    "アワード2026": "award2026.md",
    "アワード過去年GOLD・部門賞": "award-archive-new.md",
    "アワード過去年SILVER/BRONZE": "award-archive-silver-bronze-new.md",
    "ミシュラン東京2026": "michelin-tokyo2026.md",
    "ミシュラン京阪2026": "michelin-kyoto-osaka2026.md",
    "ミシュラン過去年": "michelin-archive-new.md",
    "百名店2026": "hyakumeiten-2026-new.md",
    "百名店旧年版": "hyakumeiten-older-new.md",
    "ゴ・エ・ミヨ2026": "gaultmillau.md",
    "DR/OAD": "destination-oad.md",
    "TRYラーメン": "try-ramen.md",
}


def near_candidates(n, name_map, limit=3):
    """name_map: 正規化名 -> 表示名リスト。包含/接尾辞除去/編集距離<=2 の候補を返す。"""
    cands = []
    ns = strip_suffix(n)
    for sn, disps in name_map.items():
        if len(n) >= 3 and len(sn) >= 3 and (n in sn or sn in n):
            cands.append((disps[0], "包含"))
        elif ns and ns == strip_suffix(sn) and ns != n and ns != sn:
            cands.append((disps[0], "接尾辞除去一致"))
        elif len(n) >= 4 and len(sn) >= 4 and edit_distance(n, sn) <= 2:
            cands.append((disps[0], "編集距離<=2"))
    return cands[:limit]


def main():
    # 先行突合済み98店
    with open(os.path.join(BASE, "laliste-match-result.json"), encoding="utf-8") as f:
        prev = json.load(f)
    prev_keys = {}
    for r in prev:
        for nm in (r.get("name_jp", ""), r.get("name_en", "")):
            if nm:
                prev_keys.setdefault(normalize(nm), r)

    rows113 = parse_tsv113()
    print(f"113 list parsed: {len(rows113)}")

    delta, already = [], []
    for r in rows113:
        hit = None
        for v in r["variants"]:
            if v in prev_keys:
                hit = prev_keys[v]
                break
        if not hit:  # 包含でも確認
            for v in r["variants"]:
                for pk, pr in prev_keys.items():
                    if len(v) >= 4 and len(pk) >= 4 and (v in pk or pk in v):
                        hit = pr
                        break
                if hit:
                    break
        (already.append((r, hit)) if hit else delta.append(r))
    print(f"already processed: {len(already)}, delta: {len(delta)}")
    for r in delta:
        print("  DELTA:", r["name_raw"], r["score"], r["city"])

    # saved
    saved = lm.load_saved()
    saved_map = {}
    for d in saved:
        saved_map.setdefault(normalize(d), []).append(d)
    print(f"saved parsed: {len(saved)}")

    # pools
    pool_maps = {}
    for label, fname in POOL_FILES.items():
        names = extract_pool_names(fname)
        mp = {}
        for d in names:
            mp.setdefault(normalize(d), []).append(d)
        pool_maps[label] = mp
        print(f"pool {label}: extracted {len(names)} names ({len(mp)} unique norm)")

    results = []
    for r in delta:
        variants = r["variants"]
        cls, cand = None, ""
        # saved 完全一致
        for v in variants:
            if v in saved_map:
                cls, cand = "既存", saved_map[v][0]
                break
        pool_hits, pool_near = [], []
        for label, mp in pool_maps.items():
            hitname = None
            for v in variants:
                if v in mp:
                    hitname = mp[v][0]
                    break
            if hitname:
                pool_hits.append(f"{label}:{hitname}")
            else:
                nc = []
                for v in variants:
                    nc += near_candidates(v, mp, limit=2)
                if nc:
                    pool_near.append(f"{label}:" + "; ".join(f"{c}({w})" for c, w in nc[:2]))
        if cls is None:
            cands = []
            for v in variants:
                cands += near_candidates(v, saved_map, limit=3)
            # 重複除去
            seen, uc = set(), []
            for c in cands:
                if c[0] not in seen:
                    seen.add(c[0])
                    uc.append(c)
            if uc:
                cls = "要確認"
                cand = "; ".join(f"{c}({w})" for c, w in uc[:3])
            else:
                cls = "新規"
        results.append({**r, "class": cls, "saved_candidate": cand,
                        "pool_hits": pool_hits, "pool_near": pool_near})
        print(f"[{cls}] {r['name_raw']} | saved候補: {cand} | pools: {pool_hits} | pool近接: {pool_near}")

    with open(os.path.join(BASE, "laliste-rematch-result.json"), "w", encoding="utf-8") as f:
        json.dump({"already_count": len(already), "delta": results}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
