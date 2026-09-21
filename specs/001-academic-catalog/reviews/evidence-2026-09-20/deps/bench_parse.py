import time, sys
N=int(sys.argv[1])
ent = '''@article{key%d,
  author = {M{\\"u}ller, J{\\"o}rg and van der Berg, Johannes and {World Health Organization}},
  title = {The {NASA} Mission %d: A Study of $\\alpha$-decay \\& Growth},
  journaltitle = {Journal of Synthetic Results},
  date = {2020-05-%02d},
  volume = {%d}, pages = {1--20},
  doi = {10.1000/abc_%d},
  abstract = {Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.},
}

'''
s = "".join(ent % (i,i,(i%28)+1,i,i) for i in range(N))
open(f"fx/big{N}.bib","w").write(s)
import bibtexparser, bibtexparser.middlewares as m
t=time.perf_counter(); lib=bibtexparser.parse_string(s); t1=time.perf_counter()-t
print(f"bibtexparser v2 default stack N={N}: {t1:.2f}s entries={len(lib.entries)} failed={len(lib.failed_blocks)}")
t=time.perf_counter(); lib=bibtexparser.parse_string(s, append_middleware=[m.SeparateCoAuthors(), m.SplitNameParts()]); print(f"  + names: {time.perf_counter()-t:.2f}s")
t=time.perf_counter(); lib=bibtexparser.parse_string(s, append_middleware=[m.LatexDecodingMiddleware()]); print(f"  + latex decode: {time.perf_counter()-t:.2f}s")
