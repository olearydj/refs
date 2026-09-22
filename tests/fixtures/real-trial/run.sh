#!/usr/bin/env bash
# Exercise refs against copies of real bibliographies in throwaway homes. Read-only on the copies' sources.
set -uo pipefail
T="$(cd "$(dirname "$0")" && pwd)"; REPO=/Volumes/Casa/dev/refs; OUT="$T/out"; rm -rf "$OUT"; mkdir -p "$OUT"
R() { uv run --project "$REPO" --locked refs "$@"; }
log() { printf '%s\n' "$*" | tee -a "$OUT/findings.txt"; }
home() { local n=$1; export REFS_CONFIG="$OUT/$n/config.toml" REFS_CATALOG="$OUT/$n/cat"; mkdir -p "$OUT/$n"; R init --library-root "$OUT/$n/lib" >/dev/null 2>&1 || log "[$n] init failed"; }

failures=0
for p in pipyer-paper 2026-jose-danvas 2026-insight-dema-llm manufacturing-training-media-tradeoffs dissertation; do
  home "$p"; bib="$T/papers/$p/references.bib"; n=$(grep -c '^@' "$bib")
  echo "===== $p ($n entries)"
  R --json import --format bib --input "$bib" --origin "$p" > "$OUT/$p/import.json" 2> "$OUT/$p/import.err"; ec=$?
  jq -c '{status, counts: .data.counts, warnings: [.warnings[].code] | unique, errors: [.errors[].code] | unique}' "$OUT/$p/import.json" 2>/dev/null || cat "$OUT/$p/import.err"
  echo "exit=$ec"
  jq -e '.data.counts.invalid == 0 and .data.counts.conflict == 0' "$OUT/$p/import.json" >/dev/null || failures=$((failures+1))
  # limitations by kind
  jq -r '[.data.entries[]? | .limitations[]? | .field] | group_by(.) | map("\(.[0]) x\(length)") | .[]' "$OUT/$p/import.json" 2>/dev/null | sed 's/^/  limitation: /'
  jq -r '[.data.entries[]? | select(.status!="applied") | "\(.status) \(.citation_key)"] | .[]' "$OUT/$p/import.json" 2>/dev/null | head -8 | sed 's/^/  /'
  # re-import idempotence
  R --json import --format bib --input "$bib" --origin "$p" > "$OUT/$p/reimport.json"
  jq -c '{reimport: .data.counts}' "$OUT/$p/reimport.json"
  jq -e '.data.counts.applied == 0 and .data.counts.invalid == 0 and .data.counts.conflict == 0' "$OUT/$p/reimport.json" >/dev/null || failures=$((failures+1))
  # title casing check: compare source titles to stored titles
  R --json list --limit 1000 > "$OUT/$p/list.json"
  python3 - "$bib" "$OUT/$p/list.json" <<'PY'
import re,json,sys
src=open(sys.argv[1]).read(); items=json.load(open(sys.argv[2]))['data']['items']
st={}
for m in re.finditer(r'@\w+\{([^,]+),(.*?)\n\}',src,re.S):
    t=re.search(r'\n\s*title\s*=\s*[{"](.*?)[}"],?\n',m.group(2),re.S)
    if t: st[m.group(1).strip()]=re.sub(r'[{}]','',t.group(1)).replace('\n',' ')
diffs=[]
for it in items:
    k=it.get('citation_key'); s=st.get(k); c=it.get('metadata', {}).get('title')
    if s and c and s!=c: diffs.append((k,s[:70],c[:70]))
