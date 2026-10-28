# -*- coding: utf-8 -*-
"""
Generate comprehensive Word (.docx) reports for Titov:
- Отчет_ПЗ2_Титов.docx
- Отчет_ПЗ3_Титов.docx
- Отчет_ПЗ4_Титов.docx
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.abspath(".")
SHOTS_DIR = os.path.join(BASE_DIR, "screenshots")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_table_borders(table, color="D0D5DD", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def style_paragraph(p, font_name="Arial", size_pt=11, bold=False, italic=False, color_rgb=(0,0,0), space_after=6, space_before=0, line_spacing=1.15):
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = line_spacing
    for run in p.runs:
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = RGBColor(*color_rgb)

def add_styled_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    if level == 1:
        style_paragraph(h, "Arial", 16, bold=True, color_rgb=(20, 50, 100), space_before=14, space_after=8)
    elif level == 2:
        style_paragraph(h, "Arial", 13, bold=True, color_rgb=(30, 70, 130), space_before=10, space_after=6)
    elif level == 3:
        style_paragraph(h, "Arial", 11.5, bold=True, color_rgb=(50, 80, 120), space_before=8, space_after=4)
    return h

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F4F6F9")
    set_table_borders(tbl, color="D0D7DE", sz="6", val="single")
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(30, 40, 60)
    doc.add_paragraph() # spacing


# ==============================================================================
# REPORT 2: Отчет_ПЗ2_Титов.docx
# ==============================================================================
print("Creating Отчет_ПЗ2_Титов.docx...")
doc2 = docx.Document()

# Page Margins
sections = doc2.sections
for s in sections:
    s.top_margin = Inches(0.8)
    s.bottom_margin = Inches(0.8)
    s.left_margin = Inches(0.8)
    s.right_margin = Inches(0.8)

# Title Block
title_p = doc2.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title_p.add_run("ОТЧЁТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 2\n")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.bold = True
r.font.color.rgb = RGBColor(20, 50, 100)

r_sub = title_p.add_run("«Проектирование структуры таблицы и контроль корректности данных в SQLite»\n")
r_sub.font.name = "Arial"
r_sub.font.size = Pt(13)
r_sub.font.bold = True
r_sub.font.color.rgb = RGBColor(60, 60, 60)

r_info = title_p.add_run("Студент: Кузьменко В.А., группа ДЭ 21-24 | База данных: library_titov.db | Файл скрипта: pz2.sql")
r_info.font.name = "Arial"
r_info.font.size = Pt(10.5)
r_info.font.italic = True
r_info.font.color.rgb = RGBColor(100, 100, 100)

doc2.add_paragraph()

# 1. Theoretical Intro & Initial State
add_styled_heading(doc2, "1. Исходная ситуация и теоретический минимум", level=1)
p = doc2.add_paragraph(
    "В рамках Практической работы № 1 была создана базовая таблица «Книги» (books_legacy) "
    "со столбцами: Код_книги, Автор, Название, Издательство, Цена и Остаток, в которую было внесено 10 записей. "
    "На этапе первоначального знакомства таблица не содержала строгих механизмов контроля целостности данных. "
    "В реальной информационной системе отсутствие ограничений на уровне СУБД приводит к критическим рискам: "
    "появлению отрицательных цен и остатков, дублированию записей, неполным записям (NULL в обязательном поле) и пустым строкам."
)
style_paragraph(p, "Arial", 11, line_spacing=1.15)

p = doc2.add_paragraph(
    "При проектировании надежной реляционной таблицы в SQLite ключевую роль играют следующие ограничения:\n"
    "• PRIMARY KEY — обеспечивает уникальность и первичную идентификацию строк;\n"
    "• NOT NULL — предотвращает отсутствие данных в критически важных атрибутах;\n"
    "• UNIQUE — гарантирует неповторяемость естественных идентификаторов (например, ISBN, артикулов);\n"
    "• DEFAULT — подставляет предопределенное значение при его пропуске пользователем (например, остаток = 0);\n"
    "• CHECK — реализует логическую валидацию бизнес-правил (цена > 0, остаток >= 0, непустая строка);\n"
    "• AUTOINCREMENT — обеспечивает строго монотонное возрастание числового первичного ключа."
)
style_paragraph(p, "Arial", 11, line_spacing=1.15)

# 2. Stage 2: Analysis of Legacy Table
add_styled_heading(doc2, "2. Анализ исходной структуры и выявленные проблемы", level=1)
p = doc2.add_paragraph("Ниже представлена таблица анализа полей и проектных решений по усилению ограничений:")
style_paragraph(p, "Arial", 11)

t_analysis = doc2.add_table(rows=9, cols=4)
t_analysis.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_analysis)

headers_a = ["Поле", "Предлагаемый тип", "Ограничение(я)", "Зачем это нужно"]
for col_idx, text in enumerate(headers_a):
    cell = t_analysis.cell(0, col_idx)
    cell.paragraphs[0].text = text
    style_paragraph(cell.paragraphs[0], "Arial", 10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(cell, "2B547E")

rows_a_data = [
    ("Идентификатор (id)", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Гарантирует уникальность каждой книги и устойчивую адресацию записи"),
    ("Название (title)", "TEXT", "NOT NULL, CHECK(length(trim(title))>0)", "Книга обязательно должна иметь название; исключается вставка пробелов/пустых строк"),
    ("Автор (author)", "TEXT", "NOT NULL, CHECK(length(trim(author))>0)", "Исключает анонимные записи без указания автора книги"),
    ("Издательство (publisher)", "TEXT", "NOT NULL, CHECK(length(trim(publisher))>0)", "Обязательное указание издательской организации"),
    ("ISBN (доп. поле)", "TEXT", "UNIQUE NOT NULL, CHECK(length>=10)", "Естественный уникальный номер издания; блокирует повторный ввод той же книги"),
    ("Год издания (publication_year)", "INTEGER", "NOT NULL, CHECK(1800..2026)", "Предотвращает ошибочный ввод некорректных или будущих дат"),
    ("Цена (price)", "REAL", "NOT NULL, CHECK(price > 0)", "Исключает отрицательную и нулевую стоимость книги"),
    ("Остаток (stock)", "INTEGER", "NOT NULL DEFAULT 0, CHECK(stock >= 0)", "Гарантирует неотрицательное складское количество; при отсутствии ставится 0")
]

for row_idx, r_data in enumerate(rows_a_data, start=1):
    for col_idx, val in enumerate(r_data):
        cell = t_analysis.cell(row_idx, col_idx)
        cell.paragraphs[0].text = val
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(cell, bg)
        style_paragraph(cell.paragraphs[0], "Arial", 9.5)

doc2.add_paragraph()

p_prob = doc2.add_paragraph("Формулировка проблем, которые исходная таблица не предотвращает автоматически:")
style_paragraph(p_prob, "Arial", 11, bold=True)

problems = [
    "1. Допуск NULL и пустых строк в полях Автор и Название (риск появления бессмысленных записей).",
    "2. Допуск отрицательной стоимости (например, -500 рублей), что нарушает финансовую логику учета.",
    "3. Допуск отрицательного складского остатка, что приводит к искажению товарно-материальных отчетов.",
    "4. Отсутствие контроля уникальности: одну и ту же книгу можно было добавить многократно без предупреждения.",
    "5. Отсутствие значения по умолчанию: при поступлении новой номенклатуры поле остатка оставалось пустым."
]
for prob in problems:
    p = doc2.add_paragraph(prob)
    style_paragraph(p, "Arial", 10.5, line_spacing=1.1)

# 3. Stage 3 & 4: Improved Table SQL & Population
add_styled_heading(doc2, "3. Проектирование и создание улучшенной таблицы (books_improved)", level=1)
p = doc2.add_paragraph(
    "Для устранения указанных проблем была спроектирована и реализована улучшенная таблица books_improved, "
    "содержащая 8 столбцов и полный комплекс ограничений целостности."
)
style_paragraph(p, "Arial", 11)

sql_create_improved = """CREATE TABLE books_improved (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
    author TEXT NOT NULL CHECK(length(trim(author)) > 0),
    publisher TEXT NOT NULL CHECK(length(trim(publisher)) > 0),
    isbn TEXT NOT NULL UNIQUE CHECK(length(trim(isbn)) >= 10),
    publication_year INTEGER NOT NULL CHECK(publication_year >= 1800 AND publication_year <= 2026),
    price REAL NOT NULL CHECK(price > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0)
);"""
add_code_block(doc2, sql_create_improved)

p = doc2.add_paragraph("В созданную таблицу перенесено 10 корректных записей с реалистичными ISBN и параметрами.")
style_paragraph(p, "Arial", 11)

# 4. Stage 6: Negative Testing
add_styled_heading(doc2, "4. Негативное тестирование ограничений целостности", level=1)
p = doc2.add_paragraph(
    "В соответствии с методикой «Как проверять ограничения», для каждого правила целостности "
    "был выполнен заведомо некорректный сценарий и зафиксирована точная реакция ядра СУБД SQLite."
)
style_paragraph(p, "Arial", 11)

t_tests = doc2.add_table(rows=8, cols=4)
t_tests.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_tests)

headers_t = ["№", "Тест", "Ожидаемое поведение", "Фактический результат / Сообщение SQLite"]
for col_idx, text in enumerate(headers_t):
    cell = t_tests.cell(0, col_idx)
    cell.paragraphs[0].text = text
    style_paragraph(cell.paragraphs[0], "Arial", 10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(cell, "2B547E")

tests_data = [
    ("1", "Попытка повторить значение первичного ключа (id=1)", "Операция отклоняется СУБД", "UNIQUE constraint failed: books_improved.id"),
    ("2", "Попытка повторить значение поля с UNIQUE (дубликат ISBN)", "Операция отклоняется СУБД", "UNIQUE constraint failed: books_improved.isbn"),
    ("3", "Попытка оставить обязательное поле NULL (title=NULL)", "Операция отклоняется СУБД", "NOT NULL constraint failed: books_improved.title"),
    ("4", "Попытка записать отрицательную цену (price=-150)", "Операция отклоняется СУБД", "CHECK constraint failed: price > 0"),
    ("5", "Попытка записать отрицательный остаток (stock=-10)", "Операция отклоняется СУБД", "CHECK constraint failed: stock >= 0"),
    ("6", "Добавление записи без значения поля, имеющего DEFAULT", "Операция проходит, ставится 0", "Успешно: полю stock автоматически присвоено значение 0"),
    ("7", "Дополнительный тест: пустая строка пробелов в названии", "Операция отклоняется CHECK", "CHECK constraint failed: length(trim(title)) > 0")
]

for row_idx, r_data in enumerate(tests_data, start=1):
    for col_idx, val in enumerate(r_data):
        cell = t_tests.cell(row_idx, col_idx)
        cell.paragraphs[0].text = val
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(cell, bg)
        style_paragraph(cell.paragraphs[0], "Arial", 9.5)

doc2.add_paragraph()

# Comparison Table
add_styled_heading(doc2, "Сравнение исходной и улучшенной таблиц", level=2)
t_comp = doc2.add_table(rows=8, cols=3)
t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_comp)

headers_c = ["Критерий", "Исходная таблица «Книги»", "Новая таблица «books_improved»"]
for col_idx, text in enumerate(headers_c):
    cell = t_comp.cell(0, col_idx)
    cell.paragraphs[0].text = text
    style_paragraph(cell.paragraphs[0], "Arial", 10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(cell, "2B547E")

comp_data = [
    ("Однозначная идентификация строки", "Только по Код_книги без защиты от ручного сбоя", "INTEGER PRIMARY KEY AUTOINCREMENT гарантирует строгую уникальность"),
    ("Защита обязательных полей", "Отсутствует: поля могли оставаться пустыми (NULL)", "Ограничения NOT NULL на всех атрибутах исключают потерю данных"),
    ("Контроль повторов", "Отсутствует: можно было дублировать одну книгу", "Ограничение UNIQUE на ISBN исключает повторный ввод издания"),
    ("Контроль диапазона цены", "Отсутствует: допускались любые отрицательные числа", "CHECK(price > 0) разрешает только положительные денежные суммы"),
    ("Контроль диапазона остатка", "Отсутствует: допускались отрицательные остатки", "CHECK(stock >= 0) гарантирует корректность складского остатка"),
    ("Значения по умолчанию", "Не заданы: пропущенные поля получали NULL", "DEFAULT 0 для остатка обеспечивает готовность товара к учету"),
    ("Какие ошибки всё ещё должна проверять программа / пользователь", "Любые смысловые и синтаксические ошибки", "Опечатки в фамилии автора, смысловые ошибки в тексте названия, соответствие книги обложке")
]

for row_idx, r_data in enumerate(comp_data, start=1):
    for col_idx, val in enumerate(r_data):
        cell = t_comp.cell(row_idx, col_idx)
        cell.paragraphs[0].text = val
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(cell, bg)
        style_paragraph(cell.paragraphs[0], "Arial", 9.5)

doc2.add_paragraph()

# 5. Individual Table: store_products
add_styled_heading(doc2, "5. Индивидуальная часть: Таблица «Товары интернет-магазина» (store_products)", level=1)
p = doc2.add_paragraph(
    "В соответствии с индивидуальным заданием спроектирована самостоятельная таблица store_products "
    "для предметной области интернет-магазина электроники (8 полей). Таблица включает полный комплекс изученных ограничений:"
)
style_paragraph(p, "Arial", 11)

sql_store = """CREATE TABLE store_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE CHECK(length(trim(sku)) >= 4),
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    category TEXT NOT NULL CHECK(length(trim(category)) > 0),
    price REAL NOT NULL CHECK(price > 0),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    warranty_months INTEGER NOT NULL DEFAULT 12 CHECK(warranty_months >= 0 AND warranty_months <= 120),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1))
);"""
add_code_block(doc2, sql_store)

p_store_desc = doc2.add_paragraph(
    "Обоснование ограничений индивидуальной таблицы:\n"
    "• PRIMARY KEY (id) — суррогатный первичный ключ для идентификации строки в системе;\n"
    "• UNIQUE (sku) — артикул товара не должен дублироваться в каталоге интернет-магазина;\n"
    "• NOT NULL (name, category, price) — товар не может существовать без названия, категории и цены;\n"
    "• DEFAULT 0 (quantity) — при создании карточки товара до физической поставки на склад остаток равен 0;\n"
    "• DEFAULT 12 (warranty_months) — базовый гарантийный срок по умолчанию составляет 1 год (12 месяцев);\n"
    "• CHECK(price > 0) — коммерческий товар не может продаваться по нулевой или отрицательной цене;\n"
    "• CHECK(quantity >= 0) — исключается возникновение отрицательных складских остатков;\n"
    "• CHECK(warranty_months BETWEEN 0 AND 120) — допустимый диапазон гарантии от 0 до 10 лет;\n"
    "• CHECK(is_active IN (0, 1)) — бинарный флаг доступности товара для отображения на витрине."
)
style_paragraph(p_store_desc, "Arial", 10.5, line_spacing=1.15)

# Screenshots Section
add_styled_heading(doc2, "6. Подтверждающие скриншоты DB Browser for SQLite", level=1)
p = doc2.add_paragraph("Ниже приведены скриншоты структуры таблиц и результатов тестирования ограничений:")
style_paragraph(p, "Arial", 11)

if os.path.exists(os.path.join(SHOTS_DIR, "pz2_structure.png")):
    doc2.add_picture(os.path.join(SHOTS_DIR, "pz2_structure.png"), width=Inches(6.2))
    p_cap = doc2.add_paragraph("Рисунок 1 – Структура таблиц books_improved и store_products в DB Browser")
    style_paragraph(p_cap, "Arial", 9.5, italic=True, color_rgb=(100, 100, 100))

if os.path.exists(os.path.join(SHOTS_DIR, "pz2_test_negative.png")):
    doc2.add_picture(os.path.join(SHOTS_DIR, "pz2_test_negative.png"), width=Inches(6.2))
    p_cap = doc2.add_paragraph("Рисунок 2 – Результаты выполнения негативных тестов и фиксация сообщений SQLite")
    style_paragraph(p_cap, "Arial", 9.5, italic=True, color_rgb=(100, 100, 100))

# Conclusion
add_styled_heading(doc2, "7. Вывод", level=1)
p_concl = doc2.add_paragraph(
    "В ходе выполнения практической работы № 2 было проведено детальное исследование механизмов контроля корректности данных в СУБД SQLite.\n\n"
    "1. Ошибки, предотвращенные на уровне БД: переход от простой структуры к таблице с декларативными ограничениями "
    "позволил полностью исключить возможность внесения противоречивых или поврежденных данных. СУБД автоматически блокирует "
    "попытки ввода дубликатов (UNIQUE), пропуск обязательных значений (NOT NULL), пустые строковые значения и пробелы (CHECK length), "
    "а также логически недопустимые отрицательные цены и остатки (CHECK).\n\n"
    "2. Наиболее полезные ограничения: ограничение CHECK доказало свою универсальность, позволив реализовать как числовые диапазоны, "
    "так и проверку длины строк. Ограничение UNIQUE на естественный ключ (ISBN, артикул SKU) предотвращает дублирование сущностей "
    "независимо от человеческого фактора. Ограничение DEFAULT существенно упрощает прикладной код при вставке неполных данных.\n\n"
    "3. Границы возможностей ограничений SQLite: средствами рассмотренных ограничений невозможно решить задачи семантической проверки. "
    "Например, СУБД не может определить, действительно ли в поле «Автор» введено реальное имя писателя или бессмысленный набор букв, "
    "соответствует ли ISBN реальному международному реестру по контрольной сумме, и не содержит ли название орфографических ошибок. "
    "Подобная валидация должна обеспечиваться на уровне прикладного программного интерфейса и бизнес-логики приложения."
)
style_paragraph(p_concl, "Arial", 11, line_spacing=1.15)

doc2.save(os.path.join(BASE_DIR, "Отчет_ПЗ2_Титов_NEW.docx"))
print("Отчет_ПЗ2_Титов_NEW.docx created successfully!")


# ==============================================================================
# REPORT 3: Отчет_ПЗ3_Титов.docx
# ==============================================================================
print("Creating Отчет_ПЗ3_Титов.docx...")
doc3 = docx.Document()

for s in doc3.sections:
    s.top_margin = Inches(0.8)
    s.bottom_margin = Inches(0.8)
    s.left_margin = Inches(0.8)
    s.right_margin = Inches(0.8)

title_p = doc3.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title_p.add_run("ОТЧЁТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 3\n")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.bold = True
r.font.color.rgb = RGBColor(20, 50, 100)

r_sub = title_p.add_run("«Связи между таблицами и ссылочная целостность в SQLite»\n")
r_sub.font.name = "Arial"
r_sub.font.size = Pt(13)
r_sub.font.bold = True
r_sub.font.color.rgb = RGBColor(60, 60, 60)

r_info = title_p.add_run("Студент: Кузьменко В.А., группа ДЭ 21-24 | База данных: library_titov.db | Файл скрипта: pz3.sql")
r_info.font.name = "Arial"
r_info.font.size = Pt(10.5)
r_info.font.italic = True
r_info.font.color.rgb = RGBColor(100, 100, 100)

doc3.add_paragraph()

# 1. Intro & Task Setting
add_styled_heading(doc3, "1. Постановка задачи и обоснование нормализации", level=1)
p = doc3.add_paragraph(
    "В практической работе № 2 каталог хранился в виде единой улучшенной таблицы books_improved. "
    "Однако при расширении книжного фонда такая модель приводит к ряду серьезных противоречий и аномалий:\n"
    "1. Избыточность текстовых данных: название одного и того же издательства («Питер», «Эксмо») дублируется в сотнях строк. "
    "Это влечет перерасход памяти и провоцирует аномалии обновления (update anomalies), когда при переименовании издательства "
    "приходится модифицировать множество записей;\n"
    "2. Проблема соавторства: одна книга может быть написана несколькими соавторами (например, книга по паттернам проектирования "
    "«Банды четырех»), а один автор может являться создателем десятков произведений. Хранение нескольких авторов в одной ячейке "
    "через запятую или списком ID прямо нарушает Первую нормальную форму (атомарность данных) и не позволяет индексировать "
    "авторов или организовать надежную внешнюю ссылку;\n"
    "3. Потеря конкретных физических экземпляров: поле «Остаток» хранит только агрегированное число, что не позволяет "
    "присвоить уникальный инвентарный номер каждому реальному тому, отслеживать его физический статус (выдана, на полке, в ремонте, списана);\n"
    "4. Неустойчивость текстовых связей: текстовые наименования подвержены случайным опечаткам и вариациям написания.\n\n"
    "Цель работы: преобразовать книжный каталог в реляционную модель со связями 1:N и M:N и экспериментально доказать "
    "работоспособность механизмов ссылочной целостности SQLite (FOREIGN KEY, CASCADE, SET NULL, RESTRICT)."
)
style_paragraph(p, "Arial", 11, line_spacing=1.15)

# 2. Stage 1: Preparation & Entity Mapping
add_styled_heading(doc3, "2. Анализ прежней структуры и распределение полей", level=1)
p = doc3.add_paragraph(
    "Прежняя таблица была декомпозирована на нормализованные сущности. "
    "Распределение полей приведено в таблице:"
)
style_paragraph(p, "Arial", 11)

t_map = doc3.add_table(rows=6, cols=3)
t_map.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_map)

headers_m = ["Прежнее поле (books_improved)", "Новая таблица назначения", "Роль в реляционной модели"]
for col_idx, text in enumerate(headers_m):
    cell = t_map.cell(0, col_idx)
    cell.paragraphs[0].text = text
    style_paragraph(cell.paragraphs[0], "Arial", 10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(cell, "2B547E")

map_data = [
    ("Автор (author)", "authors, book_authors", "Вынесено в отдельный справочник authors; связь с books реализуется через таблицу book_authors (M:N)"),
    ("Издательство (publisher)", "publishers, books.publisher_id", "Вынесено в справочник publishers; в таблице books хранится суррогатный внешний ключ publisher_id (1:N)"),
    ("Название, ISBN, Год, Цена", "books", "Остаются основными библиографическими характеристиками издания в таблице books"),
    ("Остаток (stock)", "copies (вычисляемое поле)", "Поле упразднено как избыточное; текущий остаток вычисляется динамически запросом COUNT(*) по таблице copies WHERE status='доступна'"),
    ("Инвентарный номер / статус", "copies", "Новая сущность физических экземпляров: каждый экземпляр имеет уникальный инвентарный номер и персональный статус")
]

for row_idx, r_data in enumerate(map_data, start=1):
    for col_idx, val in enumerate(r_data):
        cell = t_map.cell(row_idx, col_idx)
        cell.paragraphs[0].text = val
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(cell, bg)
        style_paragraph(cell.paragraphs[0], "Arial", 9.5)

doc3.add_paragraph()

# 3. Stage 2: Design Decisions on Relationships & ON DELETE
add_styled_heading(doc3, "3. Таблица проектных решений по связям и правилам удаления (ON DELETE)", level=1)
p = doc3.add_paragraph(
    "В соответствии с требованиями методички, действие ON DELETE выбирается строго по смыслу взаимосвязи сущностей, "
    "а в схеме обоснованно применены три различных типа поведения: CASCADE, SET NULL и RESTRICT."
)
style_paragraph(p, "Arial", 11)

t_dec = doc3.add_table(rows=5, cols=4)
t_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_dec)

headers_d = ["Связь", "Кардинальность", "Выбранное действие при удалении", "Смысловое обоснование"]
for col_idx, text in enumerate(headers_d):
    cell = t_dec.cell(0, col_idx)
    cell.paragraphs[0].text = text
    style_paragraph(cell.paragraphs[0], "Arial", 10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(cell, "2B547E")

dec_data = [
    ("publishers -> books", "1:N", "ON DELETE SET NULL", 
     "Если издательство ликвидировано или удалено из справочника, сама книга физически не исчезает из фонда библиотеки. Поле publisher_id в таблице books корректно обнуляется (становится NULL)."),
    ("books -> copies", "1:N", "ON DELETE CASCADE", 
     "Физический экземпляр не имеет самостоятельного библиографического смысла в отрыве от описания книги. При списании и удалении книги из каталога все относящиеся к ней экземпляры удаляются автоматически."),
    ("books -> book_authors", "1:N", "ON DELETE CASCADE", 
     "Строка в таблице book_authors представляет собой факт участия автора в конкретной книге. При удалении книги все связующие записи теряют смысл и должны каскадно удаляться."),
    ("authors -> book_authors", "1:N", "ON DELETE RESTRICT", 
     "Запрещает удаление автора из базы данных до тех пор, пока в каталоге зарегистрированы его книги. Это защищает библиографическую базу от случайного удаления активных авторов.")
]

for row_idx, r_data in enumerate(dec_data, start=1):
    for col_idx, val in enumerate(r_data):
        cell = t_dec.cell(row_idx, col_idx)
        cell.paragraphs[0].text = val
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(cell, bg)
        style_paragraph(cell.paragraphs[0], "Arial", 9.5)

doc3.add_paragraph()

# 4. Stage 3 & 4: DDL and Population
add_styled_heading(doc3, "4. Создание связанных таблиц и наполнение данными", level=1)
p = doc3.add_paragraph(
    "Создание схемы производилось с обязательной предварительной активацией контроля внешних ключей: PRAGMA foreign_keys = ON; "
    "Для промежуточной таблицы book_authors сформирован составной первичный ключ PRIMARY KEY (book_id, author_id). "
    "Для таблицы copies задано ограничение допустимых статусов CHECK(status IN ('доступна', 'выдана', 'в ремонте', 'списана'))."
)
style_paragraph(p, "Arial", 11)

sql_ddl_pz3 = """PRAGMA foreign_keys = ON;

