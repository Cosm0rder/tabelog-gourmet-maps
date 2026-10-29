#!/usr/bin/env python3
"""Generate gaultmillau.md from gm-match-results.json + official-site comparison."""
import json, sys, unicodedata
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).parent))
from gm_match import norm

BASE = Path.home() / "workspace/tabelog-to-google-maps"
res = json.loads((BASE / "gm-match-results.json").read_text(encoding="utf-8"))["results"]

PREF_ORDER = ["北海道","青森県","秋田県","岩手県","宮城県","山形県","福島県","茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県","新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県","静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県","鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県","福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"]
POOL_LABEL = {"award": "Award2026新規", "michelin": "ミシュラン東京2026新規", "hyaku2026": "百名店2026新規", "hyakuolder": "百名店旧年版新規"}

def score_key(r):
    try: return -float(r["score"])
    except: return 0.0
def sort_key(r):
    return (PREF_ORDER.index(r["pref"]) if r["pref"] in PREF_ORDER else 99, score_key(r), r["name"])

existing = sorted([r for r in res if r["status"] == "既存"], key=sort_key)
review   = sorted([r for r in res if r["status"] == "要確認"], key=sort_key)
new      = sorted([r for r in res if r["status"] == "新規"], key=sort_key)
pool_cnt = Counter()
for r in new:
    for p in r["pools"]: pool_cnt[p] += 1
new_with_pool = sum(1 for r in new if r["pools"])
toque_cnt = Counter(r["toque"] for r in res)
pref_cnt = Counter(r["pref"] for r in res)

# ---- appendix: official-site-only stores (variant pairs removed) ----
def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
def edit_dist(a, b, cap=2):
    if abs(len(a) - len(b)) > cap: return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + (ca != cb))
        prev = cur
    return prev[len(b)]
TRUE_PAIRS = {  # (official-site name, dataset name) judged to be the same store
    ("Héritage by Kei Kobayashi", "Heritage by Kei Kobayashi"),
    ("ヨンセン チャイニーズ レストラン", "4000 Chinese Restaurant"),
    ("ポール", "PAUL"),
    ("nôtori", "ノウトリ"),
    ("越味 一燈", "御料理 一燈"),
    ("研野", "日本料理 研野"),
    ("pesceco（ペシコ）", "pesceco"),
    ("燠火kawaguchi", "宮崎 燠火kawaguchi ∴"),
}
NOT_VARIANT = {"クラージュ", "ラトリエ ドゥ ジョエル・ロブション", "祇園 大渡"}  # similar name, different store
raw_by_pref = defaultdict(list)
for r in res: raw_by_pref[r["pref"]].append(r)
appendix = []
variant_pairs = []
for line in (BASE / "gm-official.txt").read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    name, pref = line.rsplit("|", 1)
    name = name.strip(); pref = pref.strip()
    on = norm(name)
    cands = raw_by_pref.get(pref, [])
    if any(c["norm"] == on for c in cands): continue
    variant = None
    for c in cands:
        if (name, c["name"]) in TRUE_PAIRS:
            variant = c; break
    if variant is None and name not in NOT_VARIANT:
        for c in cands:
            cn = c["norm"]
            if fold(cn) == fold(on):
                variant = c; break
            if len(cn) >= 3 and len(on) >= 3 and (cn in on or on in cn):
                variant = c; break
            if len(on) >= 2 and cn.endswith(on):
                variant = c; break
            if len(cn) >= 4 and edit_dist(cn, on) <= 2:
                variant = c; break
    if variant: variant_pairs.append((name, pref, variant["name"]))
    else: appendix.append((name, pref))
appendix.sort(key=lambda x: (PREF_ORDER.index(x[1]) if x[1] in PREF_ORDER else 99, x[0]))

L = []
L.append("# ゴ・エ・ミヨ 2026 掲載店 × 食べログ保存リスト突合")
L.append("")
L.append("## 版情報")
L.append("- 対象：『ゴ・エ・ミヨ 2026』（Gault & Millau 日本版 最新版）")
L.append("- 発売日：2026年3月17日（公式サイト書誌情報。まとめサイト側は3月18日発売と表記）")
L.append("- 発行：株式会社ONODERA GROUP／発売：株式会社 幻冬舎、定価3,400円（税込）、ISBN 978-4-344-95515-8")
L.append("- 掲載規模：全国581軒・47都道府県（公式発表）")
L.append("")
L.append("## 収集方法と出典")
L.append("- 主データ：まとめサイト「グレンの旅＆グルメ」（xn--e-3e2b.com）のゴ・エ・ミヨ2026都道府県別ページ（全47都道府県）から、店名・都道府県・市区町村・トック数・点数（/20点）・ジャンルを収集。各ページ記載の軒数と抽出件数が全県で一致し、合計が公式発表の581軒と完全一致したため、書籍2026の全店データとみなせる。")
L.append("- 照合：公式サイト（gaultmillau-japan.info）掲載店舗一覧644件とも全件照合した。公式サイト側は書籍2026未収録とみられる店舗も含むため、それらは本編の突合対象から外し、付録に分離した（下記）。公式サイトの東北セクションはテキスト抽出できなかったが、東北6県は主データ側で収集済み。")
L.append("- 突合方法：saved-list.md（1,429店＋付随4件＝1,433件）と店名正規化（NFKC・スペース/中黒除去・異体字統一）で照合。完全一致＝既存、包含・近接（編集距離2以内等）＝要確認、それ以外＝新規。新規については既存4プール（Award 2026新規504／ミシュラン東京2026新規407／百名店2026新規2,637／百名店旧年版新規3,458）との店名重複もチェックした。")
L.append("")
L.append("## 突合結果サマリ")
L.append("")
L.append("| 区分 | 件数 |")
L.append("|---|---|")
L.append(f"| ゴ・エ・ミヨ2026 掲載店（収集総数） | {len(res)} |")
L.append(f"| 既存（保存リストと完全一致） | {len(existing)} |")
L.append(f"| 要確認（類似名が保存リストにあり） | {len(review)} |")
L.append(f"| 新規 | {len(new)} |")
L.append(f"| うち他プール新規と重複する新規 | {new_with_pool} |")
L.append("")
L.append("新規451軒の他プール重複内訳（1店が複数プールに重なる場合あり）：")
for k in ["award", "michelin", "hyaku2026", "hyakuolder"]:
    L.append(f"- {POOL_LABEL[k]}：{pool_cnt[k]}軒")
