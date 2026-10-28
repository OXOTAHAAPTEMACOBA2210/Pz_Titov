import os
import docx
from docx.shared import Pt, RGBColor

# Очищенный скрипт для создания отчетов
# Упрощенная генерация отчета: только суть
def create_report(filename, title, code_file, code_text, screenshots=None):
    doc = docx.Document()
    
    # Заголовок
    p = doc.add_paragraph()
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(14)
    
    doc.add_paragraph("Студент: Кузьменко В.А., группа ДЭ 21-24")
    
    # Краткое описание (вместо всего кода)
    doc.add_heading("Анализ реализации:", level=1)
    doc.add_paragraph(f"В данной работе реализованы ключевые SQL-запросы и логика Python-скрипта {code_file}.")
    
    # Здесь можно вставить только критически важные части кода, если нужно
    doc.add_heading("Ключевые фрагменты:", level=1)
    doc.add_paragraph("...") 
    
    if screenshots:
        doc.add_heading("Результаты (скриншоты):", level=1)
        for shot in screenshots:
            if os.path.exists(os.path.join(SHOTS_DIR, shot)):
                doc.add_picture(os.path.join(SHOTS_DIR, shot), width=Inches(5))
                
    doc.save(filename)

BASE_DIR = "."
create_report("Отчет_ПЗ2_Кузьменко.docx", "Отчет по ПЗ 2", "pz2.sql", open("pz2.sql", "r", encoding="utf-8").read())
create_report("Отчет_ПЗ3_Кузьменко.docx", "Отчет по ПЗ 3", "pz3.sql", open("pz3.sql", "r", encoding="utf-8").read())
create_report("Отчет_ПЗ4_Кузьменко.docx", "Отчет по ПЗ 4", "pz4.sql", open("pz4.sql", "r", encoding="utf-8").read())
create_report("Отчет_ПЗ5_Кузьменко.docx", "Отчет по ПЗ 5", "pz5_crud.py", open("pz5_crud.py", "r", encoding="utf-8").read())
create_report("Отчет_ПЗ6_Кузьменко.docx", "Отчет по ПЗ 6", "pz6_stats.py", open("pz6_stats.py", "r", encoding="utf-8").read())
create_report("Отчет_ПЗ7_Кузьменко.docx", "Отчет по ПЗ 7", "pz7_parking.sql", open("pz7_parking.sql", "r", encoding="utf-8").read())
print("Отчеты созданы!")
