#!/usr/bin/env python3
"""Final classification with manual overrides + eyeball lists."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from prep_match import norm

BASE = Path.home() / "workspace/tabelog-to-google-maps"
prep = json.loads((BASE / "match-prep.json").read_text(encoding="utf-8"))
saved = prep["saved"]
results = json.loads((BASE / "match-results.json").read_text(encoding="utf-8"))
saved_by_key = {(s["no"], s["section"]): s for s in saved}

# ---- manual overrides: michelin name -> (status, saved key or None, note) ----
OVR = {
    # 表記ゆれ (same store, different notation)
    "Hajime（ハジメ）": ("hyoki", (1191, "main"), "保存側はカタカナのみ表記「ハジメ」"),
    "ラ・シーム": ("hyoki", (1069, "main"), "保存側は欧文表記「La Cime」"),
    "広東旬菜 一僖": ("hyoki", (1245, "main"), "保存側は短縮表記「一僖」（祇園四条／中華料理で一致）"),
    "北新地 福多亭": ("hyoki", (1080, "main"), "保存側は「北新地 福多亭 The Ukai」"),
    # 要確認 (similar name in saved, likely different/related store)
    "瓢亭": ("confirm", (800, "main"), "保存側は東京・日比谷の支店「南禅寺 瓢亭 日比谷店」。京都本店とは別店舗"),
    "菊乃井 露庵": ("confirm", (1201, "main"), "保存側は「菊乃井 本店」（東山区）。露庵は下京区の別店舗（支店）"),
    "菊乃井 鮨 青": ("confirm", (1201, "main"), "保存側は「菊乃井 本店」。鮨 青は菊乃井の鮨カウンターで別店舗扱い"),
    "東山 緒方": ("confirm", (1237, "main"), "保存側は下京区の「緒方」（2つ星）。東山 緒方は左京区の別店舗（2026新規）"),
    "呑小路 やま岸": ("confirm", (1240, "main"), "保存側は「富小路 やま岸」（同グループの日本料理店）および東京の「銀座呑小路やま岸」。呑小路 やま岸（居酒屋）自体は未保存"),
    "弧柳 継心": ("confirm", (1079, "main"), "保存側は「弧柳」本体。継心はその姉妹店で別店舗"),
    "空心 伽藍堂": ("confirm", (1228, "main"), "保存側は「空心」本体。2026版では伽藍堂のみ掲載（空心本体は未掲載）の公算。別館扱いのため要確認"),
    "祇園 にしかわ": ("confirm", (1238, "main"), "保存側の「祇園 にし」とは別店の公算大（にしかわが正式名）"),
}

final = []
for e in results:
    name = e["name"]
    if name in OVR:
        st, key, note = OVR[name]
        sv = [saved_by_key[key]] if key else []
        final.append({**e, "final": st, "saved_final": sv, "note": note})
    elif e["status"] == "exact1":
        final.append({**e, "final": "exact", "saved_final": e["saved"], "note": ""})
    else:
        final.append({**e, "final": "new", "saved_final": [], "note": ""})

from collections import Counter
print(Counter(f["final"] for f in final))
print(Counter((f["kubun"], f["final"]) for f in final))
json.dump(final, open(BASE / "match-final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# eyeball: new names compact
print("\n== NEW names ==")
for f in final:
    if f["final"] == "new":
        print(f"{f['city']}|{f['kubun']}|{f['name']}|{f['area']}|{f['genre']}")

# eyeball: unmatched Kansai saved (strict filter)
used = {(s["no"], s["section"]) for f in final for s in f["saved_final"]}
STRICT = re.compile(r"祇園四条|京都河原町|北新地|西梅田|東梅田|大阪梅田|心斎橋|祇園|烏丸|三宮|芦屋|西宮|吹田|茨木|豊中|嵐山|出町柳|元田中|北大路|二条城|丸太町（京都市営）|京都市営|阪神）|阪急）|天王寺|大阪阿部野橋|難波（南海）|大津|京阪")
print("\n== unmatched Kansai saved (strict) ==")
for s in saved:
    if (s["no"], s["section"]) not in used and STRICT.search(s["stations"]):
        print(f"No.{s['no']}({s['section']}) {s['name']} ― {s['stations']}／{s['genre']}")