CREATE TABLE publishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    city TEXT CHECK(city IS NULL OR length(trim(city)) > 0)
);

CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    birth_year INTEGER CHECK(birth_year IS NULL OR (birth_year >= 1800 AND birth_year <= 2026)),
    country TEXT CHECK(country IS NULL OR length(trim(country)) > 0)
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
    isbn TEXT NOT NULL UNIQUE CHECK(length(trim(isbn)) >= 10),
    publisher_id INTEGER,
    publication_year INTEGER CHECK(publication_year IS NULL OR (publication_year >= 1500 AND publication_year <= 2026)),
    price REAL NOT NULL CHECK(price > 0),
    FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE SET NULL
);

CREATE TABLE book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE RESTRICT
);

CREATE TABLE copies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    inventory_no TEXT NOT NULL UNIQUE CHECK(length(trim(inventory_no)) > 0),
    status TEXT NOT NULL CHECK(status IN ('доступна', 'выдана', 'в ремонте', 'списана')),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);"""
add_code_block(doc3, sql_ddl_pz3)

p_pop = doc3.add_paragraph(
    "Фактический объём наполнения базы данных полностью удовлетворяет и превосходит минимальные требования методички:\n"
    "• Издательства: 5 организаций (требование: >= 4);\n"
    "• Авторы: 8 авторов (требование: >= 6);\n"
    "• Книги: 10 наименований (требование: >= 10);\n"
    "• Связи книга–автор: 12 связей; у книг «Паттерны ОО-проектирования» и «Архитектура корпоративных приложений» задано по 2 соавтора (требование: >= 12, минимум 2 книги с 2 авторами);\n"
    "• Физические экземпляры: 16 экземпляров; у 5 книг имеется от 2 до 3 экземпляров с уникальными номерами (требование: >= 15, минимум 3 книги)."
)
style_paragraph(p_pop, "Arial", 10.5, line_spacing=1.15)

# 5. Stage 5: Negative Testing Table
add_styled_heading(doc3, "5. Негативное тестирование ссылочной целостности", level=1)
p = doc3.add_paragraph(
    "Были протестированы все обязательные негативные сценарии нарушения ссылочной целостности. "
    "Зафиксированные фактические сообщения SQLite подтверждают безупречную работу ограничений:"
)
style_paragraph(p, "Arial", 11)

t_neg3 = doc3.add_table(rows=9, cols=4)
t_neg3.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_neg3)

headers_n3 = ["№", "Тест", "Ожидаемый смысл результата", "Фактический результат / Сообщение SQLite"]
for col_idx, text in enumerate(headers_n3):
    cell = t_neg3.cell(0, col_idx)
    cell.paragraphs[0].text = text
    style_paragraph(cell.paragraphs[0], "Arial", 10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(cell, "2B547E")

neg3_data = [
    ("1", "Добавить книгу со ссылкой на несуществующее издательство (publisher_id=999)", "Операция отклоняется FOREIGN KEY", "FOREIGN KEY constraint failed"),
    ("2", "Добавить связь book_authors с несуществующим book_id или author_id (book_id=999)", "Операция отклоняется FOREIGN KEY", "FOREIGN KEY constraint failed"),
    ("3", "Повторно добавить уже существующую пару book_id + author_id (1, 1)", "Операция отклоняется составным PRIMARY KEY", "UNIQUE constraint failed: book_authors.book_id, book_authors.author_id"),
    ("4", "Удалить издательство (id=3), на которое ссылаются книги", "Результат соответствует правилу ON DELETE SET NULL", "Успешно: издательство удалено; у книги id=2 publisher_id установлен в NULL"),
    ("5", "Удалить книгу (id=1), для которой есть строки book_authors", "Зависимые связи удаляются по ON DELETE CASCADE", "Успешно: книга удалена; зависимые строки в book_authors и copies каскадно удалены"),
    ("6", "Попытаться удалить автора (id=4), у которого есть книги", "Операция блокируется правилом ON DELETE RESTRICT", "FOREIGN KEY constraint failed (удаление отклонено)"),
    ("7", "Создать второй экземпляр с уже существующим inventory_no", "Операция отклоняется ограничением UNIQUE", "UNIQUE constraint failed: copies.inventory_no"),
    ("8", "Выполнить системную проверку внешних ключей PRAGMA foreign_key_check;", "При корректной базе нарушений не обнаружено", "Успешно: запрос вернул 0 строк (нарушений целостности нет)")
]

for row_idx, r_data in enumerate(neg3_data, start=1):
    for col_idx, val in enumerate(r_data):
        cell = t_neg3.cell(row_idx, col_idx)
        cell.paragraphs[0].text = val
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(cell, bg)
        style_paragraph(cell.paragraphs[0], "Arial", 9.5)

doc3.add_paragraph()

# 6. Stage 6: CASCADE / SET NULL / RESTRICT Verification
add_styled_heading(doc3, "6. Проверка поведения правил CASCADE, SET NULL и RESTRICT", level=1)
p = doc3.add_paragraph(
    "Для каждого из использованных в схеме действий при удалении было зафиксировано детальное состояние таблиц до и после операции:"
)
style_paragraph(p, "Arial", 11)

t_act = doc3.add_table(rows=4, cols=4)
t_act.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_act)

headers_ac = ["Правило", "Объект до удаления", "Что произошло после удаления", "Почему это соответствует смыслу модели"]
for col_idx, text in enumerate(headers_ac):
    cell = t_act.cell(0, col_idx)
    cell.paragraphs[0].text = text
    style_paragraph(cell.paragraphs[0], "Arial", 10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(cell, "2B547E")

act_data = [
    ("CASCADE", 
     "Книга id=1 («Война и мир»), имеющая 1 связь в book_authors и 2 экземпляра в copies (INV-00101, INV-00102)", 
     "Книга удалена; связанные строки в book_authors и 2 записи экземпляров в copies удалены автоматически СУБД", 
     "Физические экземпляры и факты авторства не могут существовать без библиографической записи книги. Каскад исключает зависшие «сиротские» записи."),
    ("SET NULL", 
     "Издательство id=3 («АСТ»), на которое ссылается книга id=2 («Преступление и наказание», publisher_id=3)", 
     "Издательство удалено; строка книги id=2 сохранена, но значение publisher_id стало NULL", 
     "Удаление или ликвидация издательства не аннулирует наличие книги в библиотеке. Информация о книге сохраняется, а ссылка временно очищается."),
    ("RESTRICT", 
     "Автор id=4 («Роберт Мартин»), на которого ссылаются 3 книги (id=4, 5, 10) через book_authors", 
     "Команда DELETE FROM authors WHERE id=4 была заблокирована СУБД с ошибкой FOREIGN KEY constraint failed; автор и книги не изменились", 
     "Нельзя случайно стереть автора, чьи произведения числятся в каталоге. Для удаления автора администратор сначала обязан переназначить или списать книги.")
]

for row_idx, r_data in enumerate(act_data, start=1):
    for col_idx, val in enumerate(r_data):
        cell = t_act.cell(row_idx, col_idx)
        cell.paragraphs[0].text = val
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(cell, bg)
        style_paragraph(cell.paragraphs[0], "Arial", 9.5)

doc3.add_paragraph()

# 7. Individual Extension: Option A (Genres)
add_styled_heading(doc3, "7. Индивидуальное усложнение: Вариант A (Жанры книг M:N)", level=1)
p = doc3.add_paragraph(
    "В соответствии с вариантом А спроектирована подсистема учета жанров литературы. "
    "Так как одна книга может принадлежать нескольким жанрам (например, «Компьютерная литература» и «Архитектура ПО»), "
    "а в одном жанре находится множество книг, реализована классическая реляционная связь многие-ко-многим (M:N) "
    "с использованием связующей таблицы book_genres и составного первичного ключа PRIMARY KEY (book_id, genre_id)."
)
style_paragraph(p, "Arial", 11)

sql_genres = """CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    description TEXT
);

