#!/usr/bin/env python3
"""Compare gm-raw (summary/book compilation) vs gm-official (official site list) per prefecture."""
import json, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent))
from gm_match import norm

BASE = Path.home() / "workspace/tabelog-to-google-maps"
SLUG2PREF = {"hokkaido":"北海道","aomori":"青森県","akita":"秋田県","iwate":"岩手県","miyagi":"宮城県","yamagata":"山形県","fukushima":"福島県","tokyo":"東京都","ibaraki":"茨城県","tochigi":"栃木県","gunma":"群馬県","saitama":"埼玉県","chiba":"千葉県","kanagawa":"神奈川県","yamanashi":"山梨県","nagano":"長野県","niigata":"新潟県","toyama":"富山県","ishikawa":"石川県","fukui":"福井県","shizuoka":"静岡県","aichi":"愛知県","gifu":"岐阜県","mie":"三重県","osaka":"大阪府","kyoto":"京都府","hyogo":"兵庫県","nara":"奈良県","shiga":"滋賀県","wakayama":"和歌山県","okayama":"岡山県","hiroshima":"広島県","yamaguchi":"山口県","shimane":"島根県","tottori":"鳥取県","tokushima":"徳島県","kagawa":"香川県","ehime":"愛媛県","kochi":"高知県","fukuoka":"福岡県","saga":"佐賀県","nagasaki":"長崎県","kumamoto":"熊本県","oita":"大分県","miyazaki":"宮崎県","kagoshima":"鹿児島県","okinawa":"沖縄県"}

official = defaultdict(list)
for line in (BASE/"gm-official.txt").read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    name, pref = line.rsplit("|", 1)
    official[pref].append({"name": name.strip(), "norm": norm(name)})

raw = defaultdict(list)
for slug, pref in SLUG2PREF.items():
    f = BASE/"gm-raw"/f"{slug}.txt"
    if not f.exists():
        raw[pref] = None
        continue
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        parts = line.split("|")
        raw[pref].append({"name": parts[0].strip(), "norm": norm(parts[0])})

print(f"{'都道府県':<8} {'raw':>4} {'公式':>4} {'一致':>4}  rawのみ / 公式のみ")
tot_r = tot_o = tot_b = 0
detail = {}
for pref in SLUG2PREF.values():
    r = raw.get(pref); o = official.get(pref, [])
    onorms = {x["norm"] for x in o}
    if r is None:
        print(f"{pref:<8} {'--':>4} {len(o):>4}  rawファイルなし")
        detail[pref] = {"raw": None, "official_only": [x["name"] for x in o]}
        tot_o += len(o)
        continue
    rnorms = {x["norm"] for x in r}
    both = rnorms & onorms
    ronly = [x["name"] for x in r if x["norm"] not in onorms]
    oonly = [x["name"] for x in o if x["norm"] not in rnorms]
    tot_r += len(r); tot_o += len(o); tot_b += len(both)
    flag = "" if not ronly and not oonly else "  <-- 差異"
    print(f"{pref:<8} {len(r):>4} {len(o):>4} {len(both):>4}{flag}")
    if ronly: print(f"    rawのみ: {ronly}")
    if oonly: print(f"    公式のみ: {oonly}")
    detail[pref] = {"raw_only": ronly, "official_only": oonly, "both": len(both)}
print(f"\n合計 raw={tot_r} 公式={tot_o} 一致(norm)={tot_b}")
json.dump(detail, open(BASE/"gm-compare.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
