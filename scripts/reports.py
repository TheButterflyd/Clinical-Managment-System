import json
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.db import run_select

OUT_DIR = Path("scripts/outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_NAME = "Raport_Activitate_Medici"
PDF_PATH = OUT_DIR / f"{BASE_NAME}.pdf"
CSV_PATH = OUT_DIR / f"{BASE_NAME}.csv"
JSON_PATH = OUT_DIR / f"{BASE_NAME}.json"
CHART_PATH = OUT_DIR / f"{BASE_NAME}_chart.png"


CALE_FONT_SYSTEM = "C:\\Windows\\Fonts\\arial.ttf"
FONT_RAPORT = "Helvetica"  # Fallback implicit

if os.path.exists(CALE_FONT_SYSTEM):
    try:
        pdfmetrics.registerFont(TTFont("ArialRomana", CALE_FONT_SYSTEM))
        FONT_RAPORT = "ArialRomana"
    except Exception:
        pass


# =========================================================================

def normalize(v):
    if isinstance(v, Decimal):
        x = float(v)
        return int(x) if x.is_integer() else x
    return v


def fetch_medical_data():
    sql = """
          SELECT m.nume, COUNT(c.id_consult) as total_consultatii
          FROM Medici m
                   JOIN Programari p ON m.id_medic = p.id_medic
                   JOIN Consultatii c ON p.id_programare = c.id_prog
          GROUP BY m.id_medic, m.nume
          ORDER BY total_consultatii DESC \
          """
    rows = run_select(sql)
    return [{"nume_medic": r[0], "total_consultatii": normalize(r[1])} for r in rows]


def export_csv(data):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nume_medic", "total_consultatii"])
        writer.writeheader()
        writer.writerows(data)


def export_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_activity_chart(data):
    names = [d["nume_medic"] for d in data]
    values = [d["total_consultatii"] for d in data]

    plt.figure(figsize=(10, 6))
    plt.bar(names, values, color='#2c3e50')
    plt.title("Număr Consultații per Medic")
    plt.xlabel("Medic")
    plt.ylabel("Nr. Consultații")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(str(CHART_PATH))
    plt.close()


def generate_medical_pdf(data):
    """Generează raportul PDF profesional utilizând ReportLab cu suport diacritice."""
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()


    styles["Normal"].fontName = FONT_RAPORT
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 14


    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        fontName=FONT_RAPORT,
        fontSize=20,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=15,
        alignment=1  # Centrat
    )


    subtitle_style = ParagraphStyle(
        name="SubtitleStyle",
        parent=styles["Heading2"],
        fontName=FONT_RAPORT,
        fontSize=14,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=15
    )


    th_style = ParagraphStyle(name="TableHeader", fontName=FONT_RAPORT, fontSize=11, textColor=colors.white,
                              alignment=1)
    td_style = ParagraphStyle(name="TableCell", fontName=FONT_RAPORT, fontSize=10, alignment=1)

    elements.append(Paragraph("Sistem Management Clinică Medicală", title_style))
    elements.append(Paragraph("Raport Business Intelligence - Activitate Medici", subtitle_style))
    elements.append(Spacer(1, 10))

    intro_text = f"""
    Acest raport prezintă analiza performanței personalului medical.<br/> 
    Datele reflectă volumul de consultații finalizate, agregate din baza de date a clinicii.<br/>
    <b>Raport generat la data:</b> {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
    """
    elements.append(Paragraph(intro_text, styles["Normal"]))
    elements.append(Spacer(1, 20))


    table_data = [[
        Paragraph("Nume Medic", th_style),
        Paragraph("Total Consultații", th_style)
    ]]

    for d in data:
        table_data.append([
            Paragraph(str(d["nume_medic"]), td_style),
            Paragraph(str(d["total_consultatii"]), td_style)
        ])

    table = Table(table_data, colWidths=[3.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f4f7f6")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    if CHART_PATH.exists():
        chart = Image(str(CHART_PATH), width=6 * inch, height=3.5 * inch)
        elements.append(chart)

    doc.build(elements)


def main():
    print("=== Initiere Generare Raport Clinica ===")
    data = fetch_medical_data()

    if not data:
        print("Atenție: Nu există date înregistrate în tabela Consultatii.")
        return

    export_csv(data)
    export_json(data)
    generate_activity_chart(data)
    generate_medical_pdf(data)

    print(f" Raport generat cu succes in: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()