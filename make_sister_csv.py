import re, csv, os
BASE = os.path.expanduser('~/workspace/tabelog-to-google-maps')
text = open(os.path.join(BASE, 'sister-candidates.md'), encoding='utf-8').read()

# brand display name for search prefix, per section header keyword
rows = []
genre = None; brand = None; sub = None
for line in text.splitlines():
    h2 = re.match(r'^## (.+)', line)
    if h2:
        t = h2.group(1)
        m = re.match(r'^(.*?)→\s*(.+)$', t)
        if m:
            brand = m.group(1).strip(); genre = m.group(2).strip()
        else:
            brand = t; genre = None
        sub = None
        continue
    h3 = re.match(r'^### (.+)', line)
    if h3:
        sub = h3.group(1)
        continue
    b = re.match(r'^- (.+)', line)
    if b and genre:
        item = b.group(1).strip()
        # stop conditions: notes lines starting with ※ handled below since they're separate lines
        mm = re.match(r'^(.*?)（(.*?)）(.*)$', item)
        if mm:
            name, area, rest = mm.group(1).strip(), mm.group(2).strip(), mm.group(3)
        else:
            name, area = item, ''
        name = re.sub(r'【.*?】', '', name).strip()
        # genre override for ippe-koppe subsection
        g = genre
        ctx = (sub or '') + brand
        if 'いっぺこっぺ' in ctx and 'いっぺこっぺ' in (sub or ''):
            g = 'カレー'
        prefix = ''
        bt = re.split(r'[（(]', brand)[0].strip()
        if brand.startswith('とんかつ檍'):
            bt = 'いっぺこっぺ' if (sub and 'いっぺこっぺ' in sub) else 'とんかつ檍'
            if name.endswith('店') and bt not in name:
                prefix = bt
        elif brand.startswith('松富士食品') or brand.startswith('うしごろ'):
            prefix = ''
        elif name.endswith('店') and bt not in name and '店' not in bt:
            prefix = bt
        area = re.sub(r'、(202\d|旧|新業態).*$', '', area)
        disp = f'{prefix} {name}'.strip() if prefix else name
        if name.startswith('銀座4丁目店'):
            disp = '銀座 とんかつ 檍'
        if name == '東京つけめん 久臨':
            area = ''
        query = f'{disp} {area}'.strip()
        rows.append([disp, query, f'広義・{brand}（{g}）'])
print(len(rows))
for r in rows: print(r)
with open(os.path.join(BASE, 'mymaps-csv/広義・姉妹店.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['店名', '位置検索', '出典']); w.writerows(rows)
