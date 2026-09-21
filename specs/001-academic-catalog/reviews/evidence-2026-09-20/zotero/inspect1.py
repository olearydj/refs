import sqlite3, os, sys
home=os.path.expanduser('~/Zotero')
def opn(name):
    p=os.path.join(home,name)
    for q in ('mode=ro','mode=ro&immutable=1'):
        try:
            c=sqlite3.connect(f'file:{p}?{q}',uri=True,timeout=2)
            c.execute('select count(*) from sqlite_master').fetchone()
            print(f'## {name}: opened with {q}')
            return c
        except Exception as e:
            print(f'## {name}: {q} failed: {e!r}')
    return None
z=opn('zotero.sqlite')
print('sqlite lib',sqlite3.sqlite_version)
for r in z.execute("select schema,version from version order by schema"): print(' version',r)
for pr in ('page_size','page_count','freelist_count','journal_mode','user_version','encoding'):
    print(' pragma',pr,z.execute(f'pragma {pr}').fetchone())
tabs=[r[0] for r in z.execute("select name from sqlite_master where type='table' order by name")]
print(' tables',len(tabs)); print(' ',tabs)
print(' settings:', z.execute("select setting,key,length(value) from settings").fetchall()[:20])
b=opn('better-bibtex.sqlite')
if b:
    for r in b.execute("select type,name from sqlite_master order by 1,2"): print('  bbt',r)
    for t in [r[0] for r in b.execute("select name from sqlite_master where type='table'")]:
        print('  bbt rows',t,b.execute(f'select count(*) from "{t}"').fetchone())
        print('  cols',[ (c[1],c[2]) for c in b.execute(f'pragma table_info("{t}")')])
s=opn('better-bibtex-search.sqlite')
if s:
    for r in s.execute("select type,name from sqlite_master order by 1,2"): print('  bbts',r)