L.append("")
L.append("トック別内訳：" + "・".join(f"{t} {toque_cnt[t]}" for t in ["5トック", "4トック", "3トック", "2トック", "1トック", "トックなし", "POP"] if toque_cnt[t]))
L.append("")
L.append("都道府県別件数：")
row = []
for p in PREF_ORDER:
    if pref_cnt[p]: row.append(f"{p} {pref_cnt[p]}")
L.append("、".join(row))
L.append("")

def fmt_saved(r):
    out = []
    for s in r.get("saved", []):
        st = s["stations"].replace("、", "／") if isinstance(s["stations"], str) else "/".join(s["stations"])
        out.append(f"{s['name']}（最寄り：{st}、{s['genre']}）" if st else f"{s['name']}（{s['genre']}）")
    return " ／ ".join(out)

L.append(f"## 既存（{len(existing)}軒）")
L.append("")
L.append("保存リストに同一店あり。")
L.append("")
for r in existing:
    L.append(f"- {r['name']}（{r['pref']}・{r['area']}）｜{r['toque']} {r['score']}点｜{r['genre']} → 保存側：{fmt_saved(r)}")
L.append("")
L.append(f"## 要確認（{len(review)}軒）")
L.append("")
L.append("店名が類似する保存店があるもの（別店・別店舗・表記ゆれの可能性を含む）。")
L.append("")
for r in review:
    L.append(f"- {r['name']}（{r['pref']}・{r['area']}）｜{r['toque']} {r['score']}点｜{r['genre']} → 候補：{fmt_saved(r)}")
L.append("")
L.append(f"## 新規（{len(new)}軒）")
L.append("")
L.append("保存リストに無い店舗。［ ］内は他プールの新規リストにも載っている場合のフラグ。")
L.append("")
cur = None
for r in new:
    if r["pref"] != cur:
        cur = r["pref"]
        L.append(f"### {cur}")
    flags = "［" + "・".join(POOL_LABEL[p] for p in r["pools"]) + "］" if r["pools"] else ""
    L.append(f"- {r['name']}（{r['area']}）｜{r['toque']} {r['score']}点｜{r['genre']}{flags}")
L.append("")
L.append(f"## 付録：公式サイトのみ掲載の店舗（{len(appendix)}軒）")
L.append("")
L.append("公式サイトの掲載店舗一覧（644件）にはあるが、上記の書籍2026データ（581軒）には無い店舗。旧版からの継続掲載やウェブのみの掲載とみられ、書籍2026の掲載店とは断定できないため突合対象外とした。")
L.append("")
cur = None
for name, pref in appendix:
    if pref != cur:
        cur = pref
        L.append(f"### {cur}")
    L.append(f"- {name}")
L.append("")
L.append("## 注記")
L.append("- 表記ゆれとして同一店と判断したペア（公式サイト表記 ⇔ 本データ表記）：")
for off, pref, raw_name in variant_pairs:
    L.append(f"  - {off}（{pref}）⇔ {raw_name}")
L.append("- 本データ側のみに載る店舗（公式サイト一覧に無し）：氣分（東京都・港区）、メシモ（神奈川県）。")
L.append("- 『4000 Chinese Restaurant』（東京都）は保存リスト側にも同名で載っており既存扱い。公式サイトでは『ヨンセン チャイニーズ レストラン』表記。")
L.append("- 点数は20点満点。POPは点数評価ではなく特筆店舗の紹介区分。")
L.append("- 原データ：gm-raw/（都道府県別テキスト）、公式サイト照合データ：gm-official.txt、突合結果：gm-match-results.json")
L.append("")
(BASE / "gaultmillau.md").write_text("\n".join(L), encoding="utf-8")
print(f"gaultmillau.md written: existing={len(existing)} review={len(review)} new={len(new)} appendix={len(appendix)} variant_pairs={len(variant_pairs)}")
print("variant pairs:", variant_pairs)
