import sqlite3,os,json
from pypdf import PdfReader
con=sqlite3.connect('file:'+os.path.expanduser('~/Zotero/zotero.sqlite')+'?mode=ro',uri=True)
rows=con.execute("""SELECT a.path,n.position FROM itemAnnotations n JOIN itemAttachments a ON a.itemID=n.parentItemID WHERE length(coalesce(n.comment,''))>0""").fetchall()
def ov(a,b,t=3): return not (a[2]<b[0]-t or b[2]<a[0]-t or a[3]<b[1]-t or b[3]<a[1]-t)
for path,pos in rows:
    p=json.loads(pos); page=PdfReader(path).pages[p['pageIndex']]; found=False
    for ref in (page.get('/Annots') or []):
        o=ref.get_object() if hasattr(ref,'get_object') else ref
        if hasattr(o,'get') and o.get('/Rect') and any(ov([float(x) for x in o['/Rect']],zr) for zr in p.get('rects',[])):
            found = found or bool(o.get('/Contents'))
    print('zotero row with comment -> PDF annotation carries /Contents:',found)
