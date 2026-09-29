from: s1
next: s2
kind: task
re: -

Owner, verbatim: "why not 1 + 2?", choosing both: guidance that a label is a short tag, and a rule that spaces in a label become hyphens in the filename segment. Main is at a244793 (0.9.3). Protocol: ack and go straight on; end your turn after the report.

Branch s2/label-segment-hyphens from main:

1. Rule. The filename's label segment currently keeps only letters, digits, dots and hyphens, so "Author-hosted full text (journal article)" became "Author-hostedfulltextjournalarticle". Change it so whitespace becomes a hyphen before the other characters are dropped, runs of hyphens collapse to one, and leading or trailing hyphens are trimmed; that label becomes "Author-hosted-full-text-journal-article". Every existing single-token label must produce exactly the same segment as today (test transcription, scan, capture, PDF, r2023-06-03, mobile, figure-ruby-photo-1), and an empty result still omits the segment. The stored label text never changes; existing filenames are not renamed. Update the files-and-recovery.md sentence and its example if needed. Tests per docs/testing-convention.md, including preview equals execution for a spaced label on add and resource add.

2. Guidance. Where --label is described for users (the CLI help for --label on add and resource add, and the contract), say a label is a short tag, one or two words, hyphenated, such as scan, capture or r2023-06-03. Session 1 will add the same line to the conversion guide.

Full suite with TEXMFVAR and TEXMFCACHE at /private/tmp/refs-csl-tex-cache, Ruff, ty. No export path is involved. Report here; merging is the owner's gate.
