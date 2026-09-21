import pylatexenc
from pylatexenc.latex2text import LatexNodes2Text
s = r'Study of \ensuremath{\alpha}-decay \& 50\% Growth in CO\_2'
print(pylatexenc.__version__, repr(LatexNodes2Text().latex_to_text(s)))
