import sys
from pathlib import Path

def pdf_escape(s: str) -> str:
    return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def make_pdf(lines, out_path: Path):
    # Build a simple uncompressed PDF with one page and a single text stream
    content_lines = []
    # Start text object
    y = 750
    first = True
    for ln in lines:
        if first:
            content_lines.append(f"BT /F1 12 Tf 72 {y} Td ({pdf_escape(ln)}) Tj")
            first = False
        else:
            y -= 14
            content_lines.append(f"0 -14 Td ({pdf_escape(ln)}) Tj")
    content_lines.append("ET")
    content = "\n".join(content_lines).encode('utf-8')

    objects = []

    # Object 1: Catalog
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # Object 2: Pages
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")

    # Object 3: Page
    page_obj = (
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    )
    objects.append(page_obj)

    # Object 4: Font
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    # Object 5: Contents stream
    stream = content
    obj5 = b"5 0 obj\n<< /Length %d >>\nstream\n" % len(stream)
    obj5 += stream + b"\nendstream\nendobj\n"
    objects.append(obj5)

    # Build file
    out = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = []
    for obj in objects:
        offsets.append(len(out))
        out += obj

    xref_pos = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off

    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref_pos)

    out_path.write_bytes(out)

def read_md(md_path: Path):
    lines = []
    with md_path.open('r', encoding='utf-8') as f:
        for raw in f:
            s = raw.rstrip('\n')
            if s.startswith('#'):
                # strip markdown headers but keep content
                s = s.lstrip('#').strip()
            lines.append(s)
    return lines

if __name__ == '__main__':
    md = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('report.md')
    pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('report.pdf')
    if not md.exists():
        print('MD file not found:', md)
        sys.exit(1)
    lines = read_md(md)
    make_pdf(lines, pdf)
    print('WROTE', str(pdf))
