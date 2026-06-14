from fpdf import FPDF
from datetime import datetime


class _PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(95, 10, "Multi-Agent RAG Research Assistant")
        self.cell(95, 10, f"Page {self.page_no()}", align="R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%d %B %Y  %H:%M')}", align="C")


def generate_pdf(source_name, analysis):
    pdf = _PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(15, 40, 100)
    pdf.cell(0, 14, "Intelligence Report", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Source file: {source_name}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%d %B %Y  %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_draw_color(15, 40, 100)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # Stats
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 40, 100)
    pdf.cell(0, 10, "Document Statistics", new_x="LMARGIN", new_y="NEXT")
    pdf.set_line_width(0.3)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_text_color(0, 0, 0)
    for k, v in analysis.get("stats", {}).items():
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(65, 8, f"{k}:")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(v), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Summary
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 40, 100)
    pdf.cell(0, 10, "Summary & Insights", new_x="LMARGIN", new_y="NEXT")
    pdf.set_line_width(0.3)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 7, analysis.get("summary", ""))

    return bytes(pdf.output())
