#!/bin/bash
# usage: sidebyside.sh <dir> <basename> <routes...>   (renders each key separately per route and style)
cd "$1"; base="$2"; shift 2; routes="$@"
keys=$(grep -o '^@[a-z]*{[^,]*' $base.bib | sed 's/.*{//')
for st in apa chicago-author-date; do
  echo "################ $st"
  for k in $keys; do
    echo "== $k"
    for route in $routes; do
      printf -- '---\nnocite: "@%s"\n---\n' "$k" > one.md
      printf "  %-7s" "$route"
      pandoc one.md --citeproc --bibliography $base.$route --csl ../../csl/$st.csl -t plain --wrap=none 2>&1 | grep -v '^$' | tr '\n' ' '
      echo
    done
  done
done
