# Channel between sessions

This folder carries messages between session 1 (Claude, review) and session 2 (Codex, implementation) in place of the owner's clipboard. It is a trial begun 2026-09-27. The folder is excluded from git locally; session 1 commits a pass's thread alongside its report when the pass closes.

## Messages

One file per message, never edited after it appears. The name is `YYYY-MM-DD-HHMMSS-<from>-<short-description>.md`, with `<from>` as `s1`, `s2` or `owner`, so the folder sorts as the conversation. Write the file under a name starting with `.` and rename it into place, so a reader never sees half a message.

Every message starts with four lines:

```
from: s1 | s2 | owner
next: s1 | s2 | owner
kind: task | question | answer | report | decision | ack | stopping
re: <file name this answers, or ->
```

`next` names who acts now. A message without one is an error; the reader stops and tells the owner.

The owner may write here too, as `from: owner`; a message such as "pause" binds both sessions. On waking, read every message you have not yet read, not only the newest.

## Waiting

After sending, the sender watches this folder for the next message addressed to it, and keeps watching while it waits on the owner too. Wait in bounded chunks (a loop of short sleeps inside one command, with the longest timeout your shell tool allows) and repeat. Match a message by the sender field of its name, not anywhere in it. A session that picks up a task writes a one-line `ack`, so the sender knows it arrived. After 120 minutes with nothing, write a `stopping` message, then stop and tell the owner in your own session; whoever sees it wakes that session.

## The owner stays in the loop

Session 1 stops for the owner, in its own session, at every owner gate: approving a proposal, accepting an export gate, any `--record`, merging a branch, and any decision that goes to the ledger. During the trial session 1 also stops whenever it is unsure; the owner removes safeties, session 1 does not. Session 1 keeps one question open with the owner at a time and names any others as queued. While a decision is pending, session 2 does only work that needs none, or waits.

A message that carries an owner decision has `kind: decision` and quotes the owner's words verbatim. Session 2 does not execute a step that needs owner approval without such a quote.

Session 2 does not use its ask-the-user interface. A question goes here as `kind: question` addressed to s1, and session 1 answers it or takes it to the owner. The owner may interrupt either session at any time; what the owner says there overrides this folder.
