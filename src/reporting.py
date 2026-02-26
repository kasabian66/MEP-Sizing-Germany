
from __future__ import annotations
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import pandas as pd
from .sources import SOURCES

def _draw_title(c: canvas.Canvas, title: str, y: float) -> float:
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20*mm, y, title)
    return y - 10*mm

def _draw_paragraph(c: canvas.Canvas, text: str, y: float, size: int=9, leading: int=11) -> float:
    c.setFont("Helvetica", size)
    max_width = 170*mm
    words = text.split()
    line = ""
    for w in words:
        trial = (line + " " + w).strip()
        if c.stringWidth(trial, "Helvetica", size) <= max_width:
            line = trial
        else:
            c.drawString(20*mm, y, line)
            y -= leading
            line = w
    if line:
        c.drawString(20*mm, y, line)
        y -= leading
    return y

def df_to_table(df: pd.DataFrame, max_rows: int = 25) -> Table:
    df = df.copy()
    if len(df) > max_rows:
        df = df.head(max_rows)
    data = [list(df.columns)] + df.astype(str).values.tolist()
    t = Table(data, hAlign="LEFT", colWidths=None)
    style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONT", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ])
    t.setStyle(style)
    return t

def build_pdf(
    filename: str,
    executive: Dict[str, Any],
    tables: List[Dict[str, Any]],
    source_ids: List[str],
):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 20*mm
    y = _draw_title(c, "MEP Pre-sizing — Germany (Streamlit)", y)

    y = _draw_paragraph(c, f"Executive summary:", y, size=11)
    for k,v in executive.items():
        y = _draw_paragraph(c, f"- {k}: {v}", y)

    c.showPage()

    for tinfo in tables:
        df = tinfo["df"]
        title = tinfo.get("title","Table")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20*mm, height-20*mm, title)
        tbl = df_to_table(df)
        w,h = tbl.wrapOn(c, width-40*mm, height-40*mm)
        tbl.drawOn(c, 20*mm, height-30*mm-h)
        c.showPage()

    # Sources
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, height-20*mm, "Sources used (ID / link / access date)")
    y = height-30*mm
    c.setFont("Helvetica", 8)
    for sid in source_ids:
        s = SOURCES.get(sid)
        if not s:
            continue
        line = f"{sid} — {s.url} — {s.accessed}"
        if y < 20*mm:
            c.showPage()
            y = height-20*mm
            c.setFont("Helvetica", 8)
        c.drawString(20*mm, y, line[:140])
        y -= 4*mm

    c.save()