print(f"  titles changed by normalization: {len(diffs)} of {len(items)}")
for d in diffs[:6]: print("   ",d[0],"|",d[1],"->",d[2])
PY
  # every source: show must work
  fails=0; while IFS= read -r k; do R show "$k" >/dev/null 2>&1 || { fails=$((fails+1)); log "[$p] show failed for $k"; }; done < <(jq -r '.data.items[].citation_key' "$OUT/$p/list.json"); echo "  show failures: $fails"
  # project + export dry run against the real (copied) file
  R project create "$p" >/dev/null; while IFS= read -r k; do R project cite "$p" "$k" >/dev/null; done < <(jq -r '.data.items[].citation_key' "$OUT/$p/list.json")
  R --json export --project "$p" --output "$OUT/$p/exported.bib" --dry-run > "$OUT/$p/export-dry.json" 2>&1
  jq -c '{status, errors: [.errors[].code] | unique, warnings: ([.warnings[].code] | group_by(.) | map("\(.[0]) x\(length)"))}' "$OUT/$p/export-dry.json"
  jq -r '.data.report.entries[]? | select(.class=="blocked" or .class=="unknown") | "  \(.class) \(.citation_key): \(.reason // .code)"' "$OUT/$p/export-dry.json" | head -8
  # real export to a new file, then render through each declared consumer
  cp "$bib" "$OUT/$p/original.bib"
  R --json export --project "$p" --output "$OUT/$p/exported.bib" > "$OUT/$p/export.json" 2>&1; jq -c '{export: .status, count: .data.count, warnings: [.warnings[].code]|group_by(.)|map("\(.[0]) x\(length)"), errors: [.errors[].code]}' "$OUT/$p/export.json"
  if [ -f "$OUT/$p/exported.bib" ]; then
    for f in original exported; do printf -- '---\nnocite: "@*"\n---\n' | pandoc --citeproc --bibliography "$OUT/$p/$f.bib" -t plain 2> "$OUT/$p/$f.pandoc.err" > "$OUT/$p/$f.pandoc.txt"; done
    echo "  pandoc render diff (original vs exported): $(diff "$OUT/$p/original.pandoc.txt" "$OUT/$p/exported.pandoc.txt" | grep -c '^[<>]') lines; pandoc warnings: $(wc -l < "$OUT/$p/exported.pandoc.err")"
    python3 "$T/compare.py" "$OUT/$p" || failures=$((failures+1))
  else
    failures=$((failures+1))
  fi
done
echo; echo "===== agent CSL input"; home csl
R add --format csljson --input "$T/inputs/attention.json" 2>&1 | head -3
echo "===== library-wide BBT export (562, BibLaTeX dialect)"; home library
R --json import --format bib --input "$T/inputs/zotero-bbt-export.bib" --origin zotero > "$OUT/library/import.json" 2>"$OUT/library/import.err"; echo "exit=$?"
jq -c '{status, counts: .data.counts, errors: [.errors[].code]|unique}' "$OUT/library/import.json" 2>/dev/null || head -3 "$OUT/library/import.err"
jq -r '[.data.entries[]? | .limitations[]? | .field] | group_by(.) | map("\(.[0]) x\(length)") | .[]' "$OUT/library/import.json" 2>/dev/null | sed 's/^/  limitation: /'
jq -r '[.data.entries[]? | select(.status=="invalid" or .status=="conflict") | "\(.status) \(.citation_key): \(.reason // (.conflicts[0].code? // ""))"] | .[]' "$OUT/library/import.json" 2>/dev/null | head -10 | sed 's/^/  /'
# Whole-library reporting: retained facts are JSON info, not human warnings.
R project create library >/dev/null
R project cite library --from-import zotero >/dev/null
R --json export --project library --output "$OUT/library/exported.bib" > "$OUT/library/export.json"
R export --project library --output "$OUT/library/exported.bib" > "$OUT/library/export.txt"
echo "===== files"; 
key=$(R --json list | jq -r '.data.items[0].citation_key'); cp "$T/downloads/00265218.pdf" "$OUT/library/dl.pdf"
R resource add "$key" --path "$OUT/library/dl.pdf" --copy; ls "$OUT/library/lib/Unfiled" 2>/dev/null
R resource add "$key" --path "$OUT/library/dl.pdf" --copy --keep-name; ls "$OUT/library/lib/Unfiled" 2>/dev/null
R open --help | head -6
echo "===== search"; R search "workflow" | head -5; R search "köster"; R search "koster" | head -2
echo "===== backup/restore"; R backup --output "$OUT/library/bk" | head -1

uv run --project "$REPO" --locked python "$T/check_counts.py" "$T" || failures=$((failures+1))
echo "Trial failures: $failures"
exit "$failures"
