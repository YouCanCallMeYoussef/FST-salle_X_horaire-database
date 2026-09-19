import pdfplumber, re, sys, json
DAYS=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
LBL=re.compile(r'^(\d{1,2})h(\d{2})?-(\d{1,2})h(\d{2})?$')
def run(path):
    out=[]
    pdf=pdfplumber.open(path)
    for pn,p in enumerate(pdf.pages,1):
        words=p.extract_words()
        for w in words:
            t=w['text']
            if len(t)%2==0 and t and t[0::2]*1==t[0::2] and ''.join(ch*2 for ch in t[0::2])==t: w['text']=t[0::2]
        days=[w for w in words if w['text'] in DAYS]
        cols=sorted((w['x0'],w['x1'],w['text']) for w in days)
        # column boundaries: midpoint between day word centers
        cent=[((a+b)/2,d) for a,b,d in cols]
        ys=[]
        for r in p.rects+p.lines:
            if r['x0']<30 and r['x1']>60 and (r['bottom']-r['top'])<2:
                y=(r['top']+r['bottom'])/2
                if not ys or all(abs(y-v)>2 for v in ys): ys.append(y)
        ys.sort()
        hdr=[w for w in words if w['text'] in DAYS][0]['bottom']
        B=[y for y in ys if y>=hdr-3]
        def y2t(y,edge=None):
            k=min(range(len(B)),key=lambda i:abs(B[i]-y))
            return 8*60+15*k
        def day(x):
            return min(cent,key=lambda c:abs(c[0]-x))[1]
        leftmost=cols[0][0]-40
        blocks={}
        for r in p.rects:
            c=r.get('non_stroking_color')
            if not r.get('fill') or r['width']<40 or r['height']<3: continue
            if c in (None,(1,1,1),[1,1,1],(1.0,),[1.0],1,1.0) : continue
            if isinstance(c,(list,tuple)) and len(c)==3 and all(v>0.97 for v in c): continue
            pass
            for i,(cx,d) in enumerate(cent):
                lo=(cent[i-1][0]+cx)/2 if i else cx-70
                hi=(cent[i+1][0]+cx)/2 if i+1<len(cent) else cx+70
                a=max(lo,r['x0']); b=min(hi,r['x1'])
                if b-a>20:
                    blocks.setdefault((d,str(c)),[]).append((r['top'],r['bottom'],a,b))
        title=" ".join(w['text'] for w in words if w['top']<110)
        for (d,c),lst in blocks.items():
            lst.sort()
            # merge contiguous
            groups=[]
            for t,b,x0,x1 in lst:
                if groups and t-groups[-1][1]<3: groups[-1][1]=max(groups[-1][1],b); groups[-1][2]=min(groups[-1][2],x0); groups[-1][3]=max(groups[-1][3],x1)
                else: groups.append([t,b,x0,x1])
            for t,b,x0,x1 in groups:
                txt=" ".join(w['text'] for w in words if x0-1<=w['x0']<=x1 and t-1<=w['top']<=b)
                out.append(dict(page=pn,day=d,start=y2t(t,'top'),end=y2t(b,'bot'),color=c,text=txt,title=title))
    return out
for s in sorted(run(sys.argv[1]),key=lambda s:(s['page'],DAYS.index(s['day']),s['start'])):
    print(s['page'],s['day'],f"{s['start']//60}:{s['start']%60:02d}-{s['end']//60}:{s['end']%60:02d}",'|',s['text'])
