import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = os.path.abspath(".")
SHOTS_DIR = os.path.join(BASE_DIR, "screenshots")

def set_style(run, bold=False, size=11):
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)

def add_clean_heading(doc, text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_style(run, bold=True, size=16 if level==1 else 13)
    return p

def create_report(filename, title, code_file, code_text, screenshots=None):
    doc = docx.Document()
    add_clean_heading(doc, title, 1)
    doc.add_paragraph("Студент: Кузьменко В.А., группа ДЭ 21-24")
    
    doc.add_heading("Код скрипта:", 2)
    doc.add_paragraph(code_text)
    
    if screenshots:
        for shot in screenshots:
            if os.path.exists(os.path.join(SHOTS_DIR, shot)):
                doc.add_picture(os.path.join(SHOTS_DIR, shot), width=Inches(6))
                
    doc.save(filename)

# Генерация отчетов
create_report("Отчет_ПЗ2_Кузьменко.docx", "Отчет по ПЗ 2", "pz2.sql", open("pz2.sql", "r", encoding="utf-8").read(), ["pz2_structure.png", "pz2_test_negative.png"])
create_report("Отчет_ПЗ3_Кузьменко.docx", "Отчет по ПЗ 3", "pz3.sql", open("pz3.sql", "r", encoding="utf-8").read(), ["pz3_schema_diagram.png", "pz3_test_fk.png"])
create_report("Отчет_ПЗ4_Кузьменко.docx", "Отчет по ПЗ 4", "pz4.sql", open("pz4.sql", "r", encoding="utf-8").read(), ["pz4_comp_data.png", "pz4_study_query.png"])
create_report("Отчет_ПЗ5_Кузьменко.docx", "Отчет по ПЗ 5", "pz5_crud.py", open("pz5_crud.py", "r", encoding="utf-8").read(), ["pz5_console_crud.png"])
create_report("Отчет_ПЗ6_Кузьменко.docx", "Отчет по ПЗ 6", "pz6_stats.py", open("pz6_stats.py", "r", encoding="utf-8").read(), ["pz6_console_stats.png"])
create_report("Отчет_ПЗ7_Кузьменко.docx", "Отчет по ПЗ 7", "pz7_parking.sql", open("pz7_parking.sql", "r", encoding="utf-8").read())
print("Все отчеты созданы в ЧБ формате!")
