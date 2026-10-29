#!/usr/bin/env python3
"""百名店 過去年度アーカイブ（raw-<short>-<year>.md）と既知プール全体の突合スクリプト。
使い方: python3 match-archive.py -> hyakumeiten-archive-new.md を生成し、集計を標準出力へ。

既知プール = saved-list.md
  + 最新版 raw ファイル全件（raw-<short>.md、年度サフィックス無し）
  + award2026.md / michelin-tokyo2026.md / michelin-kyoto-osaka2026.md のリスト記載店名
分類（ユニーク店舗＝正規化店名単位）:
  - 保存リストと完全一致 -> 一致（保存）
  - 既存プールと完全一致 -> 一致（既存プール）
  - 保存/プールのいずれかと包含関係（表記ゆれ候補） -> 要確認
  - それ以外 -> 増分新規（過去年度でのみ選出され、どこにも無い店）
正規化・包含判定は match.py / match-older.py と同一方法。
"""
import glob
import os
import re
import sys
import unicodedata
from collections import defaultdict

BASE = os.path.expanduser("~/workspace/tabelog-to-google-maps")
RAW_DIR = os.path.join(BASE, "hyakumeiten-raw")
SAVED = os.path.join(BASE, "saved-list.md")
OUT = os.path.join(BASE, "hyakumeiten-archive-new.md")
POOL_FILES = ["award2026.md", "michelin-tokyo2026.md", "michelin-kyoto-osaka2026.md"]

ARCHIVE_RE = re.compile(r"^raw-(.+)-(\d{4})\.md$")


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


def parse_raw_stores(path):
    genre = ""
    urls = []
    stores = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if ln.startswith("# ジャンル:"):
                genre = ln.split(":", 1)[1].strip()
            elif ln.startswith("# URL:"):
                urls.append(ln.split(":", 1)[1].strip())
            elif ln.startswith("#"):
                continue
            elif "｜" in ln:
                nm, area = ln.split("｜", 1)
                stores.append((nm.strip(), area.strip()))
    return genre, urls, stores


def load_pool_files():
    names = {}
    for fname in POOL_FILES:
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            continue
        cnt = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.startswith("- ") and "｜" in line:
                    nm = line[2:].split("｜", 1)[0].strip()
                    nm = re.sub(r"【[^】]*】$", "", nm).strip()
                    if nm:
                        names.setdefault(normalize(nm), nm)
                        cnt += 1
        print(f"プール {fname}: {cnt}行から店名を抽出")
    return names


