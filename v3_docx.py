#!/usr/bin/env python3
"""
V3. Render the manuscript as a Word file in IEEE Transactions layout.

TTS does not accept LaTeX, so the submission artefact is .docx. This module
owns the layout; the text lives in manuscript.txt and the tables are built
from the result files, so no number is transcribed by hand.

Layout follows IEEE's Transactions metrics: US Letter, 0.75 in top margin,
1.0 in bottom, 0.625 in sides, two columns of 3.5 in with a 0.2 in gutter,
10 pt Times New Roman on single spacing, 8 pt in tables and captions.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path("/home/claude/tts")
FIGS = ROOT / "figs"
OUT = ROOT / "out"
OUT.mkdir(parents=True, exist_ok=True)

COL_W = Inches(3.5)
SERIF = "Times New Roman"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


# --------------------------------------------------------------- low level
def _cols(section, num: int, space_twips: int = 288) -> None:
    """Set the column count on a section (python-docx has no API for this)."""
    sectPr = section._sectPr
    for old in sectPr.findall(qn("w:cols")):
        sectPr.remove(old)
    cols = OxmlElement("w:cols")
    cols.set(qn("w:num"), str(num))
    cols.set(qn("w:space"), str(space_twips))
    cols.set(qn("w:equalWidth"), "1")
    sectPr.append(cols)


def _margins(section) -> None:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(0.625)
    section.right_margin = Inches(0.625)


def _runs(par, text: str, size: float, *, bold=False, italic=False,
          caps=False, color=None):
    """Write text into a paragraph.

    Markers: **bold**, *italic*, _{sub}, ^{sup}. Greek letters and operators
    are written as literal Unicode in the source text.
    """
    def emit(piece, b, i, sub=False, sup=False):
        if not piece:
            return
        r = par.add_run(piece)
        r.font.name = SERIF
        r.font.size = Pt(size)
        r.bold = b
        r.italic = i
        r.font.small_caps = caps
        r.font.subscript = sub
        r.font.superscript = sup
        if color:
            r.font.color.rgb = color
        rpr = r._element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.append(rf)
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            rf.set(qn(a), SERIF)

    for piece in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not piece:
            continue
        b, i = bold, italic
        if piece.startswith("**"):
            piece, b = piece[2:-2], True
        elif piece.startswith("*"):
            piece, i = piece[1:-1], True
        for sub_piece in re.split(r"([_^]\{[^}]*\})", piece):
            if not sub_piece:
                continue
            if sub_piece.startswith("_{"):
                emit(sub_piece[2:-1], b, True, sub=True)
            elif sub_piece.startswith("^{"):
                emit(sub_piece[2:-1], b, i, sup=True)
            else:
                emit(sub_piece, b, i)
    return par


def _para(doc, text, size=10.0, *, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
          indent=0.0, before=0, after=0, bold=False, italic=False,
          caps=False, keep=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Inches(indent)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.0
    pf.keep_with_next = keep
    _runs(p, text, size, bold=bold, italic=italic, caps=caps)
    return p


def _borders(cell, *, top=None, bottom=None):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("w:tcBorders")):
        tcPr.remove(old)
    el = OxmlElement("w:tcBorders")
    for side, sz in (("top", top), ("bottom", bottom)):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single" if sz else "nil")
        b.set(qn("w:sz"), str(sz or 0))
        b.set(qn("w:color"), "000000")
        el.append(b)
    tcPr.append(el)


# --------------------------------------------------------------- content
def table(doc, rows, widths, *, size=7.5, rules=(1,)):
    """A booktabs-style table: rule on top, under the header, at the end."""
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tbl = t._tbl
    tblPr = tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        for old in tblPr.findall(qn(tag)):
            tblPr.remove(old)
    w = OxmlElement("w:tblW")
    w.set(qn("w:w"), str(int(sum(widths) * 1440)))
    w.set(qn("w:type"), "dxa")
    tblPr.append(w)
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    for old in tbl.findall(qn("w:tblGrid")):
        tbl.remove(old)
    grid = OxmlElement("w:tblGrid")
    for cw in widths:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(int(cw * 1440)))
        grid.append(gc)
    tbl.insert(1, grid)

    for ri, row in enumerate(rows):
        for ci, cell_text in enumerate(row):
            c = t.cell(ri, ci)
            c.width = Inches(widths[ci])
            c.text = ""
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0.6)
            p.paragraph_format.space_after = Pt(0.6)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = (WD_ALIGN_PARAGRAPH.LEFT if ci == 0
                           else WD_ALIGN_PARAGRAPH.CENTER)
            _runs(p, str(cell_text), size, bold=(ri == 0))
            p.paragraph_format.keep_with_next = ri < len(rows) - 1
            top = 8 if ri == 0 else (4 if ri in rules else None)
            bot = 8 if ri == len(rows) - 1 else None
            _borders(c, top=top, bottom=bot)
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trPr.append(cs)
    return t


def figure(doc, name, caption, label, *, width=3.42):
    png = FIGS / f"{name}.png"
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(png), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cap.paragraph_format.space_after = Pt(8)
    cap.paragraph_format.line_spacing = 1.0
    _runs(cap, f"Fig. {label}. ", 8.0, bold=False)
    _runs(cap, caption, 8.0)


def wide_block(doc, fn):
    """Run *fn* across the full page width, then return to two columns."""
    s = doc.add_section(WD_SECTION.CONTINUOUS)
    _margins(s)
    _cols(s, 1)
    fn(doc)
    s2 = doc.add_section(WD_SECTION.CONTINUOUS)
    _margins(s2)
    _cols(s2, 2)


def equation(doc, body: str, number: str):
    """A centred display equation with a right-aligned number."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4)
    pf.space_after = Pt(4)
    pf.line_spacing = 1.0
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    tabs = p.paragraph_format.tab_stops
    tabs.add_tab_stop(Inches(1.70), WD_TAB_ALIGNMENT.CENTER)
    tabs.add_tab_stop(Inches(3.40), WD_TAB_ALIGNMENT.RIGHT)
    _runs(p, "\t" + body + "\t(" + number + ")", 10, italic=True)
    return p
