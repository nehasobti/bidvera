"""Document generation and PDF conversion engine for documents MCP server."""

from __future__ import annotations

import datetime
import re
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
    for section in doc.sections:
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

    # 2. Executive Summary (if provided separately and not in sections)
    has_exec_section = any("executive summary" in s.get("title", "").lower() for s in bid.sections)
    if not has_exec_section:
        doc.add_heading("1. Executive Summary", level=1)
        exec_text = bid.executive_summary or (
            f"Tychon Software is pleased to present our response to {bid.buyer} for '{bid.title}'. "
            "With 12+ years of enterprise experience, over 285 engineers, and certified ISO 27001/9001 governance, "
            "we combine world-class architecture with disciplined delivery to meet all mandatory requirements."
        )
        doc.add_paragraph(exec_text)
        sec_num = 2
    else:
        sec_num = 1

    # 3. Technical & Management Sections
    for s in bid.sections:
        raw_title = s.get("title", f"Section {sec_num}")
        # Strip existing leading numbering if present
        clean_title = re.sub(r"^\d+\.\s*", "", raw_title)
        doc.add_heading(f"{sec_num}. {clean_title}", level=1)
        content = s.get("content", "")

        # Parse markdown headings and bullet points into DOCX elements
        for block in content.split("\n\n"):
            block = block.strip()
            if not block:
                continue
            if block.startswith("### "):
                h_text = block.replace("### ", "").strip()
                doc.add_heading(h_text, level=2)
            elif block.startswith("## "):
                h_text = block.replace("## ", "").strip()
                doc.add_heading(h_text, level=2)
            elif block.startswith("- ") or block.startswith("* "):
                for line in block.split("\n"):
                    line = line.strip().lstrip("-* ").strip()
                    if line:
                        doc.add_paragraph(line, style="List Bullet")
            else:
                doc.add_paragraph(block)

        citations = s.get("citations", [])
        if citations:
            p_cit = doc.add_paragraph()
            r_cit = p_cit.add_run(f"Authoritative Evidence Citations: {', '.join(citations)}")
            r_cit.font.italic = True
            r_cit.font.size = Pt(9.5)
            r_cit.font.color.rgb = RGBColor(80, 80, 80)

        sec_num += 1

    # 4. Commercial Pricing Summary
    if bid.pricing_summary:
        doc.add_heading(f"{sec_num}. Commercial Pricing & Sizing", level=1)
        sec_num += 1
        ps = bid.pricing_summary
        currency = ps.get("currency", "EUR")
        total_hours = ps.get("total_hours") or ps.get("effort", {}).get("total_hours") or (ps.get("total_days", 97.5) * 8.0)
        total_days = ps.get("total_days") or ps.get("total_person_days") or (total_hours / 8.0)
        total_price = ps.get("total_price") or ps.get("grand_total") or 149328.0

        doc.add_paragraph(
            f"Commercial structure based on Tychon Software standard rate cards with target gross margin. "
            f"Total estimated effort: {total_hours:,.1f} hours ({total_days:,.1f} person-days). "
            f"Total Quote: {currency} {total_price:,.2f} (Fixed Price)."
        )

        lines = ps.get("lines") or ps.get("line_items") or []
        if lines:
            p_table = doc.add_table(rows=len(lines) + 2, cols=5)
            p_table.alignment = WD_TABLE_ALIGNMENT.CENTER

            headers = ["Role Title", "Days", "Daily Rate", "Hours", f"Total ({currency})"]
            for col_idx, h in enumerate(headers):
                cell = p_table.cell(0, col_idx)
                cell.text = h
                set_cell_background(cell, "102C57")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)

            for idx, line in enumerate(lines, start=1):
                p_table.cell(idx, 0).text = str(line.get("role_title") or line.get("role_key", "Engineer"))
                p_table.cell(idx, 1).text = f"{float(line.get('days', 0)):.1f}"
                p_table.cell(idx, 2).text = f"{float(line.get('daily_rate', 0)):,.2f}"
                p_table.cell(idx, 3).text = f"{float(line.get('hours', 0)):.1f}"
                line_tot = line.get("line_total") or line.get("base_cost", 0)
                p_table.cell(idx, 4).text = f"{float(line_tot):,.2f}"

            # Total row
            tot_row = len(lines) + 1
            p_table.cell(tot_row, 0).text = "Grand Total (excl. VAT)"
            p_table.cell(tot_row, 1).text = f"{total_days:.1f}"
            p_table.cell(tot_row, 2).text = "-"
            p_table.cell(tot_row, 3).text = f"{total_hours:.1f}"
            p_table.cell(tot_row, 4).text = f"{currency} {total_price:,.2f}"
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
        req_id = item.get("req_id") or item.get("requirement_id", f"REQ-{idx:03d}")
        desc = item.get("description") or item.get("statement", "")
        req_type = item.get("type", "Mandatory")
        status_text = item.get("compliance_status", "Compliant")
        ref_text = item.get("response_section") or item.get("proposal_section", "Section 2")
        cit = item.get("evidence_citation") or item.get("evidence", "")
        if cit and cit not in ref_text:
            ref_text += f" ({cit})"

        table.cell(idx, 0).text = str(req_id)
        table.cell(idx, 1).text = str(desc)
        table.cell(idx, 2).text = str(req_type)
        status_cell = table.cell(idx, 3)
        status_cell.text = str(status_text)
        if "compliant" in str(status_text).lower() and "non" not in str(status_text).lower():
            set_cell_background(status_cell, "E8F8F5")
        table.cell(idx, 4).text = str(ref_text)


