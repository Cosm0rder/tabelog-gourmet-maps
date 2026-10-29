#!/usr/bin/env python3
"""Build try-ramen.md from try-match.json + try-area-fill.json + try-raw.tsv."""
import json
from pathlib import Path
from collections import OrderedDict

BASE = Path.home() / "workspace/tabelog-to-google-maps"
data = json.loads((BASE / "try-match.json").read_text(encoding="utf-8"))
fill = json.loads((BASE / "try-area-fill.json").read_text(encoding="utf-8")) if (BASE / "try-area-fill.json").exists() else {"filled": {}}
entries = data["entries"]
shops = {s["display"]: s for s in data["shops"]}

official = json.loads((BASE / "try-area-official.json").read_text(encoding="utf-8"))

def merge_area(pool_area, off_area):
    if not off_area:
        return pool_area
    if not pool_area:
        return off_area
    if pool_area.startswith(off_area) or off_area in pool_area:
        return pool_area  # pool side is more specific (ward-level)
    return off_area

# apply official areas + API fill
for s in data["shops"]:
    if s["status"] == "既存" and not s.get("area") and s["display"] in official:
        s["area"] = official[s["display"]]  # display-only, for the full lists
    if s["status"] == "新規":
        off = official.get(s["display"])
        if off:
            s["area"] = merge_area(s.get("area"), off)
            s["area_src"] = "TRY公式Web"
        if not s.get("area") and s["display"] in fill["filled"]:
            s["area"] = fill["filled"][s["display"]]["area"]
            s["area_src"] = "Yahoo!ローカルサーチAPI"

import sys
sys.path.insert(0, str(BASE))
from prep_match import norm as _norm
shop_by_norm = {}
for s in data["shops"]:
    shop_by_norm.setdefault(_norm(s["display"]), s)

def res_str(results, edition=None):
    parts = []
    for r in results:
        if edition and r["edition"] != edition:
            continue
        rk = f"{r['rank']}位" if r["rank"] not in ("-", "") else "選出"
        grp = {"新店": "新店", "名店": "名店", "TRY大賞": "TRY大賞", "新店大賞": "新店大賞"}[r["group"]]
        if r["category"] == "総合":
            parts.append(f"{'新店大賞' if grp == '新店' else 'TRY大賞'} {rk}")
        else:
            parts.append(f"{grp}・{r['category']} {rk}")
    return "／".join(parts)