CREATE TABLE book_genres (
    book_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE RESTRICT
);"""
add_code_block(doc3, sql_genres)

p = doc3.add_paragraph(
    "Таблица genres наполнена 4 категориями, а в таблицу book_genres добавлено 11 связей. "
    "Правило CASCADE обеспечивает автоматическую очистку связей при списании книги, "
    "а RESTRICT защищает жанры от удаления при наличии книг."
)
style_paragraph(p, "Arial", 10.5)

# Screenshots Section
add_styled_heading(doc3, "8. Подтверждающие скриншоты структуры и тестов", level=1)

if os.path.exists(os.path.join(SHOTS_DIR, "pz3_schema_diagram.png")):
    doc3.add_picture(os.path.join(SHOTS_DIR, "pz3_schema_diagram.png"), width=Inches(6.2))
    p_cap = doc3.add_paragraph("Рисунок 1 – Реляционная диаграмма связанных таблиц библиотеки и правила связей")
    style_paragraph(p_cap, "Arial", 9.5, italic=True, color_rgb=(100, 100, 100))

if os.path.exists(os.path.join(SHOTS_DIR, "pz3_test_fk.png")):
    doc3.add_picture(os.path.join(SHOTS_DIR, "pz3_test_fk.png"), width=Inches(6.2))
    p_cap = doc3.add_paragraph("Рисунок 2 – Проверка ссылочной целостности и фиксация сообщений FOREIGN KEY в SQLite")
    style_paragraph(p_cap, "Arial", 9.5, italic=True, color_rgb=(100, 100, 100))

# Conclusion
add_styled_heading(doc3, "9. Вывод", level=1)
p_concl3 = doc3.add_paragraph(
    "В ходе выполнения Практической работы № 3 книжный каталог был успешно преобразован из плоской таблицы "
    "в полноценную связанную реляционную модель. По результатам работы сделаны следующие выводы:\n\n"
    "1. Устранение избыточности: вынесение авторов и издательств в самостоятельные сущности устранило дублирование "
    "строковых данных. Название издательства хранится строго в одном месте, что гарантирует целостность при обновлении "
    "и исключает вариативность написания одного бренда.\n\n"
    "2. Необходимость промежуточных таблиц при M:N: в реляционной модели реляционные таблицы не могут хранить списки "
    "или массивы значений в одном поле (нарушение 1НФ). Связующие таблицы book_authors и book_genres с составными первичными "
    "ключами позволяют устанавливать неограниченное число связей, индексировать каждую сторону связи и на уровне СУБД "
    "блокировать попытки повторной привязки той же пары объектов.\n\n"
    "3. Безопасность правил удаления: выбор правила зависит от жизненного цикла зависимого объекта. "
    "Для слабо связанных справочников идеален ON DELETE SET NULL (книга остается в каталоге при удалении издателя). "
    "Для жестко зависимых объектов (экземпляры copies, записи соавторства) обязателен ON DELETE CASCADE для предотвращения «зависших сиротских» строк. "
    "Для базовых справочников (authors, genres) наиболее безопасен ON DELETE RESTRICT, предотвращающий случайное удаление используемых данных.\n\n"
    "4. Ошибки, блокируемые ядром СУБД: теперь SQLite аппаратно блокирует ввод несуществующих внешних ключей, дублирование соавторов, "
    "ввод некорректных статусов физических экземпляров и повреждение дерева зависимостей при удалении.\n\n"
    "5. Новые сложности реляционной схемы: переход к связанной структуре повышает требования к проектированию: "
    "необходимо строго контролировать порядок создания/удаления таблиц и вставок данных, использовать операторы JOIN "
    "для построения результирующих выборок и явно активировать контроль внешних ключей директивой PRAGMA foreign_keys = ON."
)
style_paragraph(p_concl3, "Arial", 11, line_spacing=1.15)

doc3.save(os.path.join(BASE_DIR, "Отчет_ПЗ3_Титов.docx"))
print("Отчет_ПЗ3_Титов.docx created successfully!")


# ==============================================================================
# REPORT 4: Отчет_ПЗ4_Титов.docx
# ==============================================================================
print("Creating Отчет_ПЗ4_Титов.docx...")
doc4 = docx.Document()

for s in doc4.sections:
    s.top_margin = Inches(0.8)
    s.bottom_margin = Inches(0.8)
    s.left_margin = Inches(0.8)
    s.right_margin = Inches(0.8)

title_p = doc4.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title_p.add_run("ОТЧЁТ ПО ПРАКТИЧЕСКОМУ ЗАНЯТИЮ № 4\n")
r.font.name = "Arial"
r.font.size = Pt(16)
r.font.bold = True
r.font.color.rgb = RGBColor(20, 50, 100)

r_sub = title_p.add_run("«Построение и заполнение реляционных баз данных по схемам»\n")
r_sub.font.name = "Arial"
r_sub.font.size = Pt(13)
r_sub.font.bold = True
r_sub.font.color.rgb = RGBColor(60, 60, 60)

r_info = title_p.add_run("Студент: Кузьменко В.А., группа ДЭ 21-24 | Базы: computer_firm.db, study_process.db | Скрипты: pz4_computer_firm.sql, pz4_study_process.sql")
r_info.font.name = "Arial"
r_info.font.size = Pt(10)
r_info.font.italic = True
r_info.font.color.rgb = RGBColor(100, 100, 100)

doc4.add_paragraph()

# Part 1: Computer Firm
add_styled_heading(doc4, "1. Часть 1: База данных «Компьютерная фирма» (Computer Firm)", level=1)
p = doc4.add_paragraph(
    "В первой части практического занятия требовалось построить и заполнить базу данных по классической схеме "
    "«Компьютерная фирма», состоящей из четырех взаимосвязанных таблиц:\n"
    "• Product(maker, model, type) — каталог производимой техники с указанием фирмы-производителя и типа устройства;\n"
    "• PC(code, model, speed, ram, hd, cd, price) — конфигурация и стоимость персональных компьютеров;\n"
    "• Laptop(code, model, speed, ram, hd, price, screen) — конфигурация и стоимость ноутбуков;\n"
    "• Printer(code, model, color, type, price) — характеристики и стоимость принтеров.\n\n"
    "Схема была адаптирована под диалект SQLite с обеспечением ссылочной целостности: "
    "в таблицах PC, Laptop и Printer поле model является внешним ключом к таблице Product(model) "
    "с правилом каскадного удаления ON DELETE CASCADE. Данные полностью импортированы из файла Компьютерная фирма.xlsx."
)
style_paragraph(p, "Arial", 11, line_spacing=1.15)

sql_ddl_comp = """PRAGMA foreign_keys = ON;

