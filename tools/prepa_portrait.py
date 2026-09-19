import pdfplumber,sys
DAYS=["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI","SAMEDI"]
p=pdfplumber.open(sys.argv[1]).pages[0]
ws=p.extract_words()
vx=[]
for r in p.rects+p.lines:
    if r['x1']-r['x0']<2 and r['bottom']-r['top']>10 and r['top']<200:
        x=(r['x0']+r['x1'])/2
        if all(abs(x-v)>3 for v in vx): vx.append(x)
vx.sort(); vx=vx[1:]  # drop leftmost page edge (time column left)
days=[dict(text=DAYS[i],x0=vx[i],x1=vx[i+1],bottom=203) for i in range(min(6,len(vx)-1))]
print([round(v) for v in vx])
# time grid from left label column
ys=[]
for r in p.rects+p.lines:
    if r['x0']<60 and r['x1']>80 and r['bottom']-r['top']<2:
        y=(r['top']+r['bottom'])/2
        if all(abs(y-v)>2 for v in ys): ys.append(y)
ys.sort()
w8=[w for w in ws if w['x0']<95 and w['text'] in ('8','8H') and w['top']>150][0]
y8=min(ys,key=lambda y:abs(y-w8['bottom']))
w18=[w for w in ws if w['x0']<95 and w['text']=='18H'][0]
y18=min(ys,key=lambda y:abs(y-w18['bottom']))
B=[y for y in ys if y>=y8-1]
print('check 18H index',B.index(y18),'(expect 40)')
hdr=y8+1
def t(y):
    k=min(range(len(B)),key=lambda i:abs(B[i]-y)); m=8*60+15*k; return f"{m//60:02d}:{m%60:02d}"
# column x ranges from vertical borders
for d in days:
    cx=(d['x0']+d['x1'])/2
    hs=[]
    for r in p.rects+p.lines:
        h=r['bottom']-r['top']
        if r['x0']<=cx<=r['x1']:
            if h<2: hs.append((r['top']+r['bottom'])/2)
            elif r.get('fill') and r['width']>20 and h<20: hs+= [r['top'],r['bottom']]
            elif r.get('fill') and r['width']>20: hs+=[r['top'],r['bottom']]
    hs=sorted(set(round(v,1) for v in hs if v>hdr-1))
    # dedupe
    H=[]
    for v in hs:
        if not H or v-H[-1]>2: H.append(v)
    # find char in each segment
    for a,b in zip(H,H[1:]):
        # use column bounds approx +-30
        chars=[c for c in p.chars if d['x0']<(c['x0']+c['x1'])/2<d['x1'] and a<c['top']<b and c['text'].strip()]
        if chars:
            cols={}
            for c in chars: cols.setdefault(round(c['x0']),[]).append(c)
            lines=[]
            for x in sorted(cols):
                cs=sorted(cols[x],key=lambda c:-c['top'])
                lines.append(''.join(c['text'] for c in cs))
            print(d['text'],t(a),t(b),'|',' / '.join(lines)[:120])
