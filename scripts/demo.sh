#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$BASH_SOURCE")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SMOKE=0
KEEP=0
PAUSE=0
CHECKS=0
[[ -t 0 && -t 1 ]] && PAUSE=1

usage() {
  cat <<'HELP'
Usage: scripts/demo.sh [--smoke] [--no-pause] [--keep]

Narrated end-to-end test of refs US1 and US2 using synthetic data.
  --smoke      Print a compact pass or fail and clean temporary data.
  --no-pause   Never wait between sections.
  --keep       Keep the temporary directory for inspection, even in smoke mode.
  -h, --help   Show this help without running commands.
HELP
}
while (($#)); do
  case "$1" in
    --smoke) SMOKE=1; PAUSE=0 ;;
    --no-pause) PAUSE=0 ;;
    --keep) KEEP=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'error: unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
  shift
done

section() { if (( ! SMOKE )); then printf '\n== %s ==\n' "$1"; fi; }
explain() { if (( ! SMOKE )); then printf '%s\n' "$1"; fi; }
show_command() {
  if (( ! SMOKE )); then printf '$ refs --json'; printf ' %q' "$@"; printf '\n'; fi
}
pause_demo() { if (( PAUSE )); then read -r -p 'Press Enter to continue... ' _ || true; fi; }
pass() { CHECKS=$((CHECKS + 1)); if (( ! SMOKE )); then printf 'PASS %s\n' "$1"; fi; }
fail() { printf 'FAIL refs demo: %s\n' "$1" >&2; exit 1; }
assert_jq() {
  jq -e "$1" "$2" >/dev/null || fail "$3"
  pass "$3"
}
command -v jq >/dev/null || fail 'jq must be installed'
REFS_BIN="$REPO_ROOT/.venv/bin/refs"
[[ -x "$REFS_BIN" ]] || fail 'Run uv sync --locked first'
DEMO_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/refs-demo.XXXXXX")"
cleanup() {
  if (( KEEP )); then printf 'Demo retained: %s\n' "$DEMO_ROOT";
  else rm -rf -- "$DEMO_ROOT"; fi
}
trap cleanup EXIT
export REFS_CONFIG="$DEMO_ROOT/config.toml" REFS_CATALOG="$DEMO_ROOT/cat"
cd "$REPO_ROOT"
LAST=""
run() {
  local expected="$1" name="$2" status=0
  shift 2
  LAST="$DEMO_ROOT/$name.result.json"
  show_command "$@"
  "$REFS_BIN" --json "$@" >"$LAST" 2>"$DEMO_ROOT/$name.stderr" || status=$?
  if [[ "$status" != "$expected" ]]; then
    cat "$LAST" "$DEMO_ROOT/$name.stderr" >&2
    fail "$name exited $status, expected $expected"
  fi
  jq -e '.schema_version == "1.0"' "$LAST" >/dev/null || fail "$name result envelope"
  if (( ! SMOKE )); then jq -M '.' "$LAST"; fi
  pass "$name exit $expected"
}

