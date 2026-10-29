# -*- coding: utf-8 -*-
"""Destination Restaurants + OAD を saved-list.md と突合し destination-oad.md を生成する。
突合方法は hyakumeiten-raw/match.py と同一：店名正規化→完全一致=既存、包含=要確認、それ以外=新規。
"""
import re, sys, unicodedata
sys.path.insert(0, '/home/hatch/workspace/tabelog-to-google-maps')
from importlib import import_module
data = import_module('destination-oad-data')

BASE = '/home/hatch/workspace/tabelog-to-google-maps'

STRIP = re.compile(r"[\s　・･\.\,\-‐−–—―'’‘\"“”()（）\[\]【】「」&＆/／:：]")

def norm(s):
    s = unicodedata.normalize('NFKC', s).lower()
    return STRIP.sub('', s)

# --- saved-list ---
saved = []
with open(f'{BASE}/saved-list.md', encoding='utf-8') as f:
    for line in f:
        m = re.match(r'^\d+\.\s+(.+?)\s+―', line)
        if m:
            saved.append(m.group(1).strip())
saved_norm = {}
for s in saved:
    saved_norm.setdefault(norm(s), s)

def parse_pool(path):
    names = []
    in_new = False
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                if '新規' in line:
                    in_new = True
                elif '要確認' in line or '既存' in line:
                    in_new = False
                elif line.startswith('## '):
                    in_new = False
                continue
            if in_new and line.startswith('- '):
                name = re.split(r'[｜（(―]', line[2:].strip())[0].strip()
                name = name.rstrip('）)').strip()
                if name:
                    names.append(name)
    return names

POOLS = {
    'Award2026': f'{BASE}/award2026.md',
    'ミシュラン東京2026': f'{BASE}/michelin-tokyo2026.md',
    '百名店2026': f'{BASE}/hyakumeiten-2026-new.md',
    '百名店旧年': f'{BASE}/hyakumeiten-older-new.md',
}
pool_data = {}
for label, path in POOLS.items():
    ns = parse_pool(path)
    pool_data[label] = (ns, {norm(n): n for n in ns})
    print(f'pool {label}: {len(ns)} names parsed', file=sys.stderr)

def classify(name):
    n = norm(name)
    if n in saved_norm:
        return '既存', saved_norm[n]
    cands = []
    if len(n) >= 3:
        for sn, sorig in saved_norm.items():
            if len(sn) >= 3 and (n in sn or sn in n):
                cands.append(sorig)
    if cands:
        return '要確認', '、'.join(sorted(set(cands))[:4])
    return '新規', ''

def pool_check(name):
    n = norm(name)
    hits = []
    for label, (ns, ndict) in pool_data.items():
        if n in ndict:
            hits.append(f'{label}（完全一致）')
            continue
        if len(n) >= 3:
            for pn in ndict:
                if len(pn) >= 3 and (n in pn or pn in n):
                    hits.append(f'{label}（包含: {ndict[pn]}）')
                    break
    return hits

dr_rows = []
for disp, mname, pref, year, note in data.DR:
    st, det = classify(mname)
    pools = pool_check(mname) if st == '新規' else []
    dr_rows.append(dict(disp=disp, mname=mname, pref=pref, year=year, note=note,
                        status=st, detail=det, pools=pools))

oad_ranked = []
for rank, en, city, jp in data.OAD_RANKED:
    st, det = classify(jp)
    pools = pool_check(jp) if st == '新規' else []
    oad_ranked.append(dict(rank=rank, en=en, city=city, jp=jp, status=st, detail=det, pools=pools))

oad_hr = []
for en, city, jp in data.OAD_HR:
    st, det = classify(jp)
    pools = pool_check(jp) if st == '新規' else []
    oad_hr.append(dict(en=en, city=city, jp=jp, status=st, detail=det, pools=pools))

oad_rec = []
for en, city, jp in data.OAD_REC:
    st, det = classify(jp)
    pools = pool_check(jp) if st == '新規' else []
    oad_rec.append(dict(en=en, city=city, jp=jp, status=st, detail=det, pools=pools))

def count(rows):
    c = {'既存': 0, '要確認': 0, '新規': 0}
    for r in rows:
        c[r['status']] += 1
    return c

dr_c = count(dr_rows)
rk_c = count(oad_ranked)
hr_c = count(oad_hr)
rc_c = count(oad_rec)
oad_all = oad_ranked + oad_hr + oad_rec
oad_c = count(oad_all)

def pool_overlap(rows):
    tot = 0
    per = {}
    for r in rows:
        if r['pools']:
            tot += 1
            for p in r['pools']:
                key = p.split('（')[0]
                per[key] = per.get(key, 0) + 1
    return tot, per

dr_ov, dr_ov_per = pool_overlap(dr_rows)
rk_ov, rk_ov_per = pool_overlap(oad_ranked)
hr_ov, hr_ov_per = pool_overlap(oad_hr)
rc_ov, rc_ov_per = pool_overlap(oad_rec)

