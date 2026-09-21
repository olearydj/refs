import sqlite3, os, re, json, collections
home=os.path.expanduser('~/Zotero')
z=sqlite3.connect(f'file:{home}/zotero.sqlite?mode=ro',uri=True)
b=sqlite3.connect(f'file:{home}/better-bibtex.sqlite?mode=ro',uri=True)
q=lambda s,*a: z.execute(s,a).fetchall()
print('client lastVersion', q("select value from settings where setting='client' and key='lastVersion'"))
print('lastCompatibleVersion', q("select value from settings where setting='client' and key='lastCompatibleVersion'"))
import zlib,gzip
raw=q("select value from settings where setting='globalSchema' and key='data'")[0][0]
try: gs=json.loads(zlib.decompress(raw))
except Exception: gs=json.loads(zlib.decompress(raw,-15))
print('embedded globalSchema keys', list(gs.keys()) if isinstance(gs,dict) else type(gs))
print('embedded version', gs.get('version'), 'citationKey string present:', 'citationKey' in json.dumps(gs))
print('fields table has citationKey:', q("select fieldID,fieldName from fields where fieldName like '%itation%'"))
print('libraries', q("select libraryID,type,editable,filesEditable,version,archived from libraries"))
print('groups', q("select count(*) from groups"), 'feeds', q("select count(*) from feeds"))
print('items total', q("select count(*) from items"))
print('items by library', q("select libraryID,count(*) from items group by 1"))
print('items by type:')
for r in q("select t.typeName,count(*) from items i join itemTypes t using(itemTypeID) group by 1 order by 2 desc"): print('  ',r)
print('deletedItems', q("select count(*) from deletedItems"))
print('deleted by type', q("select t.typeName,count(*) from deletedItems d join items i using(itemID) join itemTypes t using(itemTypeID) group by 1"))
print('deletedCollections', q("select count(*) from deletedCollections"))
reg="select i.itemID from items i join itemTypes t using(itemTypeID) where t.typeName not in ('attachment','note','annotation')"
print('regular items', q(f"select count(*) from ({reg})"), 'regular not deleted', q(f"select count(*) from ({reg}) where itemID not in (select itemID from deletedItems)"))
print('attachments by linkMode (0=imported_file,1=imported_url,2=linked_file,3=linked_url,4=embedded_image):')
for r in q("select linkMode,count(*),sum(path is null or path=''),sum(path like 'storage:%'),sum(path like 'attachments:%'),sum(path like '/%'),sum(parentItemID is null) from itemAttachments group by 1"): print('   mode,count,emptypath,storage:,attachments:,absolute,standalone',r)
print('attachment contentType', q("select contentType,count(*) from itemAttachments group by 1 order by 2 desc"))
print('syncState', q("select syncState,count(*) from itemAttachments group by 1"))
print('notes', q("select count(*),sum(parentItemID is null) from itemNotes"))
print('annotations', q("select count(*) from itemAnnotations"), 'by type/isExternal', q("select type,isExternal,count(*) from itemAnnotations group by 1,2"))
print('annotation cols', [c[1] for c in z.execute('pragma table_info(itemAnnotations)')])
print('collections', q("select count(*) from collections"), 'by library', q("select libraryID,count(*) from collections group by 1"))
rows=q("select collectionID,parentCollectionID from collections"); par=dict(rows)
def depth(c):
    d=1
    while par.get(c): c=par[c]; d+=1
    return d
