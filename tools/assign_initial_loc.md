# Initial loc assignment

This one-time cutover tool reads recorded file paths. It opens no attachments and moves no files. For a source with files it proposes the folder relative to the supplied Box root, otherwise the folder of its managed file relative to the library root, otherwise unfiled for non-topic storage. Collections never determine loc. A storage attachment follows the Box folder when the source has both. File-less sources receive no assignment. Unexpected multiple Box or managed folders are reported for an explicit owner choice.

Run against a disposable rehearsal catalog first. Only the owner executes the real cutover after the CCC backup.

```sh
uv run --locked python tools/assign_initial_loc.py --config "$CONFIG" --catalog "$CATALOG" --box-root "$BOX_COPY" > assignments-preview.json
uv run --locked python tools/assign_initial_loc.py --config "$CONFIG" --catalog "$CATALOG" --box-root "$BOX_COPY" --execute > assignments-applied.json
```

Both reports include source ID, citation key, revision, old loc, proposed loc, reason and state. The second invocation recomputes the proposals, then applies each through the revision-checked update path. It does not mark loc as a corrected field. A stale revision refuses that update. Where no assignment is proposed, an existing loc is retained. Review the applied report before previewing reorg.
