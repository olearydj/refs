import sqlite3,os,json,collections
from pypdf import PdfReader
con=sqlite3.connect('file:'+os.path.expanduser('~/Zotero/zotero.sqlite')+'?mode=ro',uri=True)
rows=con.execute("""SELECT n.parentItemID,a.path,n.type,n.position,length(coalesce(n.text,'')),length(coalesce(n.comment,'')) FROM itemAnnotations n JOIN itemAttachments a ON a.itemID=n.parentItemID""").fetchall()
by=collections.defaultdict(list)
for pid,path,typ,pos,tl,cl in rows: by[(pid,path)].append((typ,json.loads(pos),tl,cl))
SUB={1:'/Highlight',2:'/Text',5:'/Underline'}
def overlap(a,b,tol=3):
    return not (a[2]<b[0]-tol or b[2]<a[0]-tol or a[3]<b[1]-tol or b[3]<a[1]-tol)
tot=mat=0; loosec=[0]
for i,((pid,path),zs) in enumerate(sorted(by.items(),key=lambda kv:len(kv[1])),1):
    ok=os.path.exists(path)
    if not ok: print(f"file {i}: MISSING on disk; zotero rows={len(zs)}"); tot+=len(zs); continue
    r=PdfReader(path); pdfann=collections.defaultdict(list); kinds=collections.Counter()
    for pi,page in enumerate(r.pages):
        for ref in (page.get('/Annots') or []):
            o=ref.get_object() if hasattr(ref,'get_object') else ref
            if not hasattr(o,'get'): kinds['<malformed>']+=1; continue
            st=o.get('/Subtype')
            if st in ('/Link','/Widget','/Popup'): continue
            kinds[st]+=1; pdfann[pi].append((st,[float(x) for x in o.get('/Rect',[0,0,0,0])],bool(o.get('/Contents'))))
    m=0; un=[]
    for typ,pos,tl,cl in zs:
        pi=pos.get('pageIndex'); rects=pos.get('rects') or []
        hit=any(st==SUB.get(typ,st) and any(overlap(rc,zr) for zr in rects) for st,rc,_ in pdfann.get(pi,[]))
        loose=any(any(overlap(rc,zr) for zr in rects) for st,rc,_ in pdfann.get(pi,[]))
        if not hit and loose: loosec[0]+=1
        m+=hit
        if not hit: un.append(pi)
    tot+=len(zs); mat+=m
    print(f"file {i}: pages={len(r.pages)} zotero_rows={len(zs)} (with comment: {sum(1 for z in zs if z[3])}) pdf_markup_annots={sum(kinds.values())} {dict(kinds)} matched_by_page+type+rect={m} unmatched_pages={un[:8]}")
print('TOTAL zotero rows',tot,'matched strict',mat,'matched by rect only (type differs)',loosec[0])
