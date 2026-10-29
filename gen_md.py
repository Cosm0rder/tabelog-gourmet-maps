#!/usr/bin/env python3
"""Generate michelin-kyoto-osaka2026.md. Overlap precomputed in match-final.json."""
import json
import sys
from pathlib import Path
from collections import Counter

BASE = Path.home() / "workspace/tabelog-to-google-maps"
data = json.loads((BASE / "match-final.json").read_text(encoding="utf-8"))
final = data["final"]
overlap = data["award_overlap"]

KUBUN = ["3つ星", "2つ星", "1つ星", "ビブグルマン", "セレクテッド"]
TAG = {"exact": "既存", "hyoki": "既存・表記ゆれ", "confirm": "要確認", "new": "新規"}
cnt = Counter((f["kubun"], f["final"]) for f in final)
tot = Counter(f["kubun"] for f in final)
n_exact = sum(1 for f in final if f["final"] == "exact")
n_hyoki = sum(1 for f in final if f["final"] == "hyoki")
n_conf = sum(1 for f in final if f["final"] == "confirm")
n_new = sum(1 for f in final if f["final"] == "new")
city_new = Counter(f["city"] for f in final if f["final"] == "new")
city_all = Counter(f["city"] for f in final)
FLAG = " 【アワードと重複】"

L = []
L.append("# ミシュランガイド京都・大阪 2026 掲載店リスト（全479店）と食べログ保存リスト照合結果")
L.append("")
L.append("作成：2026-10-28")
L.append("対象ガイド：ミシュランガイド京都・大阪 2026（2026-04-23発表、書籍発売 2026-04-28）")
L.append("出典：ミシュラン公式サイト（guide.michelin.com）の掲載情報をジャンル別に集計したまとめサイト「グレンの旅＆グルメ」（xn--e-3e2b.com）の京都・大阪2026ジャンル別一覧ページ群から全店を収集（東京編 michelin-tokyo2026.md と同一出典）。区分別・都市別件数（3つ星9＝京都6・大阪3／2つ星31＝19・12／1つ星139＝73・66／ビブグルマン106＝47・59／セレクテッド194＝99・95、計479＝京都244・大阪235）が、ミシュラン公式プレスリリース（2026-04-23）の発表値と完全一致することを確認済み。")
L.append("照合先：食べログ保存リスト saved-list.md（1,429件＋コレクション等、実パース1,433件）")
L.append("照合方法：店名を正規化（NFKC・スペース/中黒除去・異体字統一・繰り返し記号展開）して完全一致を「既存」とし、欧文⇔カナ表記・ジャンル接頭辞の有無・短縮表記など表記差のみで、保存側のエリア・ジャンルと整合するものを「既存（表記ゆれ）」として同一店と判定。同名・同グループでも支店や姉妹店など別店舗の公算が高いもの、名前が類似するが別店の公算が高いものは「要確認」に分離した。さらに新規店舗については、The Tabelog Award 2026 の新規504店（award2026.md）と店名の重複をチェックし、重なるものに「アワードと重複」フラグを付けた（欧文⇔カナ等の表記差がある10組も同一店と判定して含む）。")
L.append("")
L.append("## 照合結果サマリー")
L.append("")
L.append("| 区分 | 総数 | 既存（完全一致） | 既存（表記ゆれ） | 要確認 | 新規 |")
L.append("|---|---|---|---|---|---|")
for k in KUBUN:
    L.append("| " + k + " | " + str(tot[k]) + " | " + str(cnt[(k, "exact")]) + " | " + str(cnt[(k, "hyoki")]) + " | " + str(cnt[(k, "confirm")]) + " | " + str(cnt[(k, "new")]) + " |")