L = []
L.append("# TRYラーメン大賞 受賞店一覧と保存リスト突合")
L.append("")
L.append("作成：2026-10-28")
L.append("突合先：saved-list.md（保存リスト1,429件＋コレクション3件＋行ったお店1件＝全1,433件）")
L.append("突合方法：店名を正規化（NFKC・スペース/中黒除去・異体字統一＋㐂→喜・髙→高）して完全一致=既存、包含・近接=要確認候補とし、候補は目視で検証。それ以外=新規。新規については既存4プール（アワード2026新規504／ミシュラン東京2026新規407／百名店2026新規2,637／百名店旧年版新規3,458）との店名重複もチェックした。")
L.append("")
L.append("## 出典と対象版について")
L.append("")
L.append("- 最新版は**第27回 TRYラーメン大賞 2026-2027**（講談社、2026-10-22発売）。ただし全順位は書籍（電子版含む）のみで、Web上では大賞・新店大賞と一部部門結果しか公表されていない。そのため第27回は「公表分のみ」を出典明記で収録した。")
L.append("  - TRY公式Web https://tokyoramenoftheyear.com/ja/article/try-books-002 （TRY大賞＝中華そば しば田／創作麺工房 鳴龍、新店大賞＝Rustic Noodles、新店大賞店の部門1位）")
L.append("  - おとなの週末Web https://otonano-shumatsu.com/articles/592147 ほか（しば田の名店しょう油部門1位）")
L.append("  - PR TIMES（箕輪家：名店とんこつ部門8位）https://prtimes.jp/main/html/rd/p/000000004.000188782.html")
L.append("- 全順位が公開情報で確認できる最新版は**第26回 TRYラーメン大賞 2025-2026**（2025-10-21発売、新店部門9ジャンル・名店部門10ジャンル）。TRY公式Webが2026年7〜10月に「公式Web版」としてTRY大賞・新店大賞・名店部門全10ジャンルの順位と店舗住所を公開しており、これを正とした：https://tokyoramenoftheyear.com/ja/tag/26th-try-ramen-award-results")
L.append("  - 公式Web版が未公開の新店部門9ジャンルは、審査員（いけ麺氏）のブログ「麺好い」掲載の全順位転記で補った：https://ikemen3.blog.jp/archives/1083684330.html 。名店部門はブログ転記と公式Web版を全件照合し、相違した4件（新店大賞総合の順位2件・TRY大賞総合の順位1件・名店つけ麺濃厚の順位1件）は公式Web版に合わせて訂正した。店名表記も公式Web版に統一した箇所がある（例：「中華そば 西川軒」→「中華そば 西川」、「永福町大勝」→「永福町大勝軒」）。")
L.append("- エリアは、TRY公式Webの店舗情報（住所→市区町村まで）を最優先し、次いで各プール・ラーメン百名店2025原データで補った。公式記事に店舗情報の掲載が無い2店（のスた／三代目 博多 だるま）のみYahoo!ローカルサーチAPIで補完した。新店部門のみに登場する33店は公式Web版の新店部門記事が未公開（2026-10-28時点）のため「エリア未確認」とした。")
L.append("")
# summary counts
n_exist = sum(1 for s in data["shops"] if s["status"] == "既存")
n_new = sum(1 for s in data["shops"] if s["status"] == "新規")
n_conf = sum(1 for s in data["shops"] if s["status"] == "要確認")
n_pool = sum(1 for s in data["shops"] if s["status"] == "新規" and s.get("pools"))
n_poolnear = sum(1 for s in data["shops"] if s["status"] == "新規" and s.get("pool_near"))
e27 = [e for e in entries if e["edition"] == 27]
e26 = [e for e in entries if e["edition"] == 26]
u27 = len({(e["name"]) for e in e27})
L.append("## サマリー")
L.append("")
L.append(f"- 収集エントリ：第27回（公表分）{len(e27)}件＋第26回 {len(e26)}件＝延べ{len(entries)}件、ユニーク{len(data['shops'])}店（両版に登場する中華そば しば田・創作麺工房 鳴龍を含む）")
L.append(f"- 既存（保存リストと完全一致）：{n_exist}店")
L.append(f"- 要確認：{n_conf}店（正規化の近接候補6店は目視でいずれも別店舗と判定し、新規に分類した。経緯は付記参照）")
L.append(f"- 新規（保存リストに無い）：{n_new}店")
L.append(f"- 新規のうち既存プールと完全一致で重複：{n_pool}店（内訳は新規セクションのフラグ参照。主にラーメン百名店2025=百名店旧年版新規）")
L.append(f"- 新規のうちプール側と表記ゆれの包含関係があるもの：{n_poolnear}店（フラグに候補名を併記）")
L.append("")
# ---- full lists ----
def emit_full(edition, title):
    L.append(f"## {title}")
    L.append("")
    es = [e for e in entries if e["edition"] == edition]
    groups = OrderedDict()
    for e in es:
        groups.setdefault((e["group"], e["category"]), []).append(e)
    for (grp, cat), items in groups.items():
        L.append(f"### {grp}・{cat}")
        L.append("")
        for e in items:
            rk = f"{e['rank']}位" if e["rank"] not in ("-", "") else "選出（順位なし）"
            shop = shop_by_norm.get(_norm(e["name"]))
            area = (shop.get("area") if shop else None) or e["area_note"]
            tail = f"｜{area}" if area else ""
            L.append(f"- {e['name']}{tail}｜{rk}")
        L.append("")

emit_full(27, "第27回 TRYラーメン大賞 2026-2027（公表分のみ）")
emit_full(26, "第26回 TRYラーメン大賞 2025-2026（全受賞・入賞店）")