def main():
    saved = load_saved()
    saved_norm = {}
    for disp, norm in saved:
        saved_norm.setdefault(norm, disp)
    print(f"saved-list 解析: {len(saved)}件")

    pool_norm = {}
    latest_files = []
    archive_files = []
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "raw-*.md"))):
        base = os.path.basename(path)
        if ARCHIVE_RE.match(base):
            archive_files.append(path)
        else:
            latest_files.append(path)
    for path in latest_files:
        _, _, stores = parse_raw_stores(path)
        for nm, _area in stores:
            pool_norm.setdefault(normalize(nm), nm)
    print(f"最新版raw: {len(latest_files)}ファイル / プール店名 {len(pool_norm)}件")
    pool_files_names = load_pool_files()
    for n, d in pool_files_names.items():
        pool_norm.setdefault(n, d)
    print(f"プール合計（ユニーク正規化名）: {len(pool_norm)}件")
    print(f"アーカイブ対象ファイル: {len(archive_files)}件")

    table_rows = []
    occurrences = defaultdict(list)
    disp_of = {}
    total_entries = 0
    for path in archive_files:
        base = os.path.basename(path)
        m = ARCHIVE_RE.match(base)
        year = int(m.group(2))
        genre_head, _urls, stores = parse_raw_stores(path)
        genre_label = genre_head if genre_head else base
        gm = re.match(r"^(.*?)\s*百名店\s*\d{4}$", genre_label)
        genre_name = gm.group(1) if gm else genre_label
        table_rows.append((genre_name, year, len(stores), base))
        total_entries += len(stores)
        for nm, area in stores:
            n = normalize(nm)
            occurrences[n].append((genre_name, year))
            disp_of.setdefault(n, (nm, area))
    print(f"アーカイブ延べ店舗数: {total_entries} / ユニーク: {len(occurrences)}")

    known_saved, known_pool, check, new = [], [], [], []
    cand_pool = list(saved_norm.items()) + [(n, d) for n, d in pool_norm.items() if n not in saved_norm]
    buckets = defaultdict(list)
    for nrm, dsp in cand_pool:
        if len(nrm) >= 3:
            buckets[nrm[0]].append((nrm, dsp))

    for n, occ in occurrences.items():
        disp, area = disp_of[n]
        if n in saved_norm:
            known_saved.append((disp, area, occ))
            continue
        if n in pool_norm:
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
            f"{g} {'/'.join(str(y) for y in sorted(set(ys)))}" for g, ys in sorted(by_g.items())
        )

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# 食べログ百名店 過去年度アーカイブ 増分新規店舗（全プール突合結果）\n\n")
        f.write("対象：各ジャンルの最新版より前の年度版（公式サイト award.tabelog.com/hyakumeiten の年度別ページ）。"
                "原データは hyakumeiten-raw/raw-<ジャンル>-<年度>.md。\n\n")
        f.write("照合方法: 店名を正規化（NFKC・スペース/中黒/記号除去）して完全一致=一致、包含関係あり=要確認、それ以外=増分新規。"
                "既存手法（match.py / match-older.py）と同一。\n")
        f.write("既知プール: 保存リスト1,429店 ＋ 最新版百名店raw全件 ＋ The Tabelog Award 2026 ＋ ミシュランガイド東京2026"
                "（＋京都・大阪2026ファイルがあればそれも含む）。\n")
        f.write("「増分新規」は、過去年度でのみ選出されていて、保存リストにも既存プールのどこにも無い店舗。\n\n")

        f.write("## ジャンル×年度 収集表\n\n| ジャンル | 年度 | 収集店数 | ファイル |\n|---|---|---|---|\n")
        for g, y, c, fn in sorted(table_rows, key=lambda r: (r[0], r[1])):
            f.write(f"| {g} | {y} | {c} | {fn} |\n")
        f.write(f"\nジャンル×年度の組み合わせ数: {len(table_rows)} / 延べ収集店舗数: {total_entries} / ユニーク店舗数: {len(occurrences)}\n\n")

        f.write("## 突合集計（ユニーク店舗単位）\n\n| 分類 | 件数 |\n|---|---|\n")
        f.write(f"| 保存リストと一致 | {len(known_saved)} |\n")
        f.write(f"| 既存プールと一致 | {len(known_pool)} |\n")
        f.write(f"| 要確認（表記ゆれ候補） | {len(check)} |\n")
        f.write(f"| **増分新規** | **{len(new)}** |\n\n")

        f.write("## 増分新規（過去年度でのみ選出・どこにも無い店）\n\n")
        by_genre = defaultdict(list)
        for disp, area, occ in new:
            rep = max(occ, key=lambda gy: gy[1])[0]
            by_genre[rep].append((disp, area, occ))
        for g in sorted(by_genre):
            items = sorted(by_genre[g], key=lambda x: x[0])
            f.write(f"### {g}（{len(items)}店）\n\n")
            for disp, area, occ in items:
                f.write(f"- {disp}｜{area}（選出: {occ_str(occ)}）\n")
            f.write("\n")

        f.write("## 要確認（表記ゆれの可能性）\n\n")
        for disp, area, occ, cands in sorted(check, key=lambda x: x[0]):
            f.write(f"- {disp}｜{area}（選出: {occ_str(occ)}） → 候補: {' / '.join(cands)}\n")
        f.write("\n")

    print(f"分類: 保存一致{len(known_saved)} プール一致{len(known_pool)} 要確認{len(check)} 増分新規{len(new)}")
    print(f"ジャンル×年度: {len(table_rows)}組 / 延べ{total_entries}")
    print(f"出力: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