L.append("| **合計** | **479** | **" + str(n_exact) + "** | **" + str(n_hyoki) + "** | **" + str(n_conf) + "** | **" + str(n_new) + "** |")
L.append("")
L.append("- 既存（保存リストにあり）：" + str(n_exact + n_hyoki) + "店（完全一致" + str(n_exact) + "＋表記ゆれ" + str(n_hyoki) + "）")
L.append("- 新規（保存リストに無い）：" + str(n_new) + "店（京都" + str(city_new["京都"]) + "・大阪" + str(city_new["大阪"]) + "）→ 本ファイル末尾の「新規」セクションに全件収録")
L.append("- 要確認：" + str(n_conf) + "店（同グループの支店・姉妹店など別店舗の公算が高いもの。詳細は「要確認」セクション）")
L.append("- アワードと重複：新規" + str(n_new) + "店のうち" + str(len(overlap)) + "店が The Tabelog Award 2026 の新規504店にも含まれている（「新規」セクションでフラグ表示）。後の統合では二重追加しないこと")
L.append("- 都市別：京都" + str(city_all["京都"]) + "店・大阪" + str(city_all["大阪"]) + "店")
L.append("")
L.append("## 既存（表記ゆれで一致した5店）")
L.append("")
L.append("| ミシュラン表記 | 区分 | エリア | 保存リスト表記 | 保存側エリア |")
L.append("|---|---|---|---|---|")
for f in final:
    if f["final"] == "hyoki":
        s = f["saved_final"][0]
        L.append("| " + f["name"] + " | " + f["kubun"] + " | " + f["area"] + " | " + s["name"] + "（保存No." + str(s["no"]) + "） | " + s["stations"] + "／" + s["genre"] + " |")
L.append("")
L.append("## 要確認（11店）")
L.append("")
L.append("店名が類似する保存店が存在するが、支店・姉妹店など別店舗の公算が高いもの。人手での最終確認用に候補と注記を併記する。")
L.append("")
L.append("| ミシュラン店名 | 区分 | エリア | ジャンル | 類似する保存店（エリア） | 注記 |")
L.append("|---|---|---|---|---|---|")
for f in final:
    if f["final"] == "confirm":
        s = f["saved_final"][0]
        L.append("| " + f["name"] + " | " + f["kubun"] + " | " + f["area"] + " | " + f["genre"] + " | " + s["name"] + "（保存No." + str(s["no"]) + "） ― " + s["stations"] + "／" + s["genre"] + " | " + f["note"] + " |")
L.append("")
L.append("## 全掲載店リスト（区分別・479店）")
for k in KUBUN:
    rows = [f for f in final if f["kubun"] == k]
    L.append("")
    L.append("### " + k + "（" + str(len(rows)) + "店）")
    L.append("")
    for f in rows:
        flag = FLAG if f["name"] in overlap else ""
        L.append("- " + f["name"] + "｜" + f["area"] + "｜" + f["genre"] + " 【" + TAG[f["final"]] + "】" + flag)
L.append("")
L.append("## 新規（保存リストに無い店舗・" + str(n_new) + "店）")
L.append("")
L.append("「【アワードと重複】」は The Tabelog Award 2026 の新規504店（award2026.md）にも店名が含まれるもの。統合時は二重追加に注意。")
for k in KUBUN:
    rows = [f for f in final if f["kubun"] == k and f["final"] == "new"]
    L.append("")
    L.append("### " + k + "（" + str(len(rows)) + "店）")
    L.append("")
    for f in rows:
        flag = FLAG if f["name"] in overlap else ""
        L.append("- " + f["name"] + "｜" + f["area"] + "｜" + f["genre"] + flag)
L.append("")
L.append("## 付記")
L.append("")
L.append("- 収集元のまとめサイトは guide.michelin.com を出典として明記しており、今回の収集分はジャンル別ページの目次軒数とも一致した。なお guide.michelin.com 自体は本環境のポリシーで直接取得できないため、東京編と同一の集計サイト経由とした。")
L.append("- セレクテッドの件数について、OMAKASEの記事では189店（京都96・大阪93）とされていたが、公式プレスリリースでは194店（京都99・大阪95）。総計479と一致する公式値を採用した。")
L.append("- 「徳ハ本也」（京都・2つ星）の正式表記は「徳ㇵ本也」（ㇵは小書き）。収集元ブログの表記「徳ハ本也」のまま収録した。アワード2026では「徳ㇵ本也」でGOLD受賞しており、新規セクションでは表記差を吸収してアワード重複としてフラグ済み。")
L.append("- 「空心 伽藍堂」（大阪・1つ星）：2026年版では空心の別館・伽藍堂のみが掲載され、保存リストにある「空心」本体は未掲載とみられるため要確認に分類した。")
L.append("- 保存リストにある京都・大阪の有力店でも、本湖月（大阪）、飯田・前田・安久（京都）、欧文表記店（Sugalabo V、リュミエール等）などは2026年版に掲載がなく、本ファイルの対象外である（照合はミシュラン掲載店→保存リストの方向でのみ実施）。")
L.append("")

text = "\n".join(L)
(BASE / "michelin-kyoto-osaka2026.md").write_text(text, encoding="utf-8")
print("wrote michelin-kyoto-osaka2026.md lines:", len(L))
print("overlap:", len(overlap), "status:", n_exact, n_hyoki, n_conf, n_new)
