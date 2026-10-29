import re, os, collections
text = open('/home/hatch/workspace/tabelog-to-google-maps/regroup-plan.md', encoding='utf-8').read()
sections = re.split(r'^## ', text, flags=re.M)[1:]
outdir = '/home/hatch/workspace/tabelog-to-google-maps/chunks/regroup'
os.makedirs(outdir, exist_ok=True)
summary = []
for sec in sections:
    title = sec.split('\n', 1)[0]
    genre = re.sub(r'（\d+店）$', '', title).strip()
    items = []
    for ln in sec.splitlines():
        m = re.match(r'^- (.+?) ― (.+?)／(.+?) ― (.+?)( ※.*)?$', ln)
        if m:
            name = m.group(1)
            first_station = m.group(2).split('、')[0].strip()
            items.append(f'{name}（最寄り：{first_station}）')
    # chunk into <=54
    chunks = [items[i:i+54] for i in range(0, len(items), 54)] or [[]]
    for i, ch in enumerate(chunks, 1):
        fn = f'{outdir}/{genre}-{i}.txt'
        open(fn, 'w', encoding='utf-8').write('\n'.join(ch))
    summary.append((genre, len(items), len(chunks)))
for g, n, c in summary:
    print(f'{g}: {n}店 / {c}ファイル')
print('total genres:', len(summary))