uniq_new = {}
for r in dr_rows:
    if r['status'] == '新規':
        uniq_new.setdefault(norm(r['mname']), ('DR', r))
for rows, src in ((oad_ranked, 'OAD順位'), (oad_hr, 'OAD HR'), (oad_rec, 'OAD Rec')):
    for r in rows:
        if r['status'] == '新規':
            uniq_new.setdefault(norm(r['jp']), (src, r))

print('=== SUMMARY ===')
print(f"DR: total {len(dr_rows)} 既存{dr_c['既存']} 要確認{dr_c['要確認']} 新規{dr_c['新規']} / 新規中プール重複 {dr_ov} {dr_ov_per}")
print(f"OAD Ranked: total {len(oad_ranked)} 既存{rk_c['既存']} 要確認{rk_c['要確認']} 新規{rk_c['新規']} / プール重複 {rk_ov} {rk_ov_per}")
print(f"OAD HR: total {len(oad_hr)} 既存{hr_c['既存']} 要確認{hr_c['要確認']} 新規{hr_c['新規']} / プール重複 {hr_ov} {hr_ov_per}")
print(f"OAD Rec: total {len(oad_rec)} 既存{rc_c['既存']} 要確認{rc_c['要確認']} 新規{rc_c['新規']} / プール重複 {rc_ov} {rc_ov_per}")
print(f"OAD total entries: {len(oad_all)} 既存{oad_c['既存']} 要確認{oad_c['要確認']} 新規{oad_c['新規']}")
print(f"Unique new stores (DR+OAD deduped): {len(uniq_new)}")

out = []
out.append('# Destination Restaurants × OAD Top Restaurants Japan — 収集・突合結果')
out.append('')
out.append('収集日: 2026-10-28。突合方法は既存成果物と同一（店名正規化→完全一致=既存、包含=要確認、それ以外=新規）。')
out.append('新規店については既存4プール（Award2026新規504 / ミシュラン東京2026新規407 / 百名店2026新規2,637 / 百名店旧年新規3,458）の新規一覧との店名重複もチェック済み。')
out.append('')
out.append('## サマリー')
out.append('')
out.append('| ソース | 総数 | 既存 | 要確認 | 新規 | 新規のうち他プール重複 |')
out.append('|---|---|---|---|---|---|')
out.append(f"| Destination Restaurants（2021–2026累計） | {len(dr_rows)} | {dr_c['既存']} | {dr_c['要確認']} | {dr_c['新規']} | {dr_ov} |")
out.append(f"| OAD 2026 Ranked（順位付き） | {len(oad_ranked)} | {rk_c['既存']} | {rk_c['要確認']} | {rk_c['新規']} | {rk_ov} |")
out.append(f"| OAD 2026 Highly Recommended | {len(oad_hr)} | {hr_c['既存']} | {hr_c['要確認']} | {hr_c['新規']} | {hr_ov} |")
out.append(f"| OAD 2026 Recommended（日本分） | {len(oad_rec)} | {rc_c['既存']} | {rc_c['要確認']} | {rc_c['新規']} | {rc_ov} |")
out.append(f"| OAD 合計（エントリ数） | {len(oad_all)} | {oad_c['既存']} | {oad_c['要確認']} | {oad_c['新規']} | — |")
out.append('')
out.append(f"両ソース通算の重複を除いた「新規」ユニーク店数: **{len(uniq_new)}店**（下記「新規」セクション）。")
out.append('')
out.append('注記:')
out.append('- OAD公式サイト（oadreviews.com）は本環境から取得不可のため、OADリストの転載ページ（En Primeur Club の OAD Japan 2026 リスト）を出典にした。')
out.append('- OAD Ranked は公表枠150位までだが転載リストは149件（145位が欠落）。Highly Recommended は転載表で48件。Recommended は転載247件のうち海外所在の誤載5件（パリ2・ベルギー1・ロンドン1・NY1）を除外し242件。')
out.append('- OADの店名は転載が英語表記主体のため、突合用に日本語の食べログ店名へ読み替えた。読み替えが不確かな店は英語名のまま突合しており、新規に過大計上されている可能性がある。')
out.append('- Destination Restaurants 2021の2店（Tonoya-Yo＝岩手県、日本料理 Yukimoto）は日本語店名が公式情報で確定できず、英語名のまま記載・突合した。')
out.append('- 同一店が複数ソースに重複掲載される（例：片折・めくみ・茶懐石 温石はDRとOAD両方）。各ソースの表はエントリ単位、「新規」セクションは店単位で重複排除した。')
out.append('- 登喜和鮨は DR2023=新発田市 と OAD68位=新潟市 で同名だが別店の可能性が高く、店名突合では同一視される点に注意。')
out.append('')
out.append('## Destination Restaurants（2021–2026・全60店）')
out.append('')
out.append('| 選出年 | 店名 | 都道府県 | 突合 |')
out.append('|---|---|---|---|')
for r in dr_rows:
    tag = r['status']
    if r['status'] == '要確認':
        tag += f"（候補: {r['detail']}）"
    elif r['status'] == '新規' and r['pools']:
        tag += '（他プール重複: ' + '、'.join(r['pools']) + '）'
    note = f" ※{r['note']}" if r['note'] else ''
    out.append(f"| {r['year']} | {r['disp']} | {r['pref']} | {tag}{note} |")
