import subprocess, time, statistics, sys, os
py = os.path.abspath(".venv/bin/python")
cases = [("python -c pass", [py, "-c", "pass"]), ("python -S -c pass",[py,"-S","-c","pass"])]
for a in ["app_argparse","app_click","app_typer","app_typer_norich","app_typer_pyd"]:
    cases.append((a+" show k", [py, a+".py", "show", "k"]))
for a in ["app_argparse","app_click","app_typer","app_typer_norich"]:
    cases.append((a+" --help", [py, a+".py", "--help"]))
cases += [("import pydantic", [py,"-c","import pydantic"]), ("import pydantic + define 1 model", [py,"-c","from pydantic import BaseModel\nclass M(BaseModel):\n x:int\n y:str"]),
          ("import sqlite3", [py,"-c","import sqlite3"]), ("import bibtexparser", [py,"-c","import bibtexparser"]), ("import unidecode", [py,"-c","import unidecode"]),("import rich.console",[py,"-c","import rich.console"])]
for name, cmd in cases:
    ts=[]
    for i in range(22):
        t=time.perf_counter(); subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); ts.append((time.perf_counter()-t)*1000)
    first=ts[0]; ts=ts[2:]
    print(f"{name:36s} first={first:7.1f}ms  median={statistics.median(ts):6.1f}ms  min={min(ts):6.1f}ms  max={max(ts):6.1f}ms")
