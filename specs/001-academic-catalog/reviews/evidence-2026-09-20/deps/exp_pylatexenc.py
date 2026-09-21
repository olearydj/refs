import pylatexenc, sys, warnings
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexencode import unicode_to_latex, UnicodeToLatexEncoder
print("pylatexenc", pylatexenc.__version__, "python", sys.version.split()[0])
cases = [
 r'The {NASA} Mission to {{M}ars}',
 r'A {\"o} and \"{o} and \"o and {\"O}ber',
 r'Study of $\alpha$-decay \& 50\% Growth in {$\mathrm{CO}_2$}',
 r'M{\"u}ller, J{\"o}rg and Erd\H{o}s, P\'al and {\O}stergaard, S{\o}ren',
 r'https://example.org/a_b%20c#frag?x=1&y=2~z',
 r'10.1000/abc_def(2021)1%2F2',
 r'Journal with {"}quotes{"} {and} \textit{italics} and \emph{emph} --- dash -- en ``q\'\'',
 r'Nested {braces {three {deep}}} and \{ escaped \}',
 r'Vall{\'e}e Poussin, Charles~Louis',
 r'\noopsort{1990}Title with \unknownmacro{arg} and {\sc Small Caps}',
 r'Na\"{\i}ve \c{c} \v{s} \ss{} \L{}\'od\'z \aa \ae',
 r'Unbalanced {brace',
 r'$x_i^2 \leq \frac{1}{2}$ and H$_2$O',
]
l2t = LatexNodes2Text()
l2t_keep = LatexNodes2Text(math_mode='verbatim', keep_braced_groups=True, strict_latex_spaces=True)
for c in cases:
    print("IN   :", c)
    for name, conv in (("default", l2t), ("keepbr", l2t_keep)):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                u = conv.latex_to_text(c)
            except Exception as e:
                u = None; print(f"  {name} EXC {type(e).__name__}: {e}")
        if u is not None:
            back = unicode_to_latex(u)
            again = conv.latex_to_text(back)
            print(f"  {name:7} L->U : {u!r}")
            print(f"  {name:7} U->L : {back!r}   same_as_input={back==c}  U_stable={again==u}")
print("##### unicode_to_latex on plain unicode")
for u in ["Müller & Søn 50% _x_ #1 ~ {NASA} $5 Erdős Łódź “quoted” — α β ﬁ 山田 naïve \\textit{x}"]:
    print(repr(unicode_to_latex(u)))
    print(repr(unicode_to_latex(u, non_ascii_only=True)))
