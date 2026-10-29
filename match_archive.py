# -*- coding: utf-8 -*-
"""Tabelog Award 過去年 SILVER/BRONZE アーカイブ × 保存リスト＋全プール 突合"""
import re, unicodedata, json
from pathlib import Path
from collections import defaultdict

BASE = Path.home() / "workspace/tabelog-to-google-maps"

VARIANTS = str.maketrans({
    "髙": "高", "﨑": "崎", "𠮷": "吉", "㐂": "喜", "澤": "沢", "櫻": "桜", "龍": "竜", "廣": "広",
    "榮": "栄", "齋": "斎", "邊": "辺", "國": "国", "會": "会", "圓": "円", "龜": "亀",
    "嶋": "島", "舘": "館", "壽": "寿", "萬": "万", "與": "与", "來": "来", "條": "条",
    "應": "応", "營": "営", "關": "関", "縣": "県", "區": "区", "麵": "麺",
    "鹽": "塩", "螢": "蛍", "蟲": "虫", "絲": "糸", "戀": "恋", "獨": "独", "獻": "献", "顯": "顕",
    "佛": "仏", "瀧": "滝", "遙": "遥", "頰": "頬", "惠": "恵", "渚": "緒", "靑": "青", "淸": "清",
    "郞": "郎", "亰": "京", "凜": "凛", "濱": "浜", "邉": "辺", "塚": "塚",
})
REMOVE_CHARS = set(" ・･·‐-―ー.,、。，．・:：;；/／\\|｜()（）[]［］【】「」『』\"'’‘“”!?！？~〜～*＊&＆+＋=＝_＿<>＜＞#＃@＠%％¥￥$＄")

def normalize(name):
    s = unicodedata.normalize("NFKC", name)
    s = s.translate(VARIANTS)
    s = s.lower()
    s = "".join(ch for ch in s if ch not in REMOVE_CHARS and not ch.isspace())
    return s

KANA_ROMAJI = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o", "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so", "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no", "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo", "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro", "わ": "wa", "を": "wo", "ん": "n",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go", "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do", "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo", "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
    "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho", "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
    "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo", "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
    "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo", "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
    "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
    "ー": "", "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o", "っ": "", "ゃ": "ya", "ゅ": "yu", "ょ": "yo",
}

def romanize(s):
    s = "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)
    out, i = [], 0
    while i < len(s):
        if i + 1 < len(s) and s[i:i + 2] in KANA_ROMAJI:
            out.append(KANA_ROMAJI[s[i:i + 2]]); i += 2
        elif s[i] in KANA_ROMAJI:
            out.append(KANA_ROMAJI[s[i]]); i += 1
        else:
            return ""
    return "".join(out)

def is_kana_only(raw):
    s = unicodedata.normalize("NFKC", raw)
    return bool(s) and all(("ぁ" <= c <= "ゖ" or "ァ" <= c <= "ヶ" or c in "ー・ 　") for c in s)

refs = {}
def add_ref(display, source):
    n = normalize(display)
    if n and n not in refs:
        refs[n] = (display, source)
    m = re.match(r"^(.*?)（(.+?)）(.*)$", display)
    if m:
        add_ref(m.group(2), source)
        add_ref((m.group(1) + m.group(3)).strip(), source)

