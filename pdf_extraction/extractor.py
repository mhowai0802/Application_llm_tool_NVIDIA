import re
from PyPDF2 import PdfReader
from pathlib import Path
import pprint

def find_toc_page(reader: PdfReader, keywords=("table of contents","contents")):
    """Scan pages until one contains any keyword. Return (idx,text) or (None,"")."""
    for idx, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        if any(kw in txt.lower() for kw in keywords):
            return idx, txt
    return None, ""


def parse_toc(raw_text: str) -> dict[str, int]:
    """
    Find lines ending in space+digits:
      ^(.+?)\s+(\d+)$
    Return { title.lower(): logical_page_no }.
    """
    # This regex captures titles followed by at least one whitespace and then digits at end of line
    pat = re.compile(r"^(.+?)\s+(\d+)$", re.MULTILINE)
    toc: dict[str, int] = {}

    # For debugging
    matches_found = 0

    for m in pat.finditer(raw_text):
        title = m.group(1).strip().lower()
        pg = int(m.group(2))
        toc[title] = pg
        matches_found += 1

    print(f"Found {matches_found} matches")

    return toc

def build_absolute_toc(toc_page_idx: int, toc: dict[str,int]) -> dict[str,int]:
    """
    Convert logical page numbers to 0-based PDF indices.
    We assume logical pg 1 is at pdf-index = toc_page_idx+1.
    """
    offset = toc_page_idx
    master = {}
    for title, pg in toc.items():
        if toc['definitions'] == 3:
            pg = pg - 2
        master[title] = offset + pg
    return master

def extract_sections(
    pdf_path: str,
    want: list[str]|None = None
) -> dict[str,str|None]:
    """
    Open PDF, locate TOC, parse it, then extract the first page text
    of each section in `want` (case‐insensitive). If want is None,
    extract all TOC entries.
    Returns { section_title: text_or_None }.
    """
    reader = PdfReader(pdf_path)

    toc_page_idx, toc_text = find_toc_page(reader)
    if toc_page_idx is None:
        raise RuntimeError(f"No TOC found in {pdf_path}")
    toc       = parse_toc(toc_text)
    abs_toc   = build_absolute_toc(toc_page_idx, toc)
    pprint.pprint(abs_toc)
    # decide which keys to pull
    keys = [t.lower() for t in want] if want else list(toc.keys())
    out: dict[str,str|None] = {}
    for key in keys:
        if key not in abs_toc:
            out[key] = None
            continue

        idx = abs_toc[key]
        if 0 <= idx < len(reader.pages):
            out[key] = reader.pages[idx].extract_text() or ""
        else:
            out[key] = None
    return out

def batch_extract(
    folder: str|Path,
    want: list[str]|None = None
) -> dict[str, dict[str,str|None]]:
    """
    Walk folder for all .pdf, extract sections, return
      { filename.pdf: { section_title: text|None } }
    """
    from pathlib import Path
    folder = Path(folder)
    results: dict[str, dict[str,str|None]] = {}

    for pdf in sorted(folder.glob("*.pdf")):
        try:
            data = extract_sections(str(pdf), want)
        except Exception as e:
            data = {"__error__": str(e)}
        results[pdf.name] = data
    return results