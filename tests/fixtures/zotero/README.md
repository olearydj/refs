# Synthetic Zotero fixture

`fixture.py` creates only synthetic data in a caller-supplied temporary directory. `userdata.sql` is the unmodified Zotero 6.0.37 userdata schema 121 from https://raw.githubusercontent.com/zotero/zotero/6.0.37/resource/schema/userdata.sql. SHA-256: `dfe40b669bf61852132385cb9aed5efd0f669e1fddfc3aac10b0395446217e8f`. Zotero copyright and AGPL-3.0-or-later terms remain in the file; COPYING contains the upstream license. These reference files are tests only and are not distributed in the refs wheel.

The fixture includes six regular items, nine creator roles and ordered coauthors, three collections, three memberships, three file attachments, a URL attachment, a child note, an attachment outline, an annotation, a related pair, trash and a legacy key database. Tests vary it for local identities, malformed parents, unsupported versions and missing locators. No real library data is included.
