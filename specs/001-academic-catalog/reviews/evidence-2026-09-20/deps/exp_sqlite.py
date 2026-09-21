import sqlite3, sys, pathlib
print("python", sys.version); print("executable", sys.executable)
print("sqlite_version", sqlite3.sqlite_version, "threadsafety", sqlite3.threadsafety)
c = sqlite3.connect(":memory:", autocommit=False)
print("autocommit attr:", c.autocommit)
opts = [r[0] for r in c.execute("PRAGMA compile_options")]
print("compile_options:", opts)
for feat in ["ENABLE_FTS5","ENABLE_FTS3","ENABLE_JSON1","OMIT_JSON","ENABLE_RTREE","ENABLE_MATH_FUNCTIONS","ENABLE_DBSTAT_VTAB","THREADSAFE=1","OMIT_LOAD_EXTENSION","ENABLE_STAT4","ENABLE_GEOPOLY"]:
    print(f"   {feat}: {any(o.startswith(feat) for o in opts)}")
print("json:", c.execute("select json_extract('{\"a\":[1,2]}', '$.a[1]')").fetchone(), "jsonb:", c.execute("select typeof(jsonb('{\"a\":1}')), json(jsonb('{\"a\":1}'))").fetchone())
for tok in ["unicode61", "unicode61 remove_diacritics 2", "porter unicode61", "trigram", "trigram remove_diacritics 1", "ascii"]:
    try:
        c.execute(f"create virtual table t using fts5(title, tokenize=\"{tok}\")")
        c.execute("insert into t values ('Müller and Erdős on Łódź: naïve Straße')")
        res = {q: c.execute("select count(*) from t where t match ?", (q,)).fetchone()[0] for q in ["muller","erdos","lodz","strasse","naive","ull"]}
        print(f"   tokenizer {tok!r}: OK {res}")
        c.execute("drop table t")
    except Exception as e:
        print(f"   tokenizer {tok!r}: FAIL {e}")
print("strict tables:", c.execute("create table s(a int) strict").fetchall() == [])
print("backup api:", hasattr(c, "backup"), "| Path.move:", hasattr(pathlib.Path, "move"), "Path.copy:", hasattr(pathlib.Path, "copy"), "hardlink_to:", hasattr(pathlib.Path, "hardlink_to"))
try:
    c.enable_load_extension(True); print("load_extension: available")
except Exception as e: print("load_extension:", type(e).__name__, e)
