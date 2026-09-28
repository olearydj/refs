# Channel between sessions

This folder carries messages between session 1 (Claude, review) and session 2 (Codex, implementation) in place of the owner's clipboard. It is a trial begun 2026-09-27. The folder is excluded from git locally; session 1 commits a pass's thread alongside its report when the pass closes.

## Messages

One file per message, never edited after it appears. The name is `YYYY-MM-DD-HHMMSS-<from>-<short-description>.md`, with `<from>` as `s1`, `s2` or `owner`, so the folder sorts as the conversation. Write the file under a name starting with `.` and rename it into place, so a reader never sees half a message. No two messages share a timestamp; wait a second if needed.

Every message starts with four lines:

```
from: s1 | s2 | owner
next: s1 | s2 | owner
kind: task | question | answer | report | decision | ack | stopping
re: <file name this answers, or ->
```

`next` names who acts now. A message without one is an error; the reader stops and tells the owner.

The owner may write here too, as `from: owner`; a message such as "pause" binds both sessions. On waking, read every message you have not yet read, not only the newest.

## Waiting and waking

Session 2 does not poll. After writing its message it ends its turn, and it names its session id in its first `ack` of a pass. Session 1 wakes it after writing a message, with `codex queue --thread <session 2's id> --message "New message in comms: <file name>"`; the queued message starts session 2's turn even when it is idle (tested 2026-09-27). The folder stays the record; the queue is only the doorbell. The owner can wake session 2 the same way, or by typing in its window.

Session 1 waits with a background watcher, which costs nothing while idle, and keeps it running while it waits on the owner too. The watcher matches a message by the sender field of its name, not anywhere in it. After 120 minutes with nothing, session 1 tells the owner.

A session that picks up a task writes an `ack` that restates the task in a line and names the folder it is working in, so the sender knows it arrived and was understood. A session that must stop before finishing writes a `stopping` message saying where it stands.

## The owner stays in the loop

Session 1 stops for the owner, in its own session, at every owner gate: approving a proposal, accepting an export gate, any `--record`, merging a branch, and any decision that goes to the ledger. During the trial session 1 also stops whenever it is unsure; the owner removes safeties, session 1 does not. Session 1 keeps one question open with the owner at a time and names any others as queued. While a decision is pending, session 2 does only work that needs none, or waits.

A message that carries an owner decision has `kind: decision` and quotes the owner's words verbatim. Session 2 does not execute a step that needs owner approval without such a quote.

Session 2 does not use its ask-the-user interface. A question goes here as `kind: question` addressed to s1, and session 1 answers it or takes it to the owner. The owner may interrupt either session at any time; what the owner says there overrides this folder.