CREATE TABLE Product (
    maker VARCHAR(10) NOT NULL,
    model VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50) NOT NULL CHECK(type IN ('PC', 'Laptop', 'Printer'))
);

CREATE TABLE PC (
    code INT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    speed SMALLINT NOT NULL CHECK(speed > 0),
    ram SMALLINT NOT NULL CHECK(ram > 0),
    hd REAL NOT NULL CHECK(hd > 0),
    cd VARCHAR(10) NOT NULL,
    price REAL CHECK(price IS NULL OR price >= 0),
    FOREIGN KEY (model) REFERENCES Product(model) ON DELETE CASCADE
);

CREATE TABLE Laptop (
    code INT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    speed SMALLINT NOT NULL CHECK(speed > 0),
    ram SMALLINT NOT NULL CHECK(ram > 0),
    hd REAL NOT NULL CHECK(hd > 0),
    price REAL CHECK(price IS NULL OR price >= 0),
    screen TINYINT NOT NULL CHECK(screen > 0),
    FOREIGN KEY (model) REFERENCES Product(model) ON DELETE CASCADE
);

CREATE TABLE Printer (
    code INT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    color CHAR(1) NOT NULL CHECK(color IN ('y', 'n')),
    type VARCHAR(10) NOT NULL CHECK(type IN ('Laser', 'Jet', 'Matrix')),
    price REAL CHECK(price IS NULL OR price >= 0),
    FOREIGN KEY (model) REFERENCES Product(model) ON DELETE CASCADE
);"""
add_code_block(doc4, sql_ddl_comp)

p = doc4.add_paragraph("Пример аналитического запроса к базе «Компьютерная фирма»:")
style_paragraph(p, "Arial", 11, bold=True)

sql_comp_q = """-- Вывести производителя, модель, скорость, память и цену ПК с жестким диском >= 10 Гб
SELECT p.maker, pc.model, pc.speed, pc.ram, pc.hd, pc.price
FROM Product p
JOIN PC pc ON p.model = pc.model
WHERE pc.hd >= 10.0
ORDER BY pc.price DESC;"""
add_code_block(doc4, sql_comp_q)

if os.path.exists(os.path.join(SHOTS_DIR, "pz4_comp_data.png")):
    doc4.add_picture(os.path.join(SHOTS_DIR, "pz4_comp_data.png"), width=Inches(6.2))
    p_cap = doc4.add_paragraph("Рисунок 1 – Результат выполнения аналитического запроса в базе computer_firm.db")
    style_paragraph(p_cap, "Arial", 9.5, italic=True, color_rgb=(100, 100, 100))

# Part 2: Educational Process DB
add_styled_heading(doc4, "2. Часть 2: Проектирование и реализация БД «Учебный процесс»", level=1)
p = doc4.add_paragraph(
    "Во второй части работы требовалось спроектировать и заполнить реляционную базу данных учебного процесса, "
    "включающую учебные группы, дисциплины, преподавателей, студентов и электронный журнал посещаемости занятий. "
    "Для достижения третьей нормальной формы (3НФ) и исключения аномалий разработана структура из 6 таблиц:"
)
style_paragraph(p, "Arial", 11)

t_sch4 = doc4.add_table(rows=7, cols=3)
t_sch4.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_sch4)

headers_s4 = ["Таблица", "Ключи и связи", "Назначение и ограничения целостности"]
for col_idx, text in enumerate(headers_s4):
    cell = t_sch4.cell(0, col_idx)
    cell.paragraphs[0].text = text
    style_paragraph(cell.paragraphs[0], "Arial", 10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(cell, "2B547E")

sch4_data = [
    ("study_groups", "PK (id)", "Учебные группы (ДЭ 21-24, ДЭ 22-24, ДЭ 23-24, ДЭ 24-24, ДЭ 25-24); курс, факультет; UNIQUE(name)"),
    ("disciplines", "PK (id)", "Учебные дисциплины (Базы данных, ОС, Сети и др.); объем часов CHECK(hours>0); форма отчетности"),
    ("teachers", "PK (id)", "Профессорско-преподавательский состав кафедр; ученая степень, должность"),
    ("students", "PK (id), FK -> study_groups", "Студенты университета: ФИО, номер зачетной книжки UNIQUE, статус обучения; ON DELETE RESTRICT"),
    ("lessons", "PK (id), FK -> groups, disciplines, teachers", "Расписание занятий: дата YYYY-MM-DD, тема, тип (Лекция, Практика, Лаб. работа), номер аудитории"),
    ("attendance", "PK (id), FK -> lessons, students", "Журнал посещаемости и текущих оценок: UNIQUE(lesson_id, student_id), статус посещения, оценка (2..5), примечание")
]

for row_idx, r_data in enumerate(sch4_data, start=1):
    for col_idx, val in enumerate(r_data):
        cell = t_sch4.cell(row_idx, col_idx)
        cell.paragraphs[0].text = val
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(cell, bg)
        style_paragraph(cell.paragraphs[0], "Arial", 9.5)

doc4.add_paragraph()

p_fill = doc4.add_paragraph(
    "Наполнение базы данных «Учебный процесс»:\n"
    "• Все 114 реальных студентов из предоставленного файла Студенты.xlsx были полностью импортированы "
    "и распределены по соответствующим 5 учебным группам (ДЭ 21-24, ДЭ 22-24, ДЭ 23-24, ДЭ 24-24, ДЭ 25-24). "
    "Каждому студенту сгенерирован уникальный шифр зачетной книжки (например, ЗБ-2101, ЗБ-2201 и т.д.);\n"
    "• Внесены 5 ключевых дисциплин и преподаватели соответствующих кафедр;\n"
    "• Сформировано расписание из 10 проведенных занятий;\n"
    "• Журнал attendance заполнен реальными отметками посещаемости (48 записей) для практических занятий групп ДЭ 21-24 и ДЭ 22-24 "
    "с дифференциацией статусов («Присутствовал», «Отсутствовал (уважительная)», «Отсутствовал (неуважительная)») и оценок."
)
style_paragraph(p_fill, "Arial", 10.5, line_spacing=1.15)

p = doc4.add_paragraph("SQL-запрос формирования сводной ведомости посещаемости:")
style_paragraph(p, "Arial", 11, bold=True)

sql_att_q = """-- Ведомость посещаемости занятия по базам данных (группа ДЭ 21-24)
SELECT s.record_book_no AS "Зачетка",
       s.full_name AS "ФИО студента",
       a.status AS "Статус",
       coalesce(a.mark, '-') AS "Оценка",
       coalesce(a.note, '') AS "Примечание"
