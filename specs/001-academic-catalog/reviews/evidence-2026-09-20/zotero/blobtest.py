import sqlite3, os, time, hashlib, resource
p='blobtest.sqlite'
for f in (p,p+'.bak'):
    if os.path.exists(f): os.remove(f)
c=sqlite3.connect(p); c.execute('pragma journal_mode=delete'); c.execute('pragma synchronous=full')
c.execute('create table artifacts(sha256 text primary key, bytes blob, n int)')
c.execute('create table sources(id integer primary key, j text)')
c.executemany('insert into sources(j) values(?)', [('x'*6000,) for _ in range(562)]); c.commit()
print('catalog w/o artifacts', os.path.getsize(p))
N=74035200
for i in range(3):
    b=os.urandom(N); t=time.time()
    c.execute('insert into artifacts values(?,?,?)',(hashlib.sha256(b).hexdigest(),b,N)); c.commit()
    print(f'snapshot {i+1}: insert+commit {time.time()-t:.2f}s size {os.path.getsize(p):,}')
del b
t=time.time(); d=sqlite3.connect(p+'.bak'); c.backup(d); d.close(); print(f'backup API copy {time.time()-t:.2f}s size {os.path.getsize(p+".bak"):,}')
t=time.time(); c.execute('vacuum'); print(f'vacuum {time.time()-t:.2f}s')
t=time.time(); r=c.execute('select length(bytes) from artifacts').fetchall(); print(f'length() scan {time.time()-t:.2f}s')
t=time.time(); x=c.execute('select bytes from artifacts limit 1').fetchone()[0]; print(f'read one blob {time.time()-t:.2f}s; maxrss MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6)
t=time.time(); print(c.execute('pragma integrity_check').fetchone(), f'integrity_check {time.time()-t:.2f}s')
c.close(); os.remove(p); os.remove(p+'.bak')
