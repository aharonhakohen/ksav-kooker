# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Word (.docx) Exporter
Exports transcribed and edited Hebrew notes to Microsoft Word
with full Right-to-Left (RTL) typography, David font, and proper margins.
"""

import os
from typing import List, Dict, Any, Optional
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def set_rtl_paragraph(p):
    """Sets paragraph direction to Right-to-Left (Bidi)."""
    pPr = p._p.get_or_add_pPr()
    bidi = pPr.find(qn('w:bidi'))
    if bidi is None:
        bidi = OxmlElement('w:bidi')
        pPr.append(bidi)
    bidi.set(qn('w:val'), '1')

def add_hebrew_run(p, text, font_name="David", font_size=12, bold=False, italic=False, color=None):
    """Adds a run with explicit Hebrew RTL font mappings."""
    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
        
    rPr = run._r.get_or_add_rPr()
    rtl = rPr.find(qn('w:rtl'))
    if rtl is None:
        rtl = OxmlElement('w:rtl')
        rPr.append(rtl)
    rtl.set(qn('w:val'), '1')
    
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    return run

def add_hebrew_paragraph(doc, text="", align=WD_ALIGN_PARAGRAPH.RIGHT, font_size=12, bold=False, italic=False, space_after=6, space_before=0, font_name="David"):
    """Adds a paragraph configured for Hebrew text."""
    p = doc.add_paragraph()
    set_rtl_paragraph(p)
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = 1.2
    if text:
        add_hebrew_run(p, text, font_name=font_name, font_size=font_size, bold=bold, italic=italic)
    return p

def export_notes_to_docx(
    pages: List[Dict[str, Any]],
    output_path: str,
    document_title: str = "שיעורי תורה וחידושים",
    document_subtitle: str = "",
    author_name: str = "",
    font_name: str = "David"
) -> str:
    """
    Exports a list of page dicts to a formatted .docx document.
    Each page dict can contain:
      - 'page_num': int
      - 'title': str (optional header, e.g. 'שיעור א'')
      - 'date': str (optional, e.g. 'בס"ד | יום ג' פרשת נח')
      - 'text': str (the transcribed / edited text)
    """
    doc = docx.Document()

    # Set 1-inch margins on all sections & set section direction to RTL
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
        sectPr = section._sectPr
        bidi = sectPr.find(qn('w:bidi'))
        if bidi is None:
            bidi = OxmlElement('w:bidi')
            sectPr.append(bidi)
        bidi.set(qn('w:val'), '1')

    # Main Document Header
    if document_title:
        add_hebrew_paragraph(doc, document_title, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=20, bold=True, space_after=4, space_before=12, font_name=font_name)
    if document_subtitle:
        add_hebrew_paragraph(doc, document_subtitle, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=14, bold=True, space_after=4, space_before=0, font_name=font_name)
    if author_name:
        add_hebrew_paragraph(doc, author_name, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=12, italic=True, space_after=14, space_before=0, font_name=font_name)
    
    if document_title or document_subtitle:
        add_hebrew_paragraph(doc, "___________________________________________________________", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=10, space_after=18, space_before=0)

    # Pages content
    for i, page_data in enumerate(pages):
        if i > 0:
            doc.add_page_break()

        page_num = page_data.get("page_num", i + 1)
        title = page_data.get("title", f"עמוד {page_num}")
        date_str = page_data.get("date", "")
        text = page_data.get("text", "")

        # Page Header
        if title:
            add_hebrew_paragraph(doc, title, align=WD_ALIGN_PARAGRAPH.RIGHT, font_size=16, bold=True, space_after=4, space_before=6, font_name=font_name)
        if date_str:
            add_hebrew_paragraph(doc, date_str, align=WD_ALIGN_PARAGRAPH.RIGHT, font_size=11, bold=True, space_after=10, space_before=0, font_name=font_name)
        
        add_hebrew_paragraph(doc, f"[דף {page_num}]", align=WD_ALIGN_PARAGRAPH.LEFT, font_size=9, bold=False, space_after=6, space_before=0, font_name=font_name)

        # Paragraphs
        paragraphs = text.split("\n")
        for para in paragraphs:
            para = para.strip()
            if para:
                add_hebrew_paragraph(doc, para, align=WD_ALIGN_PARAGRAPH.JUSTIFY, font_size=12, bold=False, space_after=8, space_before=0, font_name=font_name)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path
