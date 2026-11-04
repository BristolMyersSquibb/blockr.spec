#!/usr/bin/env python3
"""Puts each sentence of the wiki's pages on a line of its own.

Usage: break-lines.py [--check] [<path> ... | -]

The wiki renders the lines of a paragraph as one paragraph, so a page
looks the same whether its sentences share a line or not, while a diff
shows only the sentences that changed. This script breaks a line after
each sentence that is followed by another, and indents the new line as
the paragraph or list item it continues. It never joins lines, so a line
broken after a clause by hand keeps that break. It leaves code, tables,
headings, HTML and the status line under a page's name alone, and never
breaks inside a code span, a link or an HTML tag.

A path is a page or a folder of pages, and with no path the script takes
every page of the repo it sits in. A path of - reads a page from standard
input and writes it to standard output, as a git filter does. With
--check it changes nothing, but lists each line that holds more than one
sentence, with exit status 1.
"""

import re
import sys
from pathlib import Path

FENCE = re.compile(r" *(`{3,}|~{3,})")
LIST_ITEM = re.compile(r" *(?:[-+*]|\d{1,9}[.)]) {1,4}(?=\S)")
# Lines that are not a paragraph's text: headings, table rows, block quotes,
# thematic breaks and link reference definitions.
OTHER = re.compile(r" {0,3}(?:#{1,6}(?: |$)|>|([-*_])(?: *\1){2,} *$|\[[^\]]+\]:)| *\|")
HTML_BLOCK = re.compile(r" {0,3}<(?:!--|/?[A-Za-z][A-Za-z0-9-]*(?:[ />]|$))")
TAG = re.compile(
    r"<(?:!--.*?--|/?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?|[A-Za-z][A-Za-z0-9.+-]{1,31}:[^\s<>]*)>",
    re.S,
)
# A sentence ends on a full stop, question mark or exclamation mark, which
# closing brackets, quotes and emphasis may follow, and the next one opens
# on a capital, after an opening bracket, quote or emphasis, or on a link or
# a code span.
END = re.compile(r"[.?!][)\"'’”*_]*$")
ABBREVIATION = re.compile(r"(?i)\b(?:e\.g|i\.e|cf|vs|etc|al|approx|incl|resp|viz)\.[)\"'’”*_]*$")
START = re.compile(r"(?:[*_]{1,3}|[\"'“‘(\[])?[A-Z]|`{1,2}[^`]|\[(?!\S*\]:)")
PUNCTUATION = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


def backtick_run(s, i):
    j = i
    while j < len(s) and s[j] == "`":
        j += 1
    return j


def code_span_end(s, i):
    """Where the code span opening at i ends, or None if its backticks are literal."""
    j = backtick_run(s, i)
    k = j
    while k < len(s):
        if s[k] != "`":
            k += 1
            continue
        m = backtick_run(s, k)
        if m - k == j - i:
            return m
        k = m
    return None


def bracket_end(s, i, open_, close):
    """Where the bracketed text opening at i ends, skipping code spans and escapes."""
    depth = 0
    k = i
    while k < len(s):
        c = s[k]
        if c == "\\":
            k += 2
            continue
        if c == "`":
            k = code_span_end(s, k) or backtick_run(s, k)
            continue
        if c == open_:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return k + 1
        k += 1
    return None


def protected(s):
    """The spans of s that no break may fall in: code spans, links and tags."""
    spans = []
    i = 0
    while i < len(s):
        c = s[i]
        end = None
        if c == "\\" and i + 1 < len(s) and s[i + 1] in PUNCTUATION:
            i += 2
            continue
        if c == "`":
            end = code_span_end(s, i)
            if end is None:
                i = backtick_run(s, i)
                continue
        elif c == "<":
            tag = TAG.match(s, i)
            end = tag.end() if tag else None
        elif c == "[":
            end = bracket_end(s, i, "[", "]")
            if end is not None and end < len(s) and s[end] in "([":
                end = bracket_end(s, end, *("()" if s[end] == "(" else "[]")) or end
        if end is None:
            i += 1
        else:
            spans.append((i, end))
            i = end
    return spans


