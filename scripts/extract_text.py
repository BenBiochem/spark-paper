#!/usr/bin/env python3
"""extract_text.py: robust, dependency-free text extraction for `read-paper`.

The skill must ingest "raw PDFs or Word or anything" without depending on a
system `pandoc` install. This extracts text from the common office and text
formats using ONLY the Python standard library, and falls back to external CLI
tools (pdftotext, antiword, libreoffice, pandoc) only if they happen to exist.

Zero-dependency formats (always work):
  .docx .odt .pptx              -> unzip + parse the OOXML/ODF XML
  .txt .md .markdown .csv .tsv  -> read as-is
  .json .tex .rst .yaml .yml    -> read as-is
  .html .htm                    -> strip tags (html.parser)

Via external tool if present (else a clear message):
  .pdf   -> pdftotext (poppler)   [inside the skill, prefer the native Read tool]
  .doc   -> antiword | catdoc | libreoffice
  .rtf   -> unrtf | libreoffice | pandoc
  other  -> pandoc, if installed

Usage:
  extract_text.py FILE [-o OUT.md]      # OUT defaults to stdout
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

PASSTHROUGH = {".txt", ".md", ".markdown", ".text", ".csv", ".tsv", ".json",
               ".tex", ".rst", ".log", ".yaml", ".yml"}


def _localname(tag):
    """Strip the XML namespace, leaving the local element name."""
    return tag.rsplit("}", 1)[-1]


def _xml_paragraphs(xml_bytes, para_tags):
    """Extract text from OOXML/ODF XML by local element name.

    Each element whose local name is in `para_tags` becomes one paragraph; its
    descendant text runs (local name 't') are concatenated in document order,
    with tab/break elements turned into whitespace. Robust to namespace
    variation across Word/ODF versions because it matches on local names.
    """
    root = ET.fromstring(xml_bytes)
    paras = []
    for el in root.iter():
        if _localname(el.tag) not in para_tags:
            continue
        buf = []
        for node in el.iter():
            ln = _localname(node.tag)
            if ln == "t" and node.text:
                buf.append(node.text)
            elif ln == "tab":
                buf.append("\t")
            elif ln in ("br", "cr"):
                buf.append("\n")
        paras.append("".join(buf))
    return "\n\n".join(paras)


def from_docx(path):
    with zipfile.ZipFile(path) as z:
        return _xml_paragraphs(z.read("word/document.xml"), {"p"})


def from_odt(path):
    with zipfile.ZipFile(path) as z:
        return _xml_paragraphs(z.read("content.xml"), {"p", "h"})


def from_pptx(path):
    out = []
    with zipfile.ZipFile(path) as z:
        slides = sorted(
            n for n in z.namelist()
            if n.startswith("ppt/slides/slide") and n.endswith(".xml")
        )
        for name in slides:
            out.append(_xml_paragraphs(z.read(name), {"p"}))
    return "\n\n".join(out)


class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def from_html(path):
    parser = _Stripper()
    with open(path, encoding="utf-8", errors="replace") as fh:
        parser.feed(fh.read())
    return "".join(parser.parts)


def _try_tools(path, candidates):
    """Run the first available external tool; return its stdout or None.

    `candidates` is a list of (executable, argv-builder) pairs.
    """
    for exe, build_argv in candidates:
        if shutil.which(exe):
            try:
                result = subprocess.run(build_argv(path), capture_output=True,
                                        text=True, timeout=180, check=True)
                if result.stdout.strip():
                    return result.stdout
            except Exception:
                continue
    return None


def from_pdf(path):
    return _try_tools(path, [
        ("pdftotext", lambda p: ["pdftotext", "-layout", p, "-"]),
    ])


def from_doc(path):
    return _try_tools(path, [
        ("antiword", lambda p: ["antiword", p]),
        ("catdoc", lambda p: ["catdoc", p]),
        ("libreoffice", lambda p: ["libreoffice", "--headless", "--cat", p]),
    ])


def from_rtf(path):
    return _try_tools(path, [
        ("unrtf", lambda p: ["unrtf", "--text", p]),
        ("pandoc", lambda p: ["pandoc", "-f", "rtf", "-t", "plain", p]),
    ])


def _office_fallback(path):
    """Last-resort conversion for a zip-based office file the stdlib path
    couldn't open (e.g. a corrupt/recovered or oddly-structured file)."""
    text = _try_tools(path, [
        ("pandoc", lambda p: ["pandoc", "-t", "plain", "--wrap=none", p]),
    ])
    if text is not None:
        return text
    exe = shutil.which("libreoffice") or shutil.which("soffice")
    if exe:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            try:
                subprocess.run([exe, "--headless", "--convert-to", "txt:Text",
                                "--outdir", td, path],
                               capture_output=True, timeout=180, check=True)
                out = os.path.join(
                    td, os.path.splitext(os.path.basename(path))[0] + ".txt")
                if os.path.isfile(out):
                    with open(out, encoding="utf-8", errors="replace") as fh:
                        return fh.read()
            except Exception:
                pass
    return None


def extract(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".docx", ".odt", ".pptx"):
        try:
            if ext == ".docx":
                return from_docx(path)
            if ext == ".odt":
                return from_odt(path)
            return from_pptx(path)
        except (zipfile.BadZipFile, KeyError) as exc:
            # The stdlib path needs a valid zip with the expected parts.
            text = _office_fallback(path)
            if text is not None:
                return text
            with open(path, "rb") as fh:
                head = fh.read(4)
            if not head.startswith(b"PK"):
                sys.exit("%s is not a valid %s file: it lacks the 'PK' zip "
                         "signature (first bytes %r); it is corrupt or "
                         "mislabeled. Re-export it from Word, or read the PDF/"
                         ".md version instead."
                         % (os.path.basename(path), ext, head))
            sys.exit("%s is a zip but is missing expected %s parts (%s). "
                     "Re-export it from the source application."
                     % (os.path.basename(path), ext, exc))
    if ext in (".html", ".htm"):
        return from_html(path)
    if ext in PASSTHROUGH:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    if ext == ".pdf":
        text = from_pdf(path)
        if text is None:
            sys.exit("PDF: no pdftotext found. In the read-paper skill, read "
                     "PDFs directly with the Read tool (native PDF support). "
                     "Or install poppler-utils for a CLI text dump.")
        return text
    if ext == ".doc":
        text = from_doc(path)
        if text is None:
            sys.exit(".doc (legacy Word): install antiword/catdoc/libreoffice, "
                     "or resave as .docx (then this script needs nothing).")
        return text
    if ext == ".rtf":
        text = from_rtf(path)
        if text is None:
            sys.exit(".rtf: install unrtf or pandoc, or resave as .docx/.txt.")
        return text
    # Last resort: let pandoc try anything, if it is installed.
    if shutil.which("pandoc"):
        return subprocess.run(["pandoc", "-t", "gfm", "--wrap=none", path],
                              capture_output=True, text=True, check=True).stdout
    sys.exit("Unsupported extension %r and pandoc is not installed." % ext)


def main():
    ap = argparse.ArgumentParser(
        description="Extract plain text from a document (standard-library first).")
    ap.add_argument("file", help="path to the document")
    ap.add_argument("-o", "--out", help="write to this file instead of stdout")
    args = ap.parse_args()

    if not os.path.isfile(args.file):
        sys.exit("not found: %s" % args.file)

    text = extract(args.file)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"  # tidy blank runs

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s (%d chars, %d words)"
              % (args.out, len(text), len(text.split())))
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
