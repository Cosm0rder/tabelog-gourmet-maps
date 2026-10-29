#!/usr/bin/env python3
"""百名店2026 rawリストと saved-list.md の店名突合スクリプト。
使い方: python3 match.py  -> hyakumeiten-2026-new.md を生成し、集計を標準出力へ。
"""
import glob
import os
import re
import sys
import unicodedata

BASE = os.path.expanduser("~/workspace/tabelog-to-google-maps")
RAW_DIR = os.path.join(BASE, "hyakumeiten-raw")
SAVED = os.path.join(BASE, "saved-list.md")
OUT = os.path.join(BASE, "hyakumeiten-2026-new.md")


def normalize(name: str) -> str:
    s = unicodedata.normalize("NFKC", name)
    s = s.lower()
    s = re.sub(r"[\s　・･\-‐−–—―'’‘\"“”()（）\[\]【】「」&＆/]", "", s)
    return s


def load_saved():
    names = []
    pat = re.compile(r"^\d+\.\s+(.+?)\s+―")
    with open(SAVED, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.strip())
            if m:
                names.append((m.group(1).strip(), normalize(m.group(1))))
    return names


def main():
    saved = load_saved()
    saved_norm = {}
    for disp, norm in saved:
        saved_norm.setdefault(norm, disp)
    print(f"saved-list 解析: {len(saved)}件")

    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, "raw-*.md")))
    summary = []
    sections = []
    tot_stores = tot_exist = tot_new = tot_check = 0

    for path in raw_files:
        with open(path, encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f]
        genre = ""
        urls = []
        stores = []
        for ln in lines:
            if ln.startswith("# ジャンル:"):
                genre = ln.split(":", 1)[1].strip()
            elif ln.startswith("# URL:"):
                urls.append(ln.split(":", 1)[1].strip())
            elif ln.startswith("#"):
                continue
            elif "｜" in ln:
                name, area = ln.split("｜", 1)
                stores.append((name.strip(), area.strip()))
        if not genre:
            genre = os.path.basename(path)
        exist, new, check = [], [], []
        for name, area in stores:
            n = normalize(name)
            if n in saved_norm:
                exist.append((name, area))
                continue
            cands = []
            if len(n) >= 3:
                for sdisp, snorm in saved:
                    if len(snorm) >= 3 and (n in snorm or snorm in n):
                        cands.append(sdisp)
            if cands:
                check.append((name, area, cands[:3]))
            else:
                new.append((name, area))
        tot_stores += len(stores)
        tot_exist += len(exist)
        tot_new += len(new)
        tot_check += len(check)
        summary.append((genre, len(stores), len(exist), len(new), len(check)))
        sec = [f"## {genre}（収集 {len(stores)}店 / 既存 {len(exist)} / 新規 {len(new)} / 要確認 {len(check)}）", ""]
        if urls:
            sec.append("出典: " + " / ".join(urls))
            sec.append("")
        sec.append("### 新規（保存リストに無い）")
        for name, area in new:
            sec.append(f"- {name}｜{area}")
        sec.append("")
        sec.append("### 要確認（表記ゆれの可能性）")
        for name, area, cands in check:
            sec.append(f"- {name}｜{area} → 候補: {' / '.join(cands)}")
        sec.append("")
        sections.append("\n".join(sec))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# 食べログ百名店 2026年版 新規店舗（保存リスト1,429店との突合結果）\n\n")
        f.write("照合方法: 店名を正規化（NFKC・スペース/中黒/記号除去）して完全一致=既存、包含関係あり=要確認、それ以外=新規。\n\n")
        f.write("## 集計\n\n| ジャンル | 収集 | 既存 | 新規 | 要確認 |\n|---|---|---|---|---|\n")
        for g, t, e, n, c in summary:
            f.write(f"| {g} | {t} | {e} | {n} | {c} |\n")
        f.write(f"| **合計** | **{tot_stores}** | **{tot_exist}** | **{tot_new}** | **{tot_check}** |\n\n")
        f.write("\n".join(sections))
    print(f"合計: 収集{tot_stores} 既存{tot_exist} 新規{tot_new} 要確認{tot_check}")
    for g, t, e, n, c in summary:
        print(f"  {g}: 収集{t} 既存{e} 新規{n} 要確認{c}")
    print(f"出力: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
