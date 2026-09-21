import unicodedata, unidecode
from unidecode import unidecode as ud, UnidecodeError
from anyascii import anyascii
from text_unidecode import unidecode as tud
def nfkd(s): return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)).encode("ascii","ignore").decode()
names = ["García", "García", "Łódź", "Søren", "Straße", "Иванов", "Παπαδόπουλος", "山田", "القرشي", "𠮷", "", "😀", "Nguyễn", "Đặng", "Þórsson", "O’Brien", "Müller-Lüdenscheidt", "김", "Ðorđević", "İstanbul", "Æsir"]
print(f"{'input':22} {'Unidecode1.4.0 strict':24} {'anyascii 0.3.3':22} {'text-unidecode 1.3':22} {'stdlib NFKD':14}")
for n in names:
    s = unicodedata.normalize("NFC", n)
    try: a = repr(ud(s, errors="strict"))
    except UnidecodeError as e: a = "ERROR(strict)"
    print(f"{n!r:22} {a:24} {anyascii(s)!r:22} {tud(s)!r:22} {nfkd(s)!r:14}")
