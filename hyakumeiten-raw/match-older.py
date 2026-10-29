#!/usr/bin/env python3
"""百名店 2025/2024/2022年版 rawリストと saved-list.md の店名突合スクリプト。
使い方: python3 match-older.py -> hyakumeiten-older-new.md を生成し、集計を標準出力へ。
突合方法は2026年版（match.py）と同一：正規化して完全一致=既存、包含関係=要確認、それ以外=新規。
加えて、2026年版の新規2637店（hyakumeiten-2026-new.md）と店名が重なる新規にはフラグを付ける。
"""
import os
import re
import sys
import unicodedata

BASE = os.path.expanduser("~/workspace/tabelog-to-google-maps")
RAW_DIR = os.path.join(BASE, "hyakumeiten-raw")
SAVED = os.path.join(BASE, "saved-list.md")
NEW2026 = os.path.join(BASE, "hyakumeiten-2026-new.md")
OUT = os.path.join(BASE, "hyakumeiten-older-new.md")

# 対象rawファイル（2025年版が最新16ジャンル＋2024年版2＋2022年版1＝19ジャンル）
TARGET_FILES = [
    "raw-yakitori.md",    # 焼き鳥 2025
    "raw-toriryori.md",   # 鳥料理 2025
    "raw-tachinomi.md",   # 立ち飲み 2025
    "raw-okonomiyaki.md", # お好み焼き 2025
    "raw-steak.md",       # ステーキ・鉄板焼き 2025
    "raw-soba.md",        # そば 2025
    "raw-cafe.md",        # カフェ 2025
    "raw-yoshoku.md",     # 洋食 2025
    "raw-creative.md",    # 創作料理・イノベーティブ 2025
    "raw-pizza.md",       # ピザ 2025
    "raw-tempura.md",     # 天ぷら 2025
    "raw-ramen.md",       # ラーメン 2025
    "raw-sushi.md",       # 寿司 2025
    "raw-japanese.md",    # 日本料理 2025
    "raw-french.md",      # フレンチ 2025
    "raw-italian.md",     # イタリアン 2025
    "raw-gyoza.md",       # 餃子 2024
    "raw-udon.md",        # うどん 2024
    "raw-bar.md",         # バー 2022
]


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


def load_2026_new():
    """hyakumeiten-2026-new.md の「新規」セクションの店名（正規化済み）集合を返す。"""
    names = {}
    if not os.path.exists(NEW2026):
        return names
    in_new = False
    with open(NEW2026, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("### 新規"):
                in_new = True
                continue
            if line.startswith("###") or line.startswith("## "):
                in_new = False
                continue
            if in_new and line.startswith("- ") and "｜" in line:
                body = line[2:]
                nm, area = body.split("｜", 1)
                names.setdefault(normalize(nm.strip()), (nm.strip(), area.strip()))
    return names


def main():
    saved = load_saved()
    saved_norm = {}
    for disp, norm in saved:
        saved_norm.setdefault(norm, disp)
    print(f"saved-list 解析: {len(saved)}件")
    new2026 = load_2026_new()
    print(f"2026年版 新規リスト解析: {len(new2026)}件（ユニーク正規化名）")

    summary = []
    sections = []
    tot_stores = tot_exist = tot_new = tot_check = tot_overlap = 0
    missing_files = []

    for fname in TARGET_FILES:
        path = os.path.join(RAW_DIR, fname)
        if not os.path.exists(path):
            missing_files.append(fname)
            continue
        with open(path, encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f]
        genre = ""
        urls = []
        notes = []
        stores = []
        for ln in lines:
            if ln.startswith("# ジャンル:"):
                genre = ln.split(":", 1)[1].strip()
            elif ln.startswith("# URL:"):
                urls.append(ln.split(":", 1)[1].strip())
            elif ln.startswith("# 注意"):
                notes.append(ln.lstrip("# ").strip())
            elif ln.startswith("#"):
                continue
            elif "｜" in ln:
                name, area = ln.split("｜", 1)
                stores.append((name.strip(), area.strip()))
        if not genre:
            genre = fname
        exist, new, check = [], [], []
        overlap_count = 0
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
                ov = n in new2026
                if ov:
                    overlap_count += 1
                new.append((name, area, ov))
        tot_stores += len(stores)
        tot_exist += len(exist)
        tot_new += len(new)
        tot_check += len(check)
        tot_overlap += overlap_count
        summary.append((genre, len(stores), len(exist), len(new), len(check), overlap_count))
        sec = [f"## {genre}（収集 {len(stores)}店 / 既存 {len(exist)} / 新規 {len(new)} / 要確認 {len(check)} / 2026新規と重複 {overlap_count}）", ""]
        if urls:
            sec.append("出典: " + " / ".join(urls))
            sec.append("")
        for nt in notes:
            sec.append(f"注意: {nt}")
            sec.append("")
        sec.append("### 新規（保存リストに無い）")
        for name, area, ov in new:
            flag = " ※2026年版新規と重複" if ov else ""
            sec.append(f"- {name}｜{area}{flag}")
        sec.append("")
        sec.append("### 要確認（表記ゆれの可能性）")
        for name, area, cands in check:
            sec.append(f"- {name}｜{area} → 候補: {' / '.join(cands)}")
        sec.append("")
        sections.append("\n".join(sec))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# 食べログ百名店 2025・2024・2022年版 新規店舗（保存リスト1,429店との突合結果）\n\n")
        f.write("対象：2025年版が最新の16ジャンル＋2024年版が最新の2ジャンル（餃子・うどん）＋2022年版が最新の1ジャンル（バー）＝19ジャンル。\n\n")
        f.write("照合方法: 店名を正規化（NFKC・スペース/中黒/記号除去）して完全一致=既存、包含関係あり=要確認、それ以外=新規。2026年版の突合（match.py）と同一方法。\n")
        f.write("「※2026年版新規と重複」は、hyakumeiten-2026-new.md の新規2,637店と正規化店名が一致したもの（同名異店の可能性は残るため、エリアも併記）。\n\n")
        f.write("## 集計\n\n| ジャンル | 収集 | 既存 | 新規 | 要確認 | 2026新規と重複 |\n|---|---|---|---|---|---|\n")
        for g, t, e, n, c, o in summary:
            f.write(f"| {g} | {t} | {e} | {n} | {c} | {o} |\n")
        f.write(f"| **合計** | **{tot_stores}** | **{tot_exist}** | **{tot_new}** | **{tot_check}** | **{tot_overlap}** |\n\n")
        if missing_files:
            f.write("未取得のrawファイル: " + ", ".join(missing_files) + "\n\n")
        f.write("\n".join(sections))
    print(f"合計: 収集{tot_stores} 既存{tot_exist} 新規{tot_new} 要確認{tot_check} 2026新規と重複{tot_overlap}")
    for g, t, e, n, c, o in summary:
        print(f"  {g}: 収集{t} 既存{e} 新規{n} 要確認{c} 重複{o}")
    if missing_files:
        print("未取得ファイル:", ", ".join(missing_files))
    print(f"出力: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
