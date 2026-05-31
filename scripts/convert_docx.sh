#!/usr/bin/env bash
# convert_docx.sh: convert a .docx paper to markdown for ingestion.
#
# Part of the `spark-paper` skill. The Read tool reads PDFs natively but not
# .docx; this wraps pandoc to produce a markdown file the skill can then read.
#
# Usage: convert_docx.sh <file.docx> [out.md]
#   out.md defaults to the input path with a .md extension.
set -euo pipefail

src="${1:?usage: convert_docx.sh <file.docx> [out.md]}"
out="${2:-${src%.docx}.md}"

if [ ! -f "$src" ]; then
  echo "input not found: $src" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found. Install it, e.g.:" >&2
  echo "  Debian/Ubuntu: sudo apt install pandoc" >&2
  echo "  macOS:         brew install pandoc" >&2
  exit 1
fi

# GitHub-flavored markdown, no hard line wrapping (keeps prose reflowable).
pandoc -f docx -t gfm --wrap=none "$src" -o "$out"
echo "wrote $out"
