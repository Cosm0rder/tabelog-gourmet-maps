import csv, os, re, collections
BASE = os.path.expanduser('~/workspace/tabelog-to-google-maps')
OUT = os.path.join(BASE, 'mymaps-csv')
os.makedirs(OUT, exist_ok=True)

rows = []  # (name, area, genre, source, flag, origin)
# 1) new pool
with open(os.path.join(BASE, 'new-pool-unified.tsv'), encoding='utf-8') as f:
    r = csv.DictReader(f, delimiter='\t')
    for d in r:
        rows.append((d['店名'].strip(), d['エリア/最寄り'].strip(), d['百名店ジャンル'].strip(), d['出典ソース'].strip(), d['備考フラグ'].strip(), '新規プール'))
# 2) saved stores from regroup chunks: 店名（最寄り：駅）
regdir = os.path.join(BASE, 'chunks/regroup')
for fn in sorted(os.listdir(regdir)):
    if not fn.endswith('.txt'): continue
    genre = re.sub(r'-\d+\.txt$', '', fn)
    with open(os.path.join(regdir, fn), encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            m = re.match(r'^(.*?)（最寄り：(.*?)）$', line)
            if m:
                rows.append((m.group(1).strip(), m.group(2).strip(), genre, '食べログ保存済み', '', '保存済み'))
            else:
                rows.append((line, '', genre, '食べログ保存済み', '', '保存済み'))

def norm(s):
    s = s.lower()
    s = re.sub(r'[\s　・･\-—―~〜/／()（）「」『』【】\[\]]', '', s)
    return s

# dedupe: same genre + normalized name -> merge (saved takes precedence info-wise; keep both sources)
merged = {}
for name, area, genre, src, flag, origin in rows:
    key = (genre, norm(name), norm(area)[:6])
    if key in merged:
        e = merged[key]
        if origin not in e[5]: e[5] += '+' + origin
        if src and src not in e[3]: e[3] += '、' + src
        if flag and flag not in e[4]: e[4] += flag
    else:
        merged[key] = [name, area, genre, src, flag, origin]

by_genre = collections.defaultdict(list)
for v in merged.values():
    by_genre[v[2]].append(v)

total = 0
for genre, items in sorted(by_genre.items()):
    items.sort(key=lambda x: (x[1], x[0]))
    path = os.path.join(OUT, f'{genre}.csv')
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['店名', '位置検索', '出典'])
        for name, area, g, src, flag, origin in items:
            query = f'{name} {area}'.strip()
            w.writerow([name, query, src])
    total += len(items)
    print(f'{genre}: {len(items)}')
print('TOTAL', total)
