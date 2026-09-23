# Human output, discussion notes, 2026-09-23

A discussion between the owner and the review session about how refs prints for people. Direction agreed; details open; nothing here is a contract. The `--json` envelope is unaffected throughout.

## The problem

Search and list print one line per record with the fields joined by pipes: key, first author, year, title, matched fields. The owner: "the formatting of output lines like 'something | blah | another field' is really not readable or user friendly." Long titles run past the terminal edge and the eye cannot find the column it wants.

## Direction

Plain rich tables: rich's table with the box and header off, so rows are aligned columns with no lines, one column allowed to wrap. The owner: "I like rich plain tables. good compromise, esp when using text color / formatting to help focus on what is most important." Rich is already installed through typer, so this costs no dependency. Three shapes were compared: aligned columns (best for comparing sources, needs width), two lines per record (readable, weak for comparison), and boxed tables (heavier, worse on narrow terminals). The plain table gives aligned columns on a wide terminal and wraps the title on a narrow one, so comparison survives without truncation.

The same primitive serves every output class with a different shape:

- Record lists (search, list, project show): columns for key, year, first author, title; type, file count and matched fields when width allows, dropping first when it does not; a dim count line at the end.
- Short-row lists (import list, resource check, collection list, the open chooser, reorg preview): the same table with nothing wrapping. Old and new path pairs are one row with the old path above the new.
- One record (show): a two-column table of label and value; multi-valued fields such as files take one row per value under the same label.
- Reports (export, reorg execute, import): a one-sentence summary, then one small table per group.
- Confirmations (add, update, cite and the rest): a sentence, styled, not a table.

Style vocabulary, used the same way everywhere and nowhere else: bold for the citation key, since it is what the next command takes; dim for secondary facts such as matched fields, revisions and counts; yellow for warnings; red for errors. When stdout is not a terminal, the same rows print as tab-separated plain text with no wrapping and no styles, and structure comes from `--json`.

The current human layouts are about seventy lines in two modules, one function per command shape. One table builder plus a shape per class replaces them at about the same size.

## Simulated output

Search on a wide terminal, keys bold, type and matched column dim:

```
fleuret2023little   2023  Fleuret    book     The Little Book of Deep Learning                    title
canziani2022teach   2022  Canziani   article  Teaching deep learning, a boisterous ever-evolving  title, abstract
                                              model
vaswani2017atten    2017  Vaswani    article  Attention Is All You Need                           abstract
3 sources
```

Show, labels dim, file labels dim in the right column:

```
Key        johnson2023boost
Type       book
Authors    Adam Johnson
Year       2023
Title      Boost Your Git DX: Improve Your Command Line Development Experience
loc        lib/sw-dev/carpentry
Files      BoostYourGitDX-2023-r2023-06-03.pdf   r2023-06-03
           BoostYourGitDX-2023-r2023-10-04.pdf   r2023-10-04
Projects   (none)
Revision   3
```

Reorg preview, old path dim, "renamed" yellow:

```
Preview: 31 files would move, 3 renamed on collision, nothing deleted.

tan2024large      ~/Zotero/storage/P5KPKSGQ/2402.html
                  lib/papers/aiml/2402b.html                 renamed
```

## Open, in the owner's words where there are any

- Smart shortening of long content when space is constrained, for example a path as `root/.../folder/folder/file`. Owner: "downside is reduced clarity and limited cut and paste utility, but I think it is worth further consideration. stick a pin in it for now."
- Whether wide terminals get the extra comparison columns, type and file count.
- Whether search shows the matched column only when there is something to say.
- Two guesses made while sketching, not proposed: `import list` shortening batch IDs to eight characters as git does, with the full ID in JSON; the reorg execute report pointing at a saved report file instead of printing every pair.
- Where this sits on the slate. It touches every command, so it pairs naturally with the help pass named in the [plan's post-slice-3 row](../specs/001-academic-catalog/plan.md#deferred-work).
