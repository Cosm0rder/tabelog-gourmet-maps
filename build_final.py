#!/usr/bin/env python3
"""Build michelin-kyoto-osaka2026.md with final classification + award overlap."""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).parent))
from prep_match import norm

BASE = Path.home() / "workspace/tabelog-to-google-maps"
prep = json.loads((BASE / "match-prep.json").read_text(encoding="utf-8"))
saved = prep["saved"]
award_new = prep["award_new"]
results = json.loads((BASE / "match-results.json").read_text(encoding="utf-8"))
saved_by_key = {(s["no"], s["section"]): s for s in saved}
award_by_norm = {}
for a in award_new:
    award_by_norm.setdefault(a["norm"], []).append(a)

OVR = {
    "Hajime（ハジメ）": ("hyoki", (1191, "main"), "保存側はカタカナのみの表記「ハジメ」"),
    "ラ・シーム": ("hyoki", (1069, "main"), "保存側は欧文表記「La Cime」"),
    "広東旬菜 一僖": ("hyoki", (1245, "main"), "保存側は短縮表記「一僖」。祇園四条／中華料理で一致"),
    "北新地 福多亭": ("hyoki", (1080, "main"), "保存側は「北新地 福多亭 The Ukai」"),
    "レ・スヴニール": ("hyoki", (1128, "main"), "保存側は欧文表記「LES SOUVENIRS」（北新地／フレンチ）"),
    "瓢亭": ("confirm", (800, "main"), "保存側は東京・日比谷の支店「南禅寺 瓢亭 日比谷店」。京都本店とは別店舗のため要確認"),
    "菊乃井 露庵": ("confirm", (1201, "main"), "保存側は東山区の「菊乃井 本店」。露庵は下京区の別店舗（カジュアルな支店）"),
    "菊乃井 鮨 青": ("confirm", (1201, "main"), "保存側は「菊乃井 本店」。鮨 青は菊乃井の鮨専門カウンターで、ミシュラン上は別店舗として掲載"),
    "菊乃井 無碍山房": ("confirm", (1201, "main"), "保存側は「菊乃井 本店」。無碍山房は菊乃井の喫茶・サロン業態で別店舗"),
    "高台寺 和久傳": ("confirm", (1242, "main"), "保存側は中京区の「室町 和久傳」（1つ星で別途一致）。高台寺 和久傳は東山区の別店舗"),
    "柏屋 大阪北新地": ("confirm", (1172, "main"), "保存側は「柏屋 大阪千里山」（3つ星で別途一致）。北新地は別店舗（支店）"),
    "東山 緒方": ("confirm", (1237, "main"), "保存側は下京区の「緒方」（2つ星で別途一致）。東山 緒方は左京区・眞松庵内の別店舗（2026年新規掲載）"),
    "呑小路 やま岸": ("confirm", (1240, "main"), "保存側は同グループの「富小路 やま岸」（日本料理）で、居酒屋業態の呑小路 やま岸自体は未保存。東京には「銀座呑小路やま岸」（保存No.757）もある"),
    "弧柳 継心": ("confirm", (1079, "main"), "保存側は「弧柳」本体（2つ星で別途一致）。継心はその姉妹店で別店舗"),
    "空心 伽藍堂": ("confirm", (1228, "main"), "保存側は「空心」本体。2026年版では伽藍堂のみが掲載され空心本体は未掲載の公算。別館業態のため要確認とした"),
    "祇園 にしかわ": ("confirm", (1238, "main"), "保存側の「祇園 にし」とは別店の公算大（正式名は祇園 にしかわ）"),
}
# award notation pairs (michelin name -> award name) judged identical by hand
AWARD_PAIRS = {
    "アドック": "ad hoc",
    "京、静華": "京 静華",
    "杦 SEN": "杦",
    "京星": "天ぷら 京星",
    "研野": "日本料理 研野",
    "割烹 八寸": "八寸",
    "チェンチ": "cenci",
    "ミドル": "middle",
    "ラディーチェ": "RADICE",
    "徳ハ本也": "徳ㇵ本也",
}

final = []
for e in results:
    if e["name"] in OVR:
        st, key, note = OVR[e["name"]]
        final.append({**e, "final": st, "saved_final": [saved_by_key[key]], "note": note})
    elif e["status"] == "exact1":
        final.append({**e, "final": "exact", "saved_final": e["saved"], "note": ""})
    else:
        final.append({**e, "final": "new", "saved_final": [], "note": ""})

# ---- award overlap for new stores ----
award_overlap = {}
for f in final:
    if f["final"] != "new":
        continue
    hits = award_by_norm.get(f["norm"], [])
    if f["name"] in AWARD_PAIRS:
        hits = [a for a in award_new if a["name"] == AWARD_PAIRS[f["name"]]] + hits
    if hits:
        award_overlap[f["name"]] = hits

KUBUN = ["3つ星", "2つ星", "1つ星", "ビブグルマン", "セレクテッド"]
STAT = {"exact": "既存", "hyoki": "既存・表記ゆれ", "confirm": "要確認", "new": "新規"}

cnt = Counter((f["kubun"], f["final"]) for f in final)
tot = Counter(f["kubun"] for f in final)
city_cnt = Counter((f["city"], f["final"]) for f in final)
print("kubun totals:", dict(tot), "sum", sum(tot.values()))
print("status totals:", Counter(f["final"] for f in final))
print("city:", dict(city_cnt))
print("award overlap:", len(award_overlap))
for k, v in award_overlap.items():
    print("  ", k, "->", [(a["name"], a["pref"], a["award"]) for a in v])
json.dump({"final": final, "award_overlap": {k: v for k, v in award_overlap.items()}},
          open(BASE / "match-final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