print('collection depth histogram', sorted(collections.Counter(depth(c) for c in par).items()))
print('collectionItems', q("select count(*) from collectionItems"), 'items in >1 coll', q("select count(*) from (select itemID from collectionItems group by 1 having count(*)>1)"))
print('collectionItems of non-regular items', q("select t.typeName,count(*) from collectionItems ci join items i using(itemID) join itemTypes t using(itemTypeID) group by 1"))
print('itemRelations', q("select p.predicate,count(*) from itemRelations r join relationPredicates p using(predicateID) group by 1"))
print('collectionRelations', q("select count(*) from collectionRelations"))
print('tags', q("select count(*) from tags"), 'itemTags by type', q("select type,count(*) from itemTags group by 1"))
print('creators', q("select count(*) from creators"), 'itemCreators by type:')
for r in q("select ct.creatorType,count(*) from itemCreators ic join creatorTypes ct using(creatorTypeID) group by 1 order by 2 desc"): print('  ',r)
print('single-field creators', q("select count(*) from creators where fieldMode=1"))
print('savedSearches', q("select count(*) from savedSearches"), 'publicationsItems', q("select count(*) from publicationsItems"), 'retracted', q("select count(*) from retractedItems"))
print('syncCache rows', q("select count(*) from syncCache"), 'unsynced items', q("select count(*) from items where synced=0"))
print('fulltext words', q("select count(*) from fulltextItemWords"))
# Extra
ex=q("select i.itemID,v.value from itemData d join fields f using(fieldID) join itemDataValues v using(valueID) join items i using(itemID) where f.fieldName='extra'")
print('items with non-empty extra', sum(1 for _,v in ex if v and v.strip()))
cnt=collections.Counter(); itemsw=collections.Counter(); keys=collections.Counter()
for iid,v in ex:
    kinds=set()
    for line in v.splitlines():
        line=line.strip()
        if not line: continue
        m=re.match(r'^(tex|bibtex|biblatex)\.[^:=]+\s*[:=]',line,re.I)
        if m: k='bbt-directive:'+m.group(1).lower()
        elif re.match(r'^citation key\s*:',line,re.I): k='Citation Key:'
        elif re.match(r'^(bibtex|biblatexcitekey)\s*[:\[]',line,re.I): k='legacy bibtex:'
        elif re.match(r'^[A-Za-z][A-Za-z0-9 _-]{0,40}:\s*\S',line):
            k='kv-line'; keys[line.split(':')[0].strip().lower()]+=1
        elif re.match(r'^\{:[^}]+\}',line): k='csl-cheater'
        else: k='prose'
        cnt[k]+=1; kinds.add(k)
    for k in kinds: itemsw[k]+=1
print('extra line kinds (lines)', dict(cnt)); print('extra kinds (items)', dict(itemsw))
print('extra kv labels', keys.most_common(25))
# BBT
print('BBT citationkey rows', b.execute('select count(*),sum(pinned=1),sum(pinned=0 or pinned is null),count(distinct citationKey),count(distinct itemKey) from citationkey').fetchall())
print('BBT pinned typeof', b.execute('select typeof(pinned),pinned,count(*) from citationkey group by 1,2').fetchall())
print('BBT libraryIDs', b.execute('select libraryID,count(*) from citationkey group by 1').fetchall())
print('BBT meta names', b.execute('select name,length(data),migrated from "better-bibtex"').fetchall())
bk={r[0]:r for r in b.execute('select itemKey,itemID,libraryID,citationKey,pinned from citationkey')}
zi={r[0]:(r[1],r[2]) for r in q(f"select i.key,i.itemID,i.libraryID from items i where i.itemID in ({reg})")}
print('regular item keys', len(zi), 'with BBT row', sum(k in bk for k in zi), 'BBT rows without item', sum(k not in zi for k in bk), 'itemID mismatch', sum(1 for k in zi if k in bk and bk[k][1]!=zi[k][0]))
exk={}
for iid,v in ex:
    m=re.search(r'^citation key\s*:\s*(\S+)',v,re.I|re.M)
    if m: exk[iid]=m.group(1)
id2key={v[0]:k for k,v in zi.items()}
print('Extra Citation Key lines', len(exk), 'matching BBT', sum(1 for i,k in exk.items() if id2key.get(i) in bk and bk[id2key[i]][3]==k))
dup=b.execute('select count(*) from (select citationKey from citationkey group by 1 having count(*)>1)').fetchone()
print('duplicate citekeys in BBT', dup)
ck=[r[3] for r in bk.values()]
print('key shape: non-ascii', sum(1 for k in ck if not k.isascii()), 'has uppercase', sum(1 for k in ck if k!=k.lower()), 'has punctuation', sum(1 for k in ck if re.search(r'[^A-Za-z0-9]',k)), 'examples', sorted(ck,key=len)[:2], sorted(ck,key=len)[-1:])
