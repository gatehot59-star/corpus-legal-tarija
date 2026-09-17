"""B04: extract exactly one LexiVox legal container, preserving its HTML.

No phrase blacklist, network calls, legal-status inference or original edits.
Plain text is a search derivative; legal_html preserves lists/table attributes.
Unsupported or ambiguous legal containers are rejected, never guessed.
"""
from __future__ import annotations
import argparse
import hashlib
import os
import tempfile
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Sequence

MAX_BYTES = 16 * 1024 * 1024
MAX_NODES = 200000
MAX_DEPTH = 128
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
BLOCK = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'ol', 'ul', 'dl', 'dt', 'dd', 'table', 'tr', 'caption', 'blockquote', 'pre'}
ALLOWED = BLOCK | {'a', 'strong', 'b', 'i', 'em', 'u', 's', 'span', 'sup', 'sub', 'small', 'font', 'center', 'br', 'hr', 'thead', 'tbody', 'tfoot', 'td', 'th', 'colgroup', 'col'}


class ExtractionError(ValueError):
    """The source cannot be reduced without an explicit review."""


def normalized(value: str) -> str:
    """Collapse Unicode whitespace only, without changing legal characters."""
    return ' '.join(value.split())


class LegalParser(HTMLParser):
    """Strictly consume the observed normTxtId boundary, preserving source span."""
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.lines = [0]
        for match in re.finditer('\n', source):
            self.lines.append(match.end())
        self.stack: list[str] = []
        # Ancestors outside the selected body still determine its context.
        self.ancestors: list[tuple[str, dict[str, str | None], bool]] = []
        self.targets = 0
        self.start = self.end = None
        self.text: list[str] = []
        self.title: list[str] = []
        self.title_count = 0
        self.nodes = 0
        self.structure: list[dict] = []

    @staticmethod
    def hidden_context(attributes: dict[str, str | None]) -> bool:
        """Recognize explicit hidden/inactive attributes, not computed CSS."""
        return ("hidden" in attributes or "inert" in attributes
                or (attributes.get("aria-hidden") or "").strip().lower() == "true"
                or re.search(r"display\s*:\s*none|visibility\s*:\s*hidden",
                             attributes.get("style") or "", re.I) is not None)

    def source_offset(self) -> int:
        """Return the source character offset of the current parser event."""
        row, column = self.getpos()
        return self.lines[row - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Reject duplicate containers and unsupported legal content."""
        keys = [k for k, _ in attrs]
        if any(k == 'id' and v == 'normTxtId' for k, v in attrs):
            self.targets += 1
            if self.targets != 1 or self.stack or tag != 'div':
                raise ExtractionError('ambiguous legal container')
            if len(keys) != len(set(keys)):
                raise ExtractionError('duplicate container attributes')
            attributes = dict(attrs)
            if self.hidden_context(attributes):
                raise ExtractionError('hidden legal container requires review')
            for ancestor_tag, ancestor_attrs, duplicate in self.ancestors:
                if (duplicate or ancestor_tag in {"template", "noscript", "textarea", "title"}
                        or self.hidden_context(ancestor_attrs)):
                    raise ExtractionError("hidden or inactive ancestor requires review")
            self.start = self.source_offset() + len(self.get_starttag_text())
            self.stack.append(tag)
            return
        if not self.stack:
            if tag not in VOID:
                if len(self.ancestors) >= MAX_DEPTH:
                    raise ExtractionError("ancestor depth limit exceeded")
                self.ancestors.append((tag, dict(attrs), len(keys) != len(set(keys))))
            return
        self.nodes += 1
        if self.nodes > MAX_NODES or len(self.stack) >= MAX_DEPTH:
            raise ExtractionError('legal tree limit exceeded')
        if tag not in ALLOWED or len(keys) != len(set(keys)):
            raise ExtractionError('unsupported element or duplicate attributes in legal body')
        attributes = dict(attrs)
        if self.hidden_context(attributes):
            raise ExtractionError('hidden legal content requires review')
        if tag in BLOCK or tag == 'br':
            self.text.append('\n')
        if tag in {'td', 'th'}:
            self.text.append('\t')
        if tag == 'h1':
            self.title_count += 1
        if tag in {'table', 'tr', 'td', 'th', 'ol', 'ul', 'li', 'sup', 'sub'}:
            self.structure.append({'tag': tag, 'attrs': attrs})
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle explicit self-closing markup without inventing end tags."""
        if not self.stack and tag not in VOID:
            raise ExtractionError('ambiguous self-closing ancestor requires review')
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        """Close only a balanced legal subtree; no browser-style guessing."""
        if not self.stack:
            # Reject ambiguity rather than recovering by deleting open context.
            # A crossed close must never erase a hidden or inactive ancestor.
            if tag in VOID or not self.ancestors or self.ancestors[-1][0] != tag:
                raise ExtractionError("unmatched or crossed outer closing tag")
            self.ancestors.pop()
            return
        if tag in VOID or self.stack[-1] != tag:
            raise ExtractionError('unbalanced legal markup')
        self.stack.pop()
        if not self.stack:
            self.end = self.source_offset()
            return
        if tag in BLOCK:
            self.text.append('\n')

    def handle_data(self, data: str) -> None:
        """Keep every text node inside the selected subtree, including anchor text."""
        if self.stack:
            self.text.append(data)
            if 'h1' in self.stack:
                self.title.append(data)


def extract(raw: bytes, expected_sha256: str, expected_title: str) -> dict:
    """Return a reviewed-boundary candidate, or reject without writing anything.

    expected_sha256 covers raw HTML bytes. Title is exact modulo whitespace.
    legal_html is the exact original inner span, NOT sanitized browser content.
    Never render it as trusted HTML: serve escaped or use a separate sanitizer.
    """
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ExtractionError('invalid HTML size/type')
    if not isinstance(expected_sha256, str) or re.fullmatch('[0-9a-f]{64}', expected_sha256) is None:
        raise ExtractionError('full original digest required')
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ExtractionError('original digest mismatch')
    if not isinstance(expected_title, str) or not normalized(expected_title):
        raise ExtractionError('explicit title required')
    try:
        source = raw.decode('utf-8', errors='strict')
    except UnicodeDecodeError as exc:
        raise ExtractionError('HTML must be UTF-8') from exc
    parser = LegalParser(source)
    parser.feed(source); parser.close()
    if parser.targets != 1 or parser.stack or parser.start is None or parser.end is None:
        raise ExtractionError('missing or unclosed legal body')
    title = normalized(''.join(parser.title))
    if parser.title_count != 1 or title != normalized(expected_title):
        raise ExtractionError('legal title mismatch or ambiguity')
    fragment = source[parser.start:parser.end]
    lines = []
    for line in ''.join(parser.text).split('\n'):
        # Tabs remain cell boundaries. Inline words are never split or rewritten.
        cells = [re.sub(r'[^\S\t]+', ' ', c).strip() for c in line.split('\t')]
        line = '\t'.join(cells).strip(' ')
        if line.strip():
            lines.append(line)
    text = '\n'.join(lines) + '\n'
    if not normalized(text.replace(title, '', 1)):
        raise ExtractionError('empty legal body')
    return {'profile': 'lexivox-legal-body-v1', 'source_sha256': digest,
            'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'legal_html_sha256': hashlib.sha256(fragment.encode()).hexdigest(),
            'source_char_span': [parser.start, parser.end], 'title': title,
            'text': text, 'legal_html': fragment, 'structure': parser.structure,
            'authority': 'secondary', 'legal_validity': 'NOT_MEASURED',
            'safe_to_render_html': False,
            'plain_text_limit': 'Search derivative; list numbering/CSS and table spans require legal_html or source view.'}


def main(argv: Sequence[str] | None = None) -> int:
    """Read bounded local HTML and exclusively write a NEW JSON candidate."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--sha256', required=True)
    ap.add_argument('--title', required=True)
    args = ap.parse_args(argv)
    try:
        with args.input.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        result = extract(raw, args.sha256, args.title)
        encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
        # Stage a complete file, then link exclusively. No partial final output.
        with tempfile.TemporaryDirectory(prefix='.legal-html-', dir=args.output.parent) as td:
            stage = Path(td) / 'candidate.json'
            with stage.open('xb') as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(stage, 0o600)
            os.link(stage, args.output)
    except (ValueError, OSError) as exc:
        print(json.dumps({'ok': False, 'error': type(exc).__name__}))
        return 2
    print(json.dumps({'ok': True, 'source_sha256': result['source_sha256'],
                      'text_sha256': result['text_sha256'], 'characters': len(result['text'])}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