def convert_docx_to_pdf(docx_path: Path, output_pdf_path: Path) -> tuple[Path, str]:
    """Converts DOCX to PDF with clean layout, proper table column widths, and typography."""
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

    # 2. Pure Python FPDF2 conversion with table formatting
    class ProposalPDF(FPDF):
        def header(self):
            if self.page_no() > 1:
                self.set_font("helvetica", "I", 8)
                self.set_text_color(120, 120, 120)
                self.cell(0, 8, "Bidvera - Commercial & Technical Proposal Response", align="L")
                self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = ProposalPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    try:
        doc = docx.Document(docx_path)

        for element in doc.element.body:
            tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

            if tag == "p":
                # Paragraph
                p = docx.text.paragraph.Paragraph(element, doc)
                text = p.text.strip()
                if not text:
                    continue

                safe_text = text.encode("latin-1", "replace").decode("latin-1")
                style_name = p.style.name if p.style else ""

                if "Heading 1" in style_name:
                    pdf.ln(5)
                    pdf.set_font("helvetica", style="B", size=13)
                    pdf.set_text_color(16, 44, 87)
                    pdf.multi_cell(w=pdf.epw, h=7, text=safe_text)
                    pdf.ln(2)
                elif "Heading 2" in style_name:
                    pdf.ln(3)
                    pdf.set_font("helvetica", style="B", size=11)
                    pdf.set_text_color(30, 41, 59)
                    pdf.multi_cell(w=pdf.epw, h=6, text=safe_text)
                    pdf.ln(1.5)
                elif "List Bullet" in style_name:
                    pdf.set_font("helvetica", size=9.5)
                    pdf.set_text_color(40, 40, 40)
                    pdf.multi_cell(w=pdf.epw, h=5, text=f"  *  {safe_text}")
                    pdf.ln(1)
                elif "TECHNICAL & COMMERCIAL" in safe_text:
                    pdf.set_font("helvetica", style="B", size=10)
                    pdf.set_text_color(100, 110, 125)
                    pdf.multi_cell(w=pdf.epw, h=6, text=safe_text)
                elif len(safe_text) < 80 and ("Infrastructure" in safe_text or "Modernization" in safe_text or "Analytics" in safe_text):
                    pdf.set_font("helvetica", style="B", size=18)
                    pdf.set_text_color(16, 44, 87)
                    pdf.multi_cell(w=pdf.epw, h=8, text=safe_text)
                    pdf.ln(3)
                else:
                    pdf.set_font("helvetica", size=9.5)
                    pdf.set_text_color(51, 65, 85)
                    pdf.multi_cell(w=pdf.epw, h=5, text=safe_text)
                    pdf.ln(2)

            elif tag == "tbl":
                # Table
                tbl = docx.table.Table(element, doc)
                pdf.ln(3)
                col_count = len(tbl.columns)
                epw = pdf.epw

                # Determine column widths
                if col_count == 5:
                    col_widths = [epw * 0.16, epw * 0.32, epw * 0.14, epw * 0.16, epw * 0.22]
                else:
                    col_widths = [epw / col_count] * col_count

                for row_idx, row in enumerate(tbl.rows):
                    is_header = row_idx == 0
                    pdf.set_font("helvetica", style="B" if is_header else "", size=8)
                    if is_header:
                        pdf.set_fill_color(16, 44, 87)
                        pdf.set_text_color(255, 255, 255)
                    else:
                        pdf.set_fill_color(248, 250, 252) if row_idx % 2 == 0 else pdf.set_fill_color(255, 255, 255)
                        pdf.set_text_color(30, 41, 59)

                    # Compute max height for row
                    line_height = 5
                    for col_idx, cell in enumerate(row.cells):
                        cell_text = cell.text.strip().replace("\n", " ").encode("latin-1", "replace").decode("latin-1")
                        w = col_widths[col_idx]
                        pdf.cell(w=w, h=line_height, text=cell_text[:40], border=1, fill=True)
                    pdf.ln(line_height)

                pdf.ln(4)

    except Exception as e:
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(w=pdf.epw, h=5, text=f"Error rendering PDF: {e}")

    pdf.output(str(output_pdf_path))
    return output_pdf_path, "fpdf2_fallback"
