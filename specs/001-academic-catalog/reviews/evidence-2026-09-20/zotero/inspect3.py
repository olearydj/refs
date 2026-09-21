import sqlite3, os, json, zlib, collections
home=os.path.expanduser('~/Zotero')
z=sqlite3.connect(f'file:{home}/zotero.sqlite?mode=ro',uri=True)
q=lambda s,*a: z.execute(s,a).fetchall()
print('itemData rows for citationKey field', q("select count(*) from itemData d join fields f using(fieldID) where f.fieldName='citationKey'"))
print('itemTypeFields with citationKey', q("select count(*) from itemTypeFields tf join fields f using(fieldID) where f.fieldName='citationKey'"))
raw=q("select value from settings where setting='globalSchema' and key='data'")[0][0]
gs=json.loads(zlib.decompress(raw)); s=json.dumps(gs)
import re
print('where citationKey appears in embedded schema v28:', [k for k in gs if 'citationKey' in json.dumps(gs[k])], 'meta' , json.dumps(gs['meta'])[:300])
print('csl part mention', [ (k) for k,v in gs['csl'].items() if 'citationKey' in json.dumps(v)])
print('itemNotes by item type', q("select t.typeName,count(*),sum(n.note is null or n.note=''),sum(n.parentItemID is null) from itemNotes n join items i using(itemID) join itemTypes t using(itemTypeID) group by 1"))
print('unsynced by type', q("select t.typeName,count(*) from items i join itemTypes t using(itemTypeID) where synced=0 group by 1"))
print('syncCache by type', q("select o.name,count(*),sum(length(data)) from syncCache c join syncObjectTypes o using(syncObjectTypeID) group by 1"))
r=q("select data from syncCache c join syncObjectTypes o using(syncObjectTypeID) where o.name='item' limit 1")[0][0]
d=json.loads(r); print('syncCache item JSON top keys', list(d.keys()), 'data keys', sorted(d.get('data',{}).keys())[:40])
print('items version/synced cols', [c[1] for c in z.execute('pragma table_info(items)')])
print('itemAttachments cols', [c[1] for c in z.execute('pragma table_info(itemAttachments)')])
print('itemRelations sample object shape', [re.sub(r'[A-Z0-9]{8}$','XXXXXXXX',re.sub(r'users/\d+','users/<id>',r[0])) for r in q("select object from itemRelations limit 2")])
print('dc:replaces / owl:sameAs predicates defined', q("select predicate from relationPredicates"))
# path resolvability
ok=miss=0; roots=collections.Counter()
for (p,) in q("select path from itemAttachments where linkMode=2"):
    if os.path.exists(p): ok+=1
    else: miss+=1
    roots['/'.join(p.split('/')[:5])]+=1
print('linked_file exists', ok, 'missing', miss, 'roots', roots.most_common(6))
ok=miss=0
for k,p in q("select i.key,a.path from itemAttachments a join items i using(itemID) where a.path like 'storage:%'"):
    if os.path.exists(os.path.join(home,'storage',k,p[8:])): ok+=1
    else: miss+=1
print('storage: exists', ok, 'missing', miss)
# size breakdown
try:
    rows=q("select name,sum(pgsize) from dbstat group by 1 order by 2 desc limit 12")
    tot=q("select sum(pgsize) from dbstat")[0][0]
    print('dbstat total',tot); [print('  ',n,sz,f'{sz/tot:.1%}') for n,sz in rows]
except Exception as e: print('dbstat unavailable',e)
print('dbDebug1?', q("select count(*) from dbDebug1"))
b=sqlite3.connect(f'file:{home}/better-bibtex.sqlite?mode=ro',uri=True)
for name,data in b.execute('select name,data from "better-bibtex" where name in ("better-bibtex")'):
    try:
        j=json.loads(data); print('bbt meta', name, {k:(v if not isinstance(v,(list,dict)) else type(v).__name__) for k,v in j.items()} if isinstance(j,dict) else type(j))
    except Exception as e: print('bbt meta parse', e, data[:80])