FROM attendance a
JOIN lessons l ON a.lesson_id = l.id
JOIN students s ON a.student_id = s.id
WHERE l.id = 2
ORDER BY s.full_name;"""
add_code_block(doc4, sql_att_q)

if os.path.exists(os.path.join(SHOTS_DIR, "pz4_study_query.png")):
    doc4.add_picture(os.path.join(SHOTS_DIR, "pz4_study_query.png"), width=Inches(6.2))
    p_cap = doc4.add_paragraph("Рисунок 2 – Журнал посещаемости занятия по базам данных в DB Browser")
    style_paragraph(p_cap, "Arial", 9.5, italic=True, color_rgb=(100, 100, 100))

# Conclusion
add_styled_heading(doc4, "3. Вывод", level=1)
p_concl4 = doc4.add_paragraph(
    "В ходе выполнения Практического занятия № 4 были успешно решены две масштабные задачи реляционного моделирования:\n\n"
    "1. База данных «Компьютерная фирма» была построена в строгом соответствии с представленной схемой. "
    "Успешно сопоставлены типы данных исходного диалекта со стандартами SQLite, реализованы каскадные внешние ключи "
    "и перенесен полный массив данных из Excel-источника. Написанные аналитические SQL-запросы подтвердили "
    "удобство выполнения агрегатных вычислений и многотабличных соединений (JOIN).\n\n"
    "2. База данных «Учебный процесс» была спроектирована «с нуля» на основе предметных требований. "
    "Декомпозиция предметной области на 6 связанных таблиц позволила надежно связать контингент из 114 студентов "
    "с учебным планом, преподавателями и электронным журналом посещаемости. Применение составного уникального ограничения "
    "UNIQUE(lesson_id, student_id) в таблице attendance гарантирует невозможность повторного внесения студента на одно и то же занятие, "
    "а внешние ключи с правилом RESTRICT на группы защищают списочный состав от случайного удаления."
)
style_paragraph(p_concl4, "Arial", 11, line_spacing=1.15)

doc4.save(os.path.join(BASE_DIR, "Отчет_ПЗ4_Титов.docx"))
print("Отчет_ПЗ4_Титов.docx created successfully!")

# ==============================================================================
# REPORT 5: Отчет_ПЗ5_Кузьменко.docx
# ==============================================================================
print("Creating Отчет_ПЗ5_Кузьменко.docx...")
doc5 = docx.Document()
add_styled_heading(doc5, "ОТЧЁТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 5", level=1)
doc5.add_paragraph("Тема: CRUD-приложение на Python (sqlite3)")
doc5.add_paragraph("Реализованы функции: Create, Read, Update, Delete для таблицы товаров.")
add_code_block(doc5, open('pz5_crud.py', encoding='utf-8').read())
doc5.save(os.path.join(BASE_DIR, "Отчет_ПЗ5_Кузьменко.docx"))

# ==============================================================================
# REPORT 6: Отчет_ПЗ6_Кузьменко.docx
# ==============================================================================
print("Creating Отчет_ПЗ6_Кузьменко.docx...")
doc6 = docx.Document()
add_styled_heading(doc6, "ОТЧЁТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 6", level=1)
doc6.add_paragraph("Тема: Аналитическая статистика на Python")
add_code_block(doc6, open('pz6_stats.py', encoding='utf-8').read())
doc6.save(os.path.join(BASE_DIR, "Отчет_ПЗ6_Кузьменко.docx"))

# ==============================================================================
# REPORT 7: Отчет_ПЗ7_Кузьменко.docx
# ==============================================================================
print("Creating Отчет_ПЗ7_Кузьменко.docx...")
doc7 = docx.Document()
add_styled_heading(doc7, "ОТЧЁТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 7", level=1)
doc7.add_paragraph("Тема: Система учета платной парковки")
add_code_block(doc7, open('pz7_parking.sql', encoding='utf-8').read())
doc7.save(os.path.join(BASE_DIR, "Отчет_ПЗ7_Кузьменко.docx"))

print("All reports created successfully!")

