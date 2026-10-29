# -*- coding: utf-8 -*-
"""ミシュラン過去年アーカイブ拡張（第2段階）突合: 東京2022／京都2024／大阪2024／京都2023星"""
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

def city_of_area(area):
    if area.startswith("京都"):
        return "京都"
    if area.startswith("大阪"):
        return "大阪"
    return "東京"

refs = defaultdict(list)
def add_ref(display, source, city=None):
    n = normalize(display)
    if n:
        refs[n].append((display, source, city))
    m = re.match(r"^(.*?)（(.+?)）(.*)$", display)
    if m:
        add_ref(m.group(2), source, city)
        add_ref((m.group(1) + m.group(3)).strip(), source, city)

saved_count = 0
for line in (BASE / "saved-list.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"^\d+\.\s+(.+?)\s+―\s+", line)
    if m:
        add_ref(m.group(1).strip(), "保存リスト", None); saved_count += 1

POOL_FILES = ["michelin-archive-new.md", "michelin-tokyo2026.md", "michelin-kyoto-osaka2026.md",
              "award2026.md", "hyakumeiten-2026-new.md", "hyakumeiten-older-new.md",
              "hyakumeiten-archive-new.md", "gaultmillau.md", "destination-oad.md",
              "award-archive-new.md", "award-archive-silver-bronze-new.md",
              "try-ramen.md", "laliste-50best.md"]
pool_counts = {}
for pf in POOL_FILES:
    c = 0
    for line in (BASE / pf).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- ") and "｜" in line:
            parts = line[2:].split("｜")
            name = re.sub(r"[【\[][^】\]]*[】\]]\s*$", "", parts[0].strip()).strip()
            city = city_of_area(parts[1].strip()) if len(parts) > 1 else None
            if name:
                add_ref(name, pf, city); c += 1
    pool_counts[pf] = c

for rf, city in [("michelin-raw-kyoto.txt", "京都"), ("michelin-raw-osaka.txt", "大阪")]:
    for line in (BASE / rf).read_text(encoding="utf-8").splitlines():
        parts = line.strip().split("|")
        if len(parts) == 4:
            add_ref(parts[0].strip(), rf, city)

ascii_refs = {}
for n, v in refs.items():
    if n.isascii():
        ascii_refs[n] = v[0]

TARGET_FILES = [
    ("michelin-raw-tokyo2022.txt", "東京", 2022),
    ("michelin-raw-kyoto2024.txt", "京都", 2024),
    ("michelin-raw-osaka2024.txt", "大阪", 2024),
    ("michelin-raw-kyoto2023.txt", "京都", 2023),
]
targets = {}
total_entries = 0
for tf, city, year in TARGET_FILES:
    for line in (BASE / tf).read_text(encoding="utf-8").splitlines():
        parts = line.strip().split("|")
        if len(parts) != 4:
            continue
        total_entries += 1
        name, rank, area, genre = [p.strip() for p in parts]
        key = (normalize(name), city)
        if key not in targets:
            targets[key] = {"name": name, "city": city, "area": area, "genre": genre, "history": []}
        targets[key]["history"].append(str(year) + " " + rank)

print("saved-list parsed:", saved_count)
print("pool bullet entries:", pool_counts)
print("reference unique normalized names:", len(refs))
print("target entries:", total_entries, "/ unique (name,city):", len(targets))

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

def city_ok(ref_cities, city):
    return (None in ref_cities) or (city in ref_cities)

existing, review, new = [], [], []
for (norm, city), rec in sorted(targets.items()):
    name = rec["name"]
    hit, why = None, ""
    if norm in refs:
        cities = {c for _, _, c in refs[norm]}
        if city_ok(cities, city):
            hit = refs[norm][0]; why = "完全一致"
        else:
            review.append((rec, refs[norm][0], "他都市で同名あり")); continue
    if not hit and is_kana_only(name):
        r = romanize(unicodedata.normalize("NFKC", name).replace(" ", "").replace("　", ""))
        if r and r in ascii_refs:
            hit = ascii_refs[r]; why = "ローマ字一致"
    if hit:
        existing.append((rec, hit, why)); continue
    cands = []
    for v in strip_variants(norm):
        if v in refs:
            cands.append((refs[v][0], "接頭辞/接尾辞除去一致")); break
    if not cands:
        for rn, rv in refs.items():
            if norm != rn and (norm in rn or rn in norm) and ((len(norm) >= 3 and len(rn) >= 3) or (min(len(norm), len(rn)) == 2 and abs(len(norm) - len(rn)) <= 3)):
                cands.append((rv[0], "包含")); break
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
            cands.append((refs[rn][0], "編集距離" + str(d)))
    if cands:
        review.append((rec, cands[0][0], cands[0][1]))
    else:
        new.append(rec)

print("既存:", len(existing), "/ 要確認:", len(review), "/ 増分新規:", len(new))

out = {
    "existing": [(r["name"], r["city"], r["area"], r["genre"], r["history"], h[0], h[1], w) for r, h, w in existing],
    "review": [(r["name"], r["city"], r["area"], r["genre"], r["history"], h[0], h[1], w) for r, h, w in review],
    "new": [(r["name"], r["city"], r["area"], r["genre"], r["history"]) for r in new],
}
(BASE / "michelin-archive2-match.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote michelin-archive2-match.json")
