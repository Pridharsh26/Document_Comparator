import io
import logging
from typing import List

from fpdf import FPDF
from models.schemas import ComparisonResult

logger = logging.getLogger(__name__)


class PDFExportError(Exception):
    pass


class SimplifiedReportPDF(FPDF):
    def header(self) -> None:
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "AI Document Comparator - Impact Report", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", new_x="RIGHT", new_y="LAST")


def _sanitize_text(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1", "replace")


def export_pdf(comparison: ComparisonResult) -> bytes:
    try:
        pdf = SimplifiedReportPDF()
        pdf.add_page()
        pdf.set_font("Arial", "", 10)

        pdf.cell(0, 8, _sanitize_text("Executive Summary"), new_x="LMARGIN", new_y="NEXT")
        pdf.multi_cell(0, 6, _sanitize_text(
            f"Total Legacy Rules: {comparison.summary.total_legacy_rules} | "
            f"Total Modernized Rules: {comparison.summary.total_modernized_rules}\n"
            f"Added: {comparison.summary.added} | Removed: {comparison.summary.removed} | "
            f"Modified: {comparison.summary.modified}"
        ))
        pdf.ln(2)

        for group_title, filter_fn in [
            ("Added Rules", lambda c: c.change_type.value == "ADDED"),
            ("Removed Rules", lambda c: c.change_type.value == "REMOVED"),
            ("Modified Rules", lambda c: c.change_type.value == "MODIFIED"),
        ]:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, _sanitize_text(group_title), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Arial", "", 10)
            items = [c for c in comparison.changes if filter_fn(c)]
            if not items:
                pdf.cell(0, 6, _sanitize_text("None"), new_x="LMARGIN", new_y="NEXT")
                continue
            for item in items:
                text = _sanitize_text(
                    f"- {item.change_type.value}: {(item.legacy_rule or item.modernized_rule or '')[:120]}"
                )
                pdf.multi_cell(0, 6, text)
            pdf.ln(2)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, _sanitize_text("Impact Analysis"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Arial", "", 10)
        for item in comparison.changes:
            explanation = _sanitize_text(item.business_explanation or "")
            pdf.multi_cell(0, 6, explanation)
            pdf.cell(0, 6, _sanitize_text(
                f"Impact: {item.impact_level} | Risk: {item.risk_level} | Priority: {item.priority_level}"
            ), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        stream = io.BytesIO()
        pdf.output(stream)
        return stream.getvalue()
    except Exception as exc:
        logger.error("PDF export failed: %s", exc)
        raise PDFExportError(str(exc))
