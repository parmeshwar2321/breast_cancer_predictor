from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sys

def md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f.readlines()]

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('h1', parent=styles['Heading1'], fontSize=18, spaceAfter=12)
    h2 = ParagraphStyle('h2', parent=styles['Heading2'], fontSize=14, spaceAfter=8)
    normal = styles['BodyText']

    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=72)
    story = []

    for line in lines:
        if line.startswith('Title:'):
            title = line.split(':',1)[1].strip()
            story.append(Paragraph(title, h1))
            continue
        if line.startswith('Author:'):
            story.append(Paragraph(f"Author: {line.split(':',1)[1].strip()}", normal))
            story.append(Spacer(1, 12))
            continue
        if line.startswith('Date:'):
            story.append(Paragraph(f"Date: {line.split(':',1)[1].strip()}", normal))
            story.append(Spacer(1, 12))
            continue
        if line.startswith('## '):
            story.append(Paragraph(line[3:].strip(), h2))
            continue
        if line.startswith('- '):
            story.append(Paragraph(line[2:].strip(), normal))
            continue
        if line.strip() == '':
            story.append(Spacer(1, 6))
            continue
        # fallback to normal paragraph
        story.append(Paragraph(line, normal))

    doc.build(story)

if __name__ == '__main__':
    md = sys.argv[1] if len(sys.argv)>1 else '../report.md'
    pdf = sys.argv[2] if len(sys.argv)>2 else '../report.pdf'
    md_to_pdf(md, pdf)