def breaks(s):
    """The runs of spaces in s that separate two sentences, as (start, end)."""
    spans = protected(s)

    def inside(p):
        return any(a <= p < b for a, b in spans)

    out = []
    for run in re.finditer(r" +", s):
        a, b = run.span()
        if inside(a) or b == len(s) or s[b] == "\n":
            continue
        end = END.search(s, max(0, a - 20), a)
        if (end and not inside(end.start()) and not ABBREVIATION.search(s, max(0, a - 20), a)
                and START.match(s, b)):
            out.append((a, b))
    return out


def opens_fence(line):
    """Whether the line opens a fenced code block, rather than a code span."""
    fence = FENCE.match(line)
    return bool(fence) and not (fence[1][0] == "`" and "`" in line[fence.end():])


def paragraphs(lines):
    """Each paragraph's lines, as (line index, where its text starts, indent)."""
    para = []
    fence = None
    html = None
    item = None
    previous = "blank"
    for n, line in enumerate(lines):
        kind = "other"
        if fence:
            closing = FENCE.fullmatch(line.rstrip())
            if closing and closing[1][0] == fence[0] and len(closing[1]) >= len(fence):
                fence = None
        elif html:
            if html == "comment" and "-->" in line or html == "block" and not line.strip():
                html = None
            kind = "blank" if not line.strip() else "other"
        elif not line.strip():
            kind = "blank"
        elif opens_fence(line):
            fence = FENCE.match(line)[1]
        elif HTML_BLOCK.match(line):
            if line.lstrip().startswith("<!--"):
                html = None if "-->" in line else "comment"
            else:
                html = "block"
        elif OTHER.match(line) or (n == 1 and lines[0].startswith("# ")):
            pass
        else:
            lead = len(line) - len(line.lstrip(" "))
            marker = LIST_ITEM.match(line)
            if marker:
                item = marker.end()
                start = indent = item
            elif previous == "para" or (item is not None and lead >= item):
                start = indent = lead
            elif lead >= 4:
                start = None
            else:
                item = None
                start = indent = lead
            if start is not None:
                if marker or previous != "para":
                    if para:
                        yield para
                    para = []
                para.append((n, start, indent))
                kind = "para"
        if kind != "para" and para:
            yield para
            para = []
        if kind == "blank" or kind == "para":
            previous = kind
        else:
            previous = "other"
            if not line.startswith(" "):
                item = None
    if para:
        yield para


def break_lines(text):
    """The text with its sentences on lines of their own, and the lines that needed it."""
    lines = text.split("\n")
    out = {}
    for para in paragraphs(lines):
        s = "\n".join(lines[n][start:] for n, start, _ in para)
        cuts = breaks(s)
        if not cuts:
            continue
        offset = 0
        for n, start, indent in para:
            line = lines[n][start:]
            pieces, last = [], 0
            for a, b in cuts:
                if offset <= a < offset + len(line):
                    pieces.append(line[last:a - offset])
                    last = b - offset
            if pieces:
                pieces.append(line[last:])
                out[n] = [lines[n][:start] + pieces[0]] + [" " * indent + p for p in pieces[1:]]
            offset += len(line) + 1
    new = []
    for n, line in enumerate(lines):
        new.extend(out.get(n, [line]))
    return "\n".join(new), sorted(out)


def pages(paths):
    for path in paths:
        if path.is_dir():
            yield from sorted(p for p in path.rglob("*.md") if ".git" not in p.parts)
        else:
            yield path


def report(where, changed):
    for n in changed:
        print(f"{where}:{n + 1}: holds more than one sentence", file=sys.stderr)


def main(argv):
    args = argv[1:]
    check = "--check" in args
    paths = [a for a in args if a != "--check"]
    if any(a.startswith("-") and a != "-" for a in paths) or "-" in paths and len(paths) > 1:
        sys.exit(__doc__)
    if paths == ["-"]:
        new, changed = break_lines(sys.stdin.read())
        if check:
            report("-", changed)
        else:
            sys.stdout.write(new)
        return 1 if check and changed else 0
    found = False
    for path in pages([Path(p) for p in paths] or [Path(__file__).resolve().parent.parent]):
        new, changed = break_lines(path.read_text())
        if not changed:
            continue
        found = True
        if check:
            report(path, changed)
        else:
            path.write_text(new)
            print(f"wrote {path}")
    return 1 if check and found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
