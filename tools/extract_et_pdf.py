import pdfplumber, re, json, sys

DAY_NAMES = ["lundi","mardi","mercredi","jeudi","vendredi","samedi"]
DAY_MAP = {"lundi":"Lundi","mardi":"Mardi","mercredi":"Mercredi","jeudi":"Jeudi","vendredi":"Vendredi","samedi":"Samedi"}
TIME_RE = re.compile(r'^\d{1,2}h\d{2}$')
TYPE_VOCAB = {"Cours","TD","TP","TD/TP","TP/TD","Cours intégré","cours","intégré","TD,TP"}

def fix(t):
    if len(t) % 2 == 0 and len(t) > 0:
        cand = t[0::2]
        if ''.join(c*2 for c in cand) == t:
            return cand
    return t

def h2m(t):
    m = re.match(r'(\d{1,2})h(\d{2})', t)
    if not m: return None
    return int(m.group(1))*60+int(m.group(2))

def m2h(m):
    return f"{m//60:02d}:{m%60:02d}"

def extract_pdf(path):
    pdf = pdfplumber.open(path)
    sessions = []
    for pageno, p in enumerate(pdf.pages, 1):
        words = p.extract_words(use_text_flow=False, keep_blank_chars=False, extra_attrs=['fontname','size'])
        for w in words:
            w['text'] = fix(w['text'])

        # title (top < 35)
        title_words = sorted([w for w in words if w['top'] < 35 and w['top'] > 15], key=lambda w:(round(w['top']), w['x0']))
        title = " ".join(w['text'] for w in title_words)
        title = re.sub(r'\s+', ' ', title).strip()

        # day header row
        day_words = [w for w in words if w['text'].lower() in DAY_NAMES and 36 < w['top'] < 48]
        if not day_words:
            continue
        day_cols = sorted([(w['x0'], w['text'].lower()) for w in day_words])
        # column width estimate
        xs = [c[0] for c in day_cols]
        if len(xs) > 1:
            width_est = (xs[-1]-xs[0])/(len(xs)-1)
        else:
            width_est = 130

        def day_for_x(x0):
            best, bd = None, 1e9
            for cx, cd in day_cols:
                d = abs(x0-cx)
                if d < bd:
                    bd, best = d, cd
            return DAY_MAP.get(best)

        # session rects: colored blocks, exclude giant border/background
        rects = [r for r in p.rects if r.get('fill') and r['height'] > 20 and r['width'] < 250]
        # dedupe identical rects (sometimes drawn twice)
        seen = set()
        uniq_rects = []
        for r in rects:
            key = (round(r['x0'],1), round(r['top'],1), round(r['x1'],1), round(r['bottom'],1))
            if key in seen: continue
            seen.add(key)
            uniq_rects.append(r)

        for r in uniq_rects:
            day = day_for_x(r['x0'])
            if not day:
                continue
            top, bottom = r['top'], r['bottom']
            # find start/end time labels near top/bottom edges, x close to r.x0
            cand_start = [w for w in words if TIME_RE.match(w['text']) and abs(w['top']-top) < 6 and r['x0']-6 <= w['x0'] <= r['x0']+60]
            cand_end = [w for w in words if TIME_RE.match(w['text']) and (bottom-14) <= w['top'] <= (bottom+4) and r['x0']-6 <= w['x0'] <= r['x0']+60]
            start_t = cand_start[0]['text'] if cand_start else None
            end_t = cand_end[0]['text'] if cand_end else None
            top_bound = cand_start[0]['top']+8 if cand_start else top+6
            bot_bound = cand_end[0]['top']-2 if cand_end else bottom-6

            inner = [w for w in words if r['x0']-2 <= w['x0'] and w['x1'] <= r['x1']+2
                     and top_bound <= w['top'] <= bot_bound]
            inner.sort(key=lambda w:(round(w['top']), w['x0']))

            subj, teacher, room, typ = [], [], [], []
            for w in inner:
                fn = w.get('fontname','')
                txt = w['text']
                if TIME_RE.match(txt):
                    continue
                if 'Bold' in fn:
                    subj.append(txt)
                elif 'Oblique' in fn or 'Italic' in fn:
                    room.append(txt)
                else:
                    if txt in ("Cours","TD","TP","TD/TP","TP/TD","intégré","integre","integré"):
                        typ.append(txt)
                    else:
                        teacher.append(txt)

            def clean(lst):
                s = " ".join(lst)
                s = re.sub(r'\s+([,.;:/])', r'\1', s)
                s = re.sub(r'\s+', ' ', s).strip()
                return s

            room_s = clean(room)
            teacher_s = clean(teacher)
            # fallback: room text sometimes not italic (e.g. "salle info dpt chimie") and lands in teacher
            if not room_s:
                m = re.search(r'([Ss]alle[^,/]*|[Ss]\.\w[\w.]*)$', teacher_s)
                if m:
                    room_s = m.group(1).strip()
                    teacher_s = teacher_s[:m.start()].strip()

            sessions.append({
                "page": pageno,
                "title": title,
                "day": day,
                "start": m2h(h2m(start_t)) if start_t else None,
                "end": m2h(h2m(end_t)) if end_t else None,
                "subject": clean(subj),
                "teacher": teacher_s,
                "room": room_s,
                "type": clean(typ),
            })
    return sessions

if __name__ == "__main__":
    path = sys.argv[1]
    out = extract_pdf(path)
    print(json.dumps(out, ensure_ascii=False, indent=1))