out.append('')
out.append('## OAD Top Restaurants in Japan 2026 — Ranked')
out.append('')
out.append('| 順位 | 店名 | 都市 | 突合 |')
out.append('|---|---|---|---|')
for r in oad_ranked:
    tag = r['status']
    if r['status'] == '要確認':
        tag += f"（候補: {r['detail']}）"
    elif r['status'] == '新規' and r['pools']:
        tag += '（他プール重複: ' + '、'.join(r['pools']) + '）'
    out.append(f"| {r['rank']} | {r['jp']}（{r['en']}） | {r['city']} | {tag} |")
out.append('')
out.append('## OAD Top Restaurants in Japan 2026 — Highly Recommended')
out.append('')
out.append('| 店名 | 都市 | 突合 |')
out.append('|---|---|---|')
for r in oad_hr:
    tag = r['status']
    if r['status'] == '要確認':
        tag += f"（候補: {r['detail']}）"
    elif r['status'] == '新規' and r['pools']:
        tag += '（他プール重複: ' + '、'.join(r['pools']) + '）'
    out.append(f"| {r['jp']}（{r['en']}） | {r['city']} | {tag} |")
out.append('')
out.append('## OAD Top Restaurants in Japan 2026 — Recommended（日本分）')
out.append('')
out.append('| 店名 | 都市 | 突合 |')
out.append('|---|---|---|')
for r in oad_rec:
    tag = r['status']
    if r['status'] == '要確認':
        tag += f"（候補: {r['detail']}）"
    elif r['status'] == '新規' and r['pools']:
        tag += '（他プール重複: ' + '、'.join(r['pools']) + '）'
    out.append(f"| {r['jp']}（{r['en']}） | {r['city']} | {tag} |")
out.append('')
out.append('## 要確認（保存リストに包含・近接する候補あり）')
out.append('')
for r in dr_rows:
    if r['status'] == '要確認':
        out.append(f"- {r['disp']}（DR {r['year']}・{r['pref']}）→ 保存候補: {r['detail']}")
for r in oad_ranked:
    if r['status'] == '要確認':
        out.append(f"- {r['jp']}（OAD {r['rank']}位・{r['city']}）→ 保存候補: {r['detail']}")
for r in oad_hr:
    if r['status'] == '要確認':
        out.append(f"- {r['jp']}（OAD Highly Recommended・{r['city']}）→ 保存候補: {r['detail']}")
for r in oad_rec:
    if r['status'] == '要確認':
        out.append(f"- {r['jp']}（OAD Recommended・{r['city']}）→ 保存候補: {r['detail']}")
out.append('')
out.append(f'## 新規（保存リストに無い・ユニーク{len(uniq_new)}店）')
out.append('')
out.append('形式: - 店名｜ソース｜地域〔他プール重複フラグ〕')
out.append('')
for key, (src, r) in uniq_new.items():
    if src == 'DR':
        out.append(f"- {r['disp']}｜Destination Restaurants {r['year']}｜{r['pref']}" + (f"｜重複: {'、'.join(r['pools'])}" if r['pools'] else ''))
    elif src == 'OAD順位':
        out.append(f"- {r['jp']}｜OAD 2026 {r['rank']}位｜{r['city']}" + (f"｜重複: {'、'.join(r['pools'])}" if r['pools'] else ''))
    elif src == 'OAD HR':
        out.append(f"- {r['jp']}｜OAD 2026 Highly Recommended｜{r['city']}" + (f"｜重複: {'、'.join(r['pools'])}" if r['pools'] else ''))
    else:
        out.append(f"- {r['jp']}｜OAD 2026 Recommended｜{r['city']}" + (f"｜重複: {'、'.join(r['pools'])}" if r['pools'] else ''))
out.append('')
out.append('## 出典')
out.append('')
out.append('- Destination Restaurants 公式: https://authentic-japan-selection.japantimes.com/ （各年の選出店・都道府県）')
out.append('- 2022年発表: PR TIMES（ザ・ジャパンタイムズ）リリース')
out.append('- 2023年: 料理通信「ジャパンタイムズ『The Japan Times Destination Restaurants 2023』発表」')
out.append('- 2025/2026年発表: The Japan Times 各年リリース記事')
out.append('- OAD Top Restaurants in Japan 2026（Ranked / Highly Recommended / Recommended）: En Primeur Club の OAD リスト転載ページ https://enprimeurclub.com/en/road-journal/oad-japan-ranking-2026-best-restaurants-list')

with open(f'{BASE}/destination-oad.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')
print('wrote destination-oad.md', file=sys.stderr)