section 'US1: Capture, correct and retrieve sources'
explain 'Every command uses a fresh temporary catalog. The input is synthetic.'
run 0 init init --library-root "$DEMO_ROOT/lib"
run 0 paths paths
assert_jq '.data.catalog.origin == "REFS_CATALOG"' "$LAST" 'explicit catalog selection'
run 0 schema schema source-create
assert_jq '.data.type == "object"' "$LAST" 'offline schema'
run 0 preview add --format refs --input tests/fixtures/reference.json --dry-run
assert_jq '.data.dry_run == true' "$LAST" 'capture preview'
run 0 empty list
assert_jq '.data.total == 0' "$LAST" 'preview created no source'
run 0 capture add --format refs --input tests/fixtures/reference.json
assert_jq '.data.outcome == "created" and .data.revision == 1' "$LAST" 'source created'
KEY="$(jq -r '.data.citation_key' "$LAST")"
SOURCE_ID="$(jq -r '.data.id' "$LAST")"
run 0 repeat add --format refs --input tests/fixtures/reference.json
assert_jq '.data.outcome == "already_present"' "$LAST" 'repeat identified explicitly'
run 0 correct update "$KEY" --if-revision 1 --set 'metadata.volume="13"'
assert_jq '.data.revision == 2 and .data.metadata.volume == "13"' "$LAST" 'correction persisted'
run 3 stale update "$KEY" --if-revision 1 --set 'metadata.volume="14"'
assert_jq '.errors[0].code == "stale_revision"' "$LAST" 'stale revision refused'
run 0 show show "$SOURCE_ID"
assert_jq '.data.originals[0].byte_length > 0 and .data.revision == 2' "$LAST" 'original evidence retained'
run 0 search search Python
assert_jq '.data.total == 1 and (.data.items[0].matches | length) > 0' "$LAST" 'search explains matches'
run 0 rekey-preview key set "$KEY" --key proposed-key --if-revision 2
assert_jq '.data.dry_run == true' "$LAST" 'rekey previews by default'
run 0 remove remove "$KEY" --if-revision 2 --execute
run 0 hidden list
assert_jq '.data.total == 0' "$LAST" 'removed source hidden'
run 0 reactivate reactivate "$KEY" --if-revision 3 --execute
assert_jq '.data.state == "active" and .data.revision == 4' "$LAST" 'same source reactivated'
cat >"$DEMO_ROOT/book.json" <<'JSON'
{"id":"external-book","type":"book","title":"Synthetic Research","language":"en","author":[{"family":"Jones","given":"Bea"}],"issued":{"date-parts":[[2023]]},"publisher":"Example Press","edition":2}
JSON
run 0 csl add --format csljson --input "$DEMO_ROOT/book.json"
assert_jq '.data.id != "external-book" and .data.metadata.edition == 2' "$LAST" 'CSL captured without stealing refs identity'
BOOK_KEY="$(jq -r '.data.citation_key' "$LAST")"
pause_demo

section 'US2: Select citations and publish a bibliography'
explain 'Only an explicit export writes bibliography bytes. Outside edits remain untouched.'
run 0 project project create demo
run 0 cite project cite demo "$KEY"
BIB="$DEMO_ROOT/references.bib"
[[ ! -e "$BIB" ]] || fail 'capture or citation wrote a bibliography'
run 0 export export --project demo --output "$BIB"
assert_jq '.data.count == 1' "$LAST" 'one selected citation exported'
cp "$BIB" "$DEMO_ROOT/first.bib"
run 0 repeat-export export --project demo --output "$BIB"
cmp "$BIB" "$DEMO_ROOT/first.bib" || fail 'repeat export changed bytes'
pass 'deterministic bibliography bytes'
printf '\n%% Outside edit\n' >>"$BIB"
cp "$BIB" "$DEMO_ROOT/edited.bib"
run 3 outside-edit export --project demo --output "$BIB"
assert_jq '.errors[0].code == "outside_edit"' "$LAST" 'outside edit refused'
cmp "$BIB" "$DEMO_ROOT/edited.bib" || fail 'outside edit was overwritten'
pass 'outside bytes preserved'
run 0 inspect-project project show demo
assert_jq '.data.sources | length == 1' "$LAST" 'project shows its cited sources'
run 0 cite-book project cite demo "$BOOK_KEY"
run 0 uncite-book project uncite demo "$BOOK_KEY"
run 0 projects project show
assert_jq '.data.items | length == 1' "$LAST" 'project listing'
cat >"$DEMO_ROOT/web.json" <<'JSON'
{"schema_version":"1.0","citation_key":"web-example","metadata":{"type":"webpage","title":"Synthetic Website","language":"en","URL":"https://example.org/demo"}}
JSON
run 0 web add --format refs --input "$DEMO_ROOT/web.json"
run 0 cite-web project cite demo web-example
run 0 warned-export export --project demo --output "$DEMO_ROOT/warned.bib"
assert_jq 'any(.warnings[]; .details.class == "documented_fallback")' "$LAST" 'documented fallback warns'
run 0 uncertain update web-example --if-revision 1 --set 'metadata.issued={"literal":"Uncertain Date"}'
cp "$DEMO_ROOT/warned.bib" "$DEMO_ROOT/before-block.bib"
run 3 blocked-export export --project demo --output "$DEMO_ROOT/warned.bib"
assert_jq 'any(.errors[0].details.entries[]; .code == "issued_date_lost_or_changed")' "$LAST" 'meaning-changing loss blocks'
cmp "$DEMO_ROOT/warned.bib" "$DEMO_ROOT/before-block.bib" || fail 'blocked export changed bytes'
pass 'blocked export preserved the existing bibliography'
pause_demo
printf 'PASS refs demo: %s checks (US1, US2)\n' "$CHECKS"