saved_count = 0
for line in (BASE / "saved-list.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"^\d+\.\s+(.+?)\s+―\s+", line)
    if m:
        add_ref(m.group(1).strip(), "保存リスト"); saved_count += 1

POOL_FILES = ["award2026.md", "michelin-tokyo2026.md", "michelin-kyoto-osaka2026.md",
              "hyakumeiten-2026-new.md", "hyakumeiten-older-new.md", "destination-oad.md",
              "gaultmillau.md", "award-archive-new.md"]
pool_counts = {}
for pf in POOL_FILES:
    c = 0
    for line in (BASE / pf).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- ") and "｜" in line:
            name = line[2:].split("｜")[0].strip()
            name = re.sub(r"[【\[][^】\]]*[】\]]\s*$", "", name).strip()
            if name:
                add_ref(name, pf); c += 1
    pool_counts[pf] = c

ascii_refs = {}
for n, v in list(refs.items()):
    if n.isascii():
        ascii_refs[n] = v

archive = {}
def add_archive(name, genre, pref, year, rank):
    key = (normalize(name), pref)
    if key not in archive:
        archive[key] = {"name": name, "genre": genre, "pref": pref, "history": []}
    archive[key]["history"].append(str(year) + " " + rank)

for year in range(2018, 2026):
    for rank in ["silver", "bronze"]:
        p = BASE / ("award-archive-raw-" + str(year) + "-" + rank + ".md")
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split("｜")
            if len(parts) == 3 and not line.startswith(("形式", "#", "出典")):
                add_archive(parts[0].strip(), parts[1].strip(), parts[2].strip(), year, rank.upper())

silver2025_names = []
for line in (BASE / "award-archive-raw-2025-silver.md").read_text(encoding="utf-8").splitlines():
    if "／" in line and not line.startswith("#"):
        silver2025_names = [x.strip() for x in line.split("／") if x.strip()]
for nm in silver2025_names:
    add_archive(nm, "", "", 2025, "SILVER")

print("saved-list parsed:", saved_count)
print("pool bullet entries:", pool_counts)
print("reference unique normalized names:", len(refs))
print("archive unique (name,pref) entries:", len(archive))
print("2025 silver names:", len(silver2025_names))

SUFFIXES = ["総本店", "本店", "支店", "新館", "別館", "別邸", "はなれ", "離れ", "annex", "アネックス"]
GENRE_PREFIXES = ["てんぷら", "天ぷら", "天麩羅", "鮨", "寿司", "寿し", "鮓", "すし", "日本料理", "レストラン", "焼肉", "焼き鳥", "焼鳥", "そば", "蕎麦", "うなぎ", "鰻", "ラーメン", "らーめん", "中華料理", "中国料理", "フレンチ", "イタリアン", "割烹", "料亭", "懐石", "会席", "京料理", "ふぐ", "河豚", "和食", "洋食", "ステーキハウス", "鉄板焼", "寿司処", "鮨処", "すし処", "寿し処", "鮓処"]

def strip_variants(n):
    outs = set()
    for suf in SUFFIXES:
        if n.endswith(suf) and len(n) > len(suf) + 1:
            outs.add(n[:len(n) - len(suf)])
    for pre in GENRE_PREFIXES:
        pn = normalize(pre)
        if n.startswith(pn) and len(n) > len(pn) + 1:
            outs.add(n[len(pn):])
    return outs

def edit_dist(a, b, limit=2):
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        mn = i
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (0 if ca == cb else 1)))
            mn = min(mn, cur[j])
        if mn > limit:
            return limit + 1
        prev = cur
    return prev[-1]

by_len = defaultdict(list)
for n in refs:
    by_len[len(n)].append(n)

existing, review, new = [], [], []
for (norm, pref), rec in sorted(archive.items()):
    name = rec["name"]
    hit = None
    why = ""
    if norm in refs:
        hit = refs[norm]; why = "完全一致"
    if not hit and is_kana_only(name):
        r = romanize(unicodedata.normalize("NFKC", name).replace(" ", "").replace("　", ""))
        if r and r in ascii_refs:
            hit = ascii_refs[r]; why = "ローマ字一致"
    if hit:
        existing.append((rec, hit, why)); continue
    cands = []
    for v in strip_variants(norm):
        if v in refs:
            cands.append((refs[v], "接頭辞/接尾辞除去一致")); break
    if not cands:
        for rn, rv in refs.items():
            if norm != rn and (norm in rn or rn in norm) and ((len(norm) >= 3 and len(rn) >= 3) or (min(len(norm), len(rn)) == 2 and abs(len(norm) - len(rn)) <= 3)):
                cands.append((rv, "包含")); break
    if not cands:
        best = []
        pool = []
        for L in range(max(1, len(norm) - 2), len(norm) + 3):
            pool.extend(by_len.get(L, []))
        for rn in pool:
            if rn[0] != norm[0]:
                continue
            d = edit_dist(norm, rn, 2)
            if d <= 2:
                best.append((d, rn))
        if best:
            best.sort()
            d, rn = best[0]
            cands.append((refs[rn], "編集距離" + str(d)))
    if cands:
        review.append((rec, cands[0][0], cands[0][1]))
    else:
        new.append(rec)

print("既存:", len(existing), "/ 要確認:", len(review), "/ 増分新規:", len(new))
json.dump({"existing": [(r["name"], h[0], h[1], w) for r, h, w in existing],
           "review": [(r["name"], r["genre"], r["pref"], r["history"], h[0], h[1], w) for r, h, w in review],
           "new": [(r["name"], r["genre"], r["pref"], r["history"]) for r in new]},
          open("/tmp/match_result.json", "w"), ensure_ascii=False, indent=1)
print("wrote /tmp/match_result.json")
