#!/usr/bin/env python3
"""Render a submission draft (Markdown) to PDF: Markdown -> HTML -> headless Chrome.

Usage:
    python3 scripts/render_submission_pdf.py <input.md> <output.pdf>

Why this exists, and why it is this small
-----------------------------------------
The two 공모전 양식 documents are authored as Markdown in
``docs/reference/challenge/submission/drafts/`` and have to exist as PDF. This machine has
no ``pandoc``, no ``wkhtmltopdf`` and no ``weasyprint``; it does have Google Chrome, whose
``--headless --print-to-pdf`` lays out Korean correctly from the system fonts.

So this is a *document renderer*, not a Markdown implementation: it covers exactly the
subset the drafts use — ATX headings, unordered/ordered lists (one level of nesting),
GFM pipe tables, fenced code blocks, blockquotes, horizontal rules, paragraphs, and inline
code / bold / italic / links. Anything outside that subset is rendered as literal text
rather than silently mangled. Standard library only.
"""

from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import sys
import time
import tempfile
from pathlib import Path

PRINT_TIMEOUT = 120.0  # seconds to wait for the PDF to appear and settle

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
)

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", "AppleGothic", sans-serif;
  font-size: 10.2pt; line-height: 1.62; color: #16201c; margin: 0;
  word-break: keep-all; overflow-wrap: break-word;
}
h1 { font-size: 19pt; line-height: 1.3; margin: 0 0 6pt; letter-spacing: -0.01em; }
h2 {
  font-size: 13.5pt; line-height: 1.35; margin: 22pt 0 7pt; padding-bottom: 4pt;
  border-bottom: 1.2pt solid #2b8e6c; break-after: avoid; page-break-after: avoid;
}
h3 { font-size: 11.4pt; margin: 14pt 0 5pt; break-after: avoid; page-break-after: avoid; }
h4 { font-size: 10.4pt; margin: 11pt 0 4pt; color: #33473f; break-after: avoid; page-break-after: avoid; }
p { margin: 0 0 7pt; }
ul, ol { margin: 0 0 8pt; padding-left: 16pt; }
li { margin: 0 0 3pt; }
li > ul, li > ol { margin: 3pt 0 0; }
strong { font-weight: 700; }
code {
  font-family: "SFMono-Regular", "IBM Plex Mono", Menlo, Consolas, monospace;
  font-size: 0.88em; background: #f1f5f3; padding: 0.5pt 2pt; border-radius: 2pt;
}
pre {
  font-family: "SFMono-Regular", "IBM Plex Mono", Menlo, Consolas, monospace;
  font-size: 8pt; line-height: 1.45; background: #f6f8f7; border: 0.5pt solid #d9e2de;
  border-radius: 3pt; padding: 7pt 9pt; margin: 0 0 9pt; white-space: pre-wrap;
  break-inside: avoid; page-break-inside: avoid;
}
pre code { background: none; padding: 0; font-size: inherit; }
blockquote {
  margin: 0 0 8pt; padding: 4pt 0 4pt 10pt; border-left: 2pt solid #cddbd5; color: #33473f;
}
blockquote p:last-child { margin-bottom: 0; }
table {
  border-collapse: collapse; width: 100%; margin: 4pt 0 10pt; font-size: 9.1pt;
}
/* Rows stay whole and the header repeats; the *table* may split, because forcing a long
   table onto one page leaves half a page blank in front of it. */
tr { break-inside: avoid; page-break-inside: avoid; }
thead { display: table-header-group; }
th, td { border: 0.5pt solid #c6d3ce; padding: 4pt 6pt; text-align: left; vertical-align: top; }
th { background: #eef4f1; font-weight: 700; }
hr { border: 0; border-top: 0.5pt solid #cddbd5; margin: 14pt 0; }
a { color: #16201c; text-decoration: underline; }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


# --------------------------------------------------------------------------- inline

_CODE_SENTINEL = "\x00CODE{}\x00"


def _inline(text: str) -> str:
    """Escape, then apply the inline subset. Code spans are protected first."""
    spans: list[str] = []

    def stash(match: re.Match[str]) -> str:
        spans.append(match.group(1))
        return _CODE_SENTINEL.format(len(spans) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?=\S)([^*]+?)(?<=\S)\*(?![\w*])", r"<em>\1</em>", text)
    for index, raw in enumerate(spans):
        text = text.replace(
            _CODE_SENTINEL.format(index),
            "<code>" + html.escape(raw, quote=False) + "</code>",
        )
    return text


# ----------------------------------------------------------------------------- block

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET = re.compile(r"^(\s*)[-*]\s+(.*)$")
ORDERED = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
TABLE_RULE = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")


def _split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def _render_table(lines: list[str]) -> str:
    header = _split_row(lines[0])
    out = ["<table>", "<thead><tr>"]
    out += ["<th>" + _inline(cell) + "</th>" for cell in header]
    out.append("</tr></thead>")
    body = lines[2:]
    if body:
        out.append("<tbody>")
        for row in body:
            cells = _split_row(row)
            cells += [""] * (len(header) - len(cells))
            out.append("<tr>" + "".join("<td>" + _inline(c) + "</td>" for c in cells) + "</tr>")
        out.append("</tbody>")
    out.append("</table>")
    return "\n".join(out)


def _render_list(items: list[tuple[int, str, str]]) -> str:
    """items: (indent, kind, text). One level of nesting is supported."""
    out: list[str] = []
    stack: list[str] = []
    for indent, kind, text in items:
        level = min(indent // 2, 1)
        while len(stack) > level + 1:
            out.append("</li></%s>" % stack.pop())
        if len(stack) == level + 1:
            if stack[-1] == kind:
                out.append("</li>")
            else:
                out.append("</li></%s>" % stack.pop())
                out.append("<%s>" % kind)
                stack.append(kind)
        else:
            out.append("<%s>" % kind)
            stack.append(kind)
        out.append("<li>" + _inline(text))
    while stack:
        out.append("</li></%s>" % stack.pop())
    return "\n".join(out)


def markdown_to_html(source: str) -> str:
    lines = source.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    index = 0
    total = len(lines)

    while index < total:
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            index += 1
            block: list[str] = []
            while index < total and not lines[index].strip().startswith("```"):
                block.append(lines[index])
                index += 1
            index += 1
            out.append("<pre><code>" + html.escape("\n".join(block), quote=False) + "</code></pre>")
            continue

        if re.fullmatch(r"(---+|\*\*\*+|___+)", stripped):
            out.append("<hr>")
            index += 1
            continue

        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            out.append("<h%d>%s</h%d>" % (level, _inline(heading.group(2).strip()), level))
            index += 1
            continue

        if "|" in stripped and index + 1 < total and TABLE_RULE.match(lines[index + 1]):
            table: list[str] = [lines[index], lines[index + 1]]
            index += 2
            while index < total and "|" in lines[index] and lines[index].strip():
                table.append(lines[index])
                index += 1
            out.append(_render_table(table))
            continue

        if stripped.startswith("> "):
            quote: list[str] = []
            while index < total and lines[index].strip().startswith(">"):
                quote.append(lines[index].strip()[1:].lstrip())
                index += 1
            out.append("<blockquote><p>" + _inline(" ".join(quote)) + "</p></blockquote>")
            continue

        if BULLET.match(line) or ORDERED.match(line):
            items: list[tuple[int, str, str]] = []
            while index < total:
                current = lines[index]
                bullet = BULLET.match(current)
                ordered = ORDERED.match(current)
                if bullet:
                    items.append((len(bullet.group(1)), "ul", bullet.group(2)))
                    index += 1
                elif ordered:
                    items.append((len(ordered.group(1)), "ol", ordered.group(3)))
                    index += 1
                elif current.strip() and current.startswith(("  ", "\t")) and items:
                    indent, kind, text = items[-1]
                    items[-1] = (indent, kind, text + " " + current.strip())
                    index += 1
                else:
                    break
            out.append(_render_list(items))
            continue

        paragraph: list[str] = []
        while index < total and lines[index].strip():
            candidate = lines[index]
            if (
                HEADING.match(candidate)
                or BULLET.match(candidate)
                or ORDERED.match(candidate)
                or candidate.strip().startswith(("```", ">"))
                or re.fullmatch(r"(---+|\*\*\*+|___+)", candidate.strip())
            ):
                break
            paragraph.append(candidate.strip())
            index += 1
        if paragraph:
            out.append("<p>" + _inline(" ".join(paragraph)) + "</p>")

    return "\n".join(out)


# ------------------------------------------------------------------------------ pdf


def find_chrome() -> str:
    env = os.environ.get("CHROME_BIN")
    if env and Path(env).exists():
        return env
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    found = shutil.which("google-chrome") or shutil.which("chromium")
    if found:
        return found
    raise SystemExit(
        "No Chrome/Chromium found. Set CHROME_BIN to the browser binary, or install Chrome."
    )


def render(md_path: Path, pdf_path: Path) -> None:
    source = md_path.read_text(encoding="utf-8")
    title = md_path.stem
    for line in source.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    document = HTML_TEMPLATE.format(title=html.escape(title), css=CSS, body=markdown_to_html(source))

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists():
        pdf_path.unlink()

    with tempfile.TemporaryDirectory(prefix="submission-pdf-") as work:
        html_path = Path(work) / (md_path.stem + ".html")
        html_path.write_text(document, encoding="utf-8")
        command = [
            find_chrome(),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            "--no-pdf-header-footer",
            "--disable-background-networking",
            "--virtual-time-budget=4000",
            "--user-data-dir=" + str(Path(work) / "profile"),
            "--print-to-pdf=" + str(pdf_path.resolve()),
            html_path.resolve().as_uri(),
        ]
        # Chrome 152 headless writes the PDF and then **does not exit** on this machine —
        # measured with old and new headless, with and without --virtual-time-budget and
        # --timeout. So: wait for the file to appear and stop growing, then stop the browser
        # ourselves. Waiting on the process instead would hang forever.
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + PRINT_TIMEOUT
        last_size, stable = -1, 0
        while time.monotonic() < deadline:
            if process.poll() is not None:
                break
            size = pdf_path.stat().st_size if pdf_path.exists() else 0
            stable = stable + 1 if size > 0 and size == last_size else 0
            last_size = size
            if stable >= 2:
                break
            time.sleep(0.5)
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=15)

        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            out, err = process.communicate()
            sys.stderr.write((out or "") + (err or ""))
            raise SystemExit("Chrome failed to produce %s" % pdf_path)

    print("%s -> %s (%d bytes)" % (md_path, pdf_path, pdf_path.stat().st_size))


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.stderr.write(__doc__ or "")
        return 2
    md_path = Path(argv[1])
    if not md_path.exists():
        raise SystemExit("No such file: %s" % md_path)
    render(md_path, Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