# ---- classification ----
def shop_line(s, extra=""):
    area = s.get("area") or "エリア未確認"
    return f"- {s['display']}｜{area}{extra}"

L.append(f"## 既存（保存リストと一致・{n_exist}店）")
L.append("")
for s in data["shops"]:
    if s["status"] == "既存":
        sv = s["saved"][0]
        L.append(f"- {s['display']}｜保存側エリア：{sv['stations']}｜TRY実績：{res_str(s['results'])}")
L.append("")

if n_conf:
    L.append(f"## 要確認（{n_conf}店）")
    L.append("")
    for s in data["shops"]:
        if s["status"] == "要確認":
            L.append(f"- {s['display']}｜候補：{'／'.join(s['near'])}｜TRY実績：{res_str(s['results'])}")
    L.append("")

L.append(f"## 新規（保存リストに無い・{n_new}店）")
L.append("")
L.append("プール重複フラグ：［pool:プール名］=そのプールの新規リストにも完全一致で存在 ／［pool候補:プール名「店名」］=包含関係の表記ゆれ候補")
L.append("")
for s in data["shops"]:
    if s["status"] != "新規":
        continue
    extra = f"｜TRY実績：{res_str(s['results'])}"
    for p in s.get("pools", []):
        extra += f" [pool:{p}]"
    for label, pname in s.get("pool_near", []):
        extra += f" [pool候補:{label}「{pname}」]"
    if s.get("area_src") == "Yahoo!ローカルサーチAPI":
        extra += "（エリアはYahoo!ローカルサーチAPIで補完）"
    L.append(shop_line(s, extra))
L.append("")
L.append("## 付記")
L.append("")
L.append("- 第26回の公式発表は「新店部門9ジャンル、名店部門10ジャンル全279杯」。本ファイルの順位表転記は延べ175エントリ（総合ランキングを含む）で、差分は審査員企画・殿堂入り店紹介等の順位外掲載とみられる。")
L.append("- ブログ転記では名店つけ麺濃厚部門の「中華そば専門 とんちぼ」が11位の後に10位と記載されていたが、公式Web版で12位と確認し訂正した。同様に新店大賞総合は「中華そばの店 みのひ」3位・「味噌らーめん屋 ちょりん」5位が公式順位（転記は両店とも4位）。TRY大賞総合の「中華そば しば田」は3位が公式順位（転記は2位）。")
L.append("- Ramen FeeL（TRY大賞4位ほか）は、TRY公式Webに「2026年2月末で閉店」の注記がある。")
L.append("- エリア未確認の33店はすべて第26回・新店部門のみに登場する店。公式Web版の新店部門記事が公開され次第、住所を補完できる。")
L.append("- 要確認候補として正規化で近接した6店（ラーメン 星印／麺処 ら塾／ラーメン 郷／麺処 一笑／ラーメン 男盛／らーめん 文蔵）は、いずれも保存側候補（ラーメン大至／麺処 銀笹ほか）とは別店舗と目視判定し、新規に分類した。")
L.append("- 第27回の部門別全順位は書籍発売時点でWeb未公開のため未収録。公開され次第、第27回分を全順位に差し替えるのが望ましい。")
L.append("- 同名異店の注意：伊藤中華そば（新店）と中華そば屋 伊藤（名店）は別店舗として扱った。一条流がんこラーメン 金町（新店）と一条流がんこ 総本家分家 四谷荒木町（名店）も別店舗。")
L.append("- 表記ゆれの統一：しお・鶏白湯部門の「らぁめん 元」とつけ麺清湯部門の「らあめん 元」は、公式Web版で同一店（東京都板橋区坂下2-16-11）と確認し「らあめん 元」に統一した（ユニーク店数はこの統一を反映）。")
(BASE / "try-ramen.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote try-ramen.md", len(L), "lines")
print("summary: exist", n_exist, "confirm", n_conf, "new", n_new, "pool", n_pool, "poolnear", n_poolnear)
