"""Synthetic APA comparison: intended CSL standard, @standard, portable @misc."""
import json
import subprocess
import tempfile
from pathlib import Path
root=Path(__file__).resolve().parent
style=root.parent/'evidence-2026-09-20/export/csl/apa.csl'
record={'id':'example','type':'standard','title':'Example standard','author':[{'literal':'Research and Standards Council'}],'issued':{'date-parts':[[2024]]},'number':'EX-42'}
inputs={'csl':('json',json.dumps([record])), 'native':('bib','@standard{example,title={Example Standard},author={{Research and Standards Council}},number={EX-42},year={2024}}'), 'portable':('bib','@misc{example,title={Example Standard},author={{Research and Standards Council}},howpublished={Standard EX-42},year={2024}}')}
results={}
with tempfile.TemporaryDirectory() as temp:
 for route,(suffix,content) in inputs.items():
  path=Path(temp)/f'{route}.{suffix}';path.write_text(content)
  r=subprocess.run(['pandoc','-f','markdown','-t','html','--citeproc','--csl',str(style),'--bibliography',str(path)],input='[@example]\n',text=True,capture_output=True,check=True)
  results[route]={'input':content,'html':r.stdout,'stderr':r.stderr}
results['pandoc']=subprocess.check_output(['pandoc','--version'],text=True).splitlines()[0]
(root/'standard-render-results.json').write_text(json.dumps(results,indent=2)+'\n')
for route in inputs:print(route, results[route]['html'])
