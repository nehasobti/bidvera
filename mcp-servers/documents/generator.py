"""Document generation and PDF conversion engine for documents MCP server."""

from __future__ import annotations

import datetime
import shutil
import subprocess
from pathlib import Path
from typing import Any

import docx
from document_models import BidDocumentInput
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from fpdf import FPDF


def set_cell_background(cell: Any, fill_hex: str) -> None:
    """Sets background shading color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    tc_pr.append(shd)


def build_docx_proposal(bid: BidDocumentInput, output_path: Path) -> Path:
    """Creates a formatted response proposal DOCX document."""
    doc = docx.Document()

    # Configure margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # 1. Cover Page
    p_pre = doc.add_paragraph()
    r_pre = p_pre.add_run("TECHNICAL & COMMERCIAL PROPOSAL RESPONSE")
    r_pre.font.size = Pt(11)
    r_pre.font.bold = True
    r_pre.font.color.rgb = RGBColor(100, 110, 125)

    p_title = doc.add_paragraph()
    r_title = p_title.add_run(bid.title)
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(16, 44, 87)

    p_meta = doc.add_paragraph()
    p_meta.add_run(f"Prepared for: {bid.buyer}\n").bold = True
    p_meta.add_run(f"Tender Reference: {bid.tender_id}\n")
    sub_date = bid.submission_date or datetime.date.today().isoformat()
    p_meta.add_run(f"Submission Date: {sub_date}\n")
    p_meta.add_run(f"Submitted by: {bid.company_name}\n")

    doc.add_page_break()

    # 2. Executive Summary
    doc.add_heading("1. Executive Summary", level=1)
    exec_text = bid.executive_summary or (
        f"Tychon Software is pleased to present our response to {bid.buyer} for '{bid.title}'. "
        "With 12+ years of enterprise experience, over 285 engineers, and certified ISO 27001/9001 governance, "
        "we combine world-class architecture with disciplined delivery to meet all mandatory requirements."
    )
    doc.add_paragraph(exec_text)

    # 3. Technical & Management Sections
    sec_num = 2
    for s in bid.sections:
        title = s.get("title", f"Technical Approach {sec_num}")
        doc.add_heading(f"{sec_num}. {title}", level=1)
        content = s.get("content", "")
        doc.add_paragraph(content)

        citations = s.get("citations", [])
        if citations:
            p_cit = doc.add_paragraph()
            r_cit = p_cit.add_run(f"Authoritative Evidence Citations: {', '.join(citations)}")
            r_cit.font.italic = True
            r_cit.font.size = Pt(9.5)
            r_cit.font.color.rgb = RGBColor(80, 80, 80)

        sec_num += 1

    # 4. Pricing Summary
    if bid.pricing_summary:
        doc.add_heading(f"{sec_num}. Commercial Pricing & Sizing", level=1)
        sec_num += 1
        ps = bid.pricing_summary
        currency = ps.get("currency", "EUR")
        doc.add_paragraph(
            f"Commercial structure based on Tychon Software standard rate cards with target gross margin. "
            f"Total estimated effort: {ps.get('total_hours', 0)} hours ({ps.get('total_days', 0)} person-days)."
        )

        lines = ps.get("lines", [])
        if lines:
            p_table = doc.add_table(rows=len(lines) + 2, cols=5)
            p_table.alignment = WD_TABLE_ALIGNMENT.CENTER

            headers = ["Role", "Days", "Daily Rate", "Hours", f"Total ({currency})"]
            for col_idx, h in enumerate(headers):
                cell = p_table.cell(0, col_idx)
                cell.text = h
                set_cell_background(cell, "102C57")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)

            for idx, line in enumerate(lines, start=1):
                p_table.cell(idx, 0).text = str(line.get("role_title", ""))
                p_table.cell(idx, 1).text = str(line.get("days", 0))
                p_table.cell(idx, 2).text = f"{line.get('daily_rate', 0):,.2f}"
                p_table.cell(idx, 3).text = str(line.get("hours", 0))
                p_table.cell(idx, 4).text = f"{line.get('line_total', 0):,.2f}"

            # Total row
            tot_row = len(lines) + 1
            p_table.cell(tot_row, 0).text = "Grand Total (excl. VAT)"
            p_table.cell(tot_row, 1).text = str(ps.get("total_days", 0))
            p_table.cell(tot_row, 2).text = "-"
            p_table.cell(tot_row, 3).text = str(ps.get("total_hours", 0))
            p_table.cell(tot_row, 4).text = f"{currency} {ps.get('grand_total', 0):,.2f}"
            for c in range(5):
                cell = p_table.cell(tot_row, c)
                set_cell_background(cell, "EAEDED")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.bold = True

    # 5. Compliance Matrix Table
    if bid.compliance_matrix:
        add_compliance_table_to_doc(doc, bid.compliance_matrix, sec_num)

    # 6. Sign-off block
    doc.add_page_break()
    doc.add_heading("Authorized Representative Sign-off", level=2)
    p_sign = doc.add_paragraph()
    p_sign.add_run("For and on behalf of Tychon Software:\n\n\n").bold = True
    p_sign.add_run("_________________________________________\n")
    p_sign.add_run("Authorized Signatory: Dr. Markus Weber / Elena Rostova\n")
    p_sign.add_run(f"Date: {datetime.date.today().isoformat()}\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return output_path


def add_compliance_table_to_doc(
    doc: docx.Document,
    matrix: list[dict[str, Any]],
    section_index: int = 5,
) -> None:
    """Appends compliance matrix table into python-docx Document object."""
    doc.add_heading(f"{section_index}. Compliance Matrix", level=1)
    doc.add_paragraph(
        "The following matrix outlines complete compliance coverage against all mandatory and scored requirements."
    )

    table = doc.add_table(rows=len(matrix) + 1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ["Req ID", "Requirement Description", "Type", "Status", "Response Ref"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        set_cell_background(cell, "102C57")
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

    for idx, item in enumerate(matrix, start=1):
        table.cell(idx, 0).text = str(item.get("req_id", ""))
        table.cell(idx, 1).text = str(item.get("description", ""))
        table.cell(idx, 2).text = str(item.get("type", "Mandatory"))
        status_cell = table.cell(idx, 3)
        status_text = str(item.get("compliance_status", "Compliant"))
        status_cell.text = status_text
        if "compliant" in status_text.lower() and "non" not in status_text.lower():
            set_cell_background(status_cell, "E8F8F5")
        ref_text = str(item.get("response_section", ""))
        cit = item.get("evidence_citation")
        if cit:
            ref_text += f" ({cit})"
        table.cell(idx, 4).text = ref_text


def convert_docx_to_pdf(docx_path: Path, output_pdf_path: Path) -> tuple[Path, str]:
    """Converts DOCX to PDF using LibreOffice headless if available, otherwise pure Python FPDF2."""
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Try LibreOffice headless
    soffice_cmd = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice_cmd:
        try:
            cmd = [
                soffice_cmd,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_pdf_path.parent),
                str(docx_path),
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            candidate = output_pdf_path.parent / (docx_path.stem + ".pdf")
            if candidate.exists():
                if candidate != output_pdf_path:
                    shutil.move(str(candidate), str(output_pdf_path))
                return output_pdf_path, "libreoffice"
        except Exception:
            pass

    # 2. Pure Python FPDF2 fallback
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("helvetica", style="B", size=18)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(w=pdf.epw, h=10, text="BIDVERA PROPOSAL DOCUMENT", align="C")
    pdf.ln(5)

    try:
        doc = docx.Document(docx_path)
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            is_heading = p.style and "Heading" in p.style.name
            safe_text = text.encode("latin-1", "replace").decode("latin-1")
            pdf.set_x(pdf.l_margin)
            if is_heading:
                pdf.set_font("helvetica", style="B", size=13)
                pdf.ln(3)
                pdf.multi_cell(w=pdf.epw, h=7, text=safe_text)
                pdf.ln(2)
            else:
                pdf.set_font("helvetica", size=10)
                pdf.multi_cell(w=pdf.epw, h=5, text=safe_text)
                pdf.ln(2)

        for table in doc.tables:
            pdf.ln(3)
            pdf.set_font("helvetica", style="B", size=8)
            for row in table.rows:
                row_str = " | ".join(c.text.strip().replace("\n", " ") for c in row.cells)
                safe_row = row_str.encode("latin-1", "replace").decode("latin-1")
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=5, text=safe_row)
            pdf.ln(3)

    except Exception as e:
        pdf.set_font("helvetica", size=10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(w=pdf.epw, h=5, text=f"Document converted from {docx_path.name}: {e}")

    pdf.output(str(output_pdf_path))
    return output_pdf_path, "fpdf2_fallback"
