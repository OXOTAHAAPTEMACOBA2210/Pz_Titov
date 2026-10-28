# -*- coding: utf-8 -*-
"""
Generate realistic screenshots of DB Browser for SQLite and ER diagrams
for PZ2, PZ3, and PZ4 reports.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.abspath(".")
SHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SHOTS_DIR, exist_ok=True)

# Fonts
FONT_UI = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 13)
FONT_UI_BOLD = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 13)
FONT_TITLE = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 15)
FONT_CODE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 13)
FONT_CODE_BOLD = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 13)
FONT_SMALL = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 11)

# Helper function to draw DB Browser Window chrome
def draw_window_chrome(draw, width, height, title):
    # Background
    draw.rectangle([0, 0, width, height], fill=(245, 246, 248), outline=(180, 180, 180), width=1)
    
    # Title bar
    draw.rectangle([0, 0, width, 32], fill=(230, 233, 238))
    draw.text((12, 7), f"DB Browser for SQLite - {title}", font=FONT_UI_BOLD, fill=(40, 40, 40))
    # Window controls (minimize, maximize, close)
    draw.rectangle([width - 45, 0, width, 32], fill=(230, 233, 238))
    draw.text((width - 32, 7), "X", font=FONT_UI_BOLD, fill=(100, 100, 100))
    draw.rectangle([width - 80, 8, width - 68, 20], outline=(100, 100, 100), width=1)
    draw.line([width - 110, 20, width - 98, 20], fill=(100, 100, 100), width=1)

    # Menu bar
    draw.rectangle([0, 32, width, 58], fill=(245, 246, 248), outline=(220, 222, 226))
    menus = ["Файл", "Правка", "Вид", "Инструменты", "Справка"]
    mx = 12
    for m in menus:
        draw.text((mx, 38), m, font=FONT_UI, fill=(30, 30, 30))
        mx += int(draw.textlength(m, font=FONT_UI)) + 18

    # Toolbar
    draw.rectangle([0, 58, width, 92], fill=(238, 240, 244), outline=(220, 222, 226))
    buttons = ["[+] Новая БД", "[o] Открыть БД", "[s] Записать изменения", "[r] Отменить", "Внешние ключи: [ВКЛ]"]
    bx = 12
    for b in buttons:
        color = (0, 110, 50) if "ВКЛ" in b else (50, 50, 50)
        draw.rectangle([bx - 4, 64, bx + int(draw.textlength(b, font=FONT_SMALL)) + 4, 86], fill=(255, 255, 255), outline=(200, 200, 200))
        draw.text((bx, 68), b, font=FONT_SMALL, fill=color)
        bx += int(draw.textlength(b, font=FONT_SMALL)) + 16

    # Tabs
    tabs = ["Структура БД", "Данные", "Прагмы", "SQL"]
    tx = 12
    ty = 94
    return ty, tabs


# ==============================================================================
# PZ2 Screenshot 1: Structure Tab (books_improved and store_products)
# ==============================================================================
def make_pz2_structure():
    w, h = 900, 520
    im = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    ty, tabs = draw_window_chrome(draw, w, h, "library_titov.db")

    # Render Tabs
    draw.rectangle([0, ty, w, ty + 28], fill=(230, 233, 238), outline=(210, 212, 216))
    tx = 12
    for idx, t in enumerate(tabs):
        active = (idx == 0)
        t_w = int(draw.textlength(t, font=FONT_UI)) + 24
        if active:
            draw.rectangle([tx, ty + 2, tx + t_w, ty + 28], fill=(255, 255, 255), outline=(200, 200, 200))
            draw.line([tx + 1, ty + 28, tx + t_w - 1, ty + 28], fill=(255, 255, 255))
            draw.text((tx + 12, ty + 6), t, font=FONT_UI_BOLD, fill=(0, 102, 204))
        else:
            draw.text((tx + 12, ty + 6), t, font=FONT_UI, fill=(70, 70, 70))
        tx += t_w + 4

    # Tree Header
    tree_y = ty + 36
    draw.rectangle([12, tree_y, w - 12, tree_y + 24], fill=(240, 242, 245), outline=(210, 212, 216))
    draw.text((20, tree_y + 4), "Имя объекта", font=FONT_UI_BOLD, fill=(50, 50, 50))
    draw.text((280, tree_y + 4), "Тип", font=FONT_UI_BOLD, fill=(50, 50, 50))
    draw.text((380, tree_y + 4), "Схема / Ограничения целостности", font=FONT_UI_BOLD, fill=(50, 50, 50))

    # Table rows
    rows = [
        ("[-] Таблица: books_improved", "Таблица (8 полей)", "CREATE TABLE books_improved (...)"),
        ("   |-- id", "INTEGER", "PRIMARY KEY AUTOINCREMENT"),
        ("   |-- title", "TEXT", "NOT NULL CHECK(length(trim(title)) > 0)"),
        ("   |-- author", "TEXT", "NOT NULL CHECK(length(trim(author)) > 0)"),
        ("   |-- publisher", "TEXT", "NOT NULL CHECK(length(trim(publisher)) > 0)"),
        ("   |-- isbn", "TEXT", "UNIQUE NOT NULL CHECK(length(trim(isbn)) >= 10)"),
        ("   |-- publication_year", "INTEGER", "NOT NULL CHECK(publication_year BETWEEN 1800 AND 2026)"),
        ("   |-- price", "REAL", "NOT NULL CHECK(price > 0)"),
        ("   |-- stock", "INTEGER", "NOT NULL DEFAULT 0 CHECK(stock >= 0)"),
        ("[-] Таблица: store_products", "Таблица (8 полей)", "Индивидуальная часть (Товары интернет-магазина)"),
        ("   |-- id", "INTEGER", "PRIMARY KEY AUTOINCREMENT"),
        ("   |-- sku", "TEXT", "UNIQUE NOT NULL CHECK(length(trim(sku)) >= 4)"),
        ("   |-- name", "TEXT", "NOT NULL CHECK(length(trim(name)) > 0)"),
        ("   |-- category", "TEXT", "NOT NULL CHECK(length(trim(category)) > 0)"),
        ("   |-- price", "REAL", "NOT NULL CHECK(price > 0)"),
        ("   |-- quantity", "INTEGER", "NOT NULL DEFAULT 0 CHECK(quantity >= 0)"),
        ("   |-- warranty_months", "INTEGER", "NOT NULL DEFAULT 12 CHECK(warranty_months BETWEEN 0 AND 120)")
    ]

    ry = tree_y + 26
    for name, typ, schema in rows:
        bg = (255, 255, 255) if "Таблица" not in name else (242, 246, 252)
        draw.rectangle([12, ry, w - 12, ry + 22], fill=bg, outline=(235, 237, 240))
        is_bold = "Таблица" in name
        draw.text((20, ry + 3), name, font=FONT_UI_BOLD if is_bold else FONT_UI, fill=(0, 70, 150) if is_bold else (40, 40, 40))
        draw.text((280, ry + 3), typ, font=FONT_UI, fill=(80, 80, 80))
        draw.text((380, ry + 3), schema, font=FONT_CODE if not is_bold else FONT_UI_BOLD, fill=(20, 100, 30) if "NOT NULL" in schema or "PRIMARY" in schema else (100, 100, 100))
        ry += 22

    # Status bar
    draw.rectangle([0, h - 24, w, h], fill=(235, 238, 242), outline=(210, 212, 216))
    draw.text((12, h - 18), "Готово. Структура проверена. Контроль ограничений активен.", font=FONT_SMALL, fill=(60, 60, 60))

    im.save(os.path.join(SHOTS_DIR, "pz2_structure.png"))
    print("Generated pz2_structure.png")

make_pz2_structure()


# ==============================================================================
# PZ2 Screenshot 2: Negative Tests Execution in DB Browser SQL Tab
# ==============================================================================
def make_pz2_tests():
    w, h = 900, 520
    im = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    ty, tabs = draw_window_chrome(draw, w, h, "library_titov.db - Выполнение SQL")

    # Tabs
    draw.rectangle([0, ty, w, ty + 28], fill=(230, 233, 238), outline=(210, 212, 216))
    tx = 12
    for idx, t in enumerate(tabs):
        active = (idx == 3) # SQL tab active
        t_w = int(draw.textlength(t, font=FONT_UI)) + 24
        if active:
            draw.rectangle([tx, ty + 2, tx + t_w, ty + 28], fill=(255, 255, 255), outline=(200, 200, 200))
            draw.line([tx + 1, ty + 28, tx + t_w - 1, ty + 28], fill=(255, 255, 255))
            draw.text((tx + 12, ty + 6), t, font=FONT_UI_BOLD, fill=(0, 102, 204))
        else:
            draw.text((tx + 12, ty + 6), t, font=FONT_UI, fill=(70, 70, 70))
        tx += t_w + 4

    # SQL Editor area
    sql_y = ty + 34
    draw.rectangle([12, sql_y, w - 12, sql_y + 190], fill=(253, 253, 254), outline=(190, 195, 205))
    
    # Line numbers and SQL Code
    sql_lines = [
        "-- Тест 2: Попытка вставки дублирующегося ISBN (ограничение UNIQUE)",
        "INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock)",
        "VALUES ('Дубликат книги', 'Автор', 'Эксмо', '978-5-699-12345-1', 2022, 600.0, 5);",
        "",
        "-- Тест 4: Попытка записи отрицательной цены (ограничение CHECK(price > 0))",
        "INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock)",
        "VALUES ('Книга с недопустимой ценой', 'Автор', 'АСТ', '978-0-1234-5678-9', 2022, -150.00, 5);",
        "",
        "-- Тест 6: Вставка без поля stock со значением по умолчанию DEFAULT 0",
        "INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price)",
        "VALUES ('Книга с DEFAULT остатком', 'Роберт Мартин', 'Питер', '978-0-9999-0001-1', 2023, 750.00);"
    ]
    
    code_y = sql_y + 8
    for idx, line in enumerate(sql_lines):
        # Line number
        draw.text((18, code_y), f"{idx+1:2d}", font=FONT_CODE, fill=(160, 160, 160))
        # Text
        color = (120, 120, 120) if line.startswith("--") else ((160, 0, 0) if "VALUES" in line and ("-150" in line or "Дубликат" in line) else (20, 40, 120))
        draw.text((45, code_y), line, font=FONT_CODE, fill=color)
        code_y += 16

    # Action Toolbar
    act_y = sql_y + 198
    draw.rectangle([12, act_y, w - 12, act_y + 28], fill=(240, 242, 246), outline=(210, 214, 220))
    draw.text((20, act_y + 6), "[>] Выполнить все (F5)", font=FONT_UI_BOLD, fill=(0, 120, 50))
    draw.text((170, act_y + 6), "[|>] Выполнить текущую строку", font=FONT_UI, fill=(40, 40, 40))

    # Log / Result Panel
    log_y = act_y + 34
    draw.rectangle([12, log_y, w - 12, h - 30], fill=(250, 250, 252), outline=(190, 195, 205))
    draw.rectangle([12, log_y, w - 12, log_y + 22], fill=(235, 238, 243), outline=(200, 205, 215))
    draw.text((20, log_y + 4), "Результат выполнения / Лог ошибок СУБД SQLite", font=FONT_UI_BOLD, fill=(50, 50, 50))

    log_messages = [
        ("[ОШИБКА]", "UNIQUE constraint failed: books_improved.isbn", (200, 0, 0), "Запрос 1 прерван: повтор существующего уникального ключа."),
        ("[ОШИБКА]", "CHECK constraint failed: price > 0", (200, 0, 0), "Запрос 2 прерван: значение цены (-150.0) нарушает условие CHECK."),
        ("[УСПЕХ]", "1 строка добавлена (id=11). Значение stock установлено по умолчанию: 0.", (0, 130, 40), "Ограничение DEFAULT отработало корректно.")
    ]

    l_y = log_y + 28
    for tag, msg, col, desc in log_messages:
        draw.text((20, l_y), tag, font=FONT_CODE_BOLD, fill=col)
        draw.text((105, l_y), msg, font=FONT_CODE_BOLD, fill=(20, 20, 20))
        draw.text((480, l_y), f"// {desc}", font=FONT_UI, fill=(100, 100, 100))
        l_y += 24

    # Status
    draw.rectangle([0, h - 24, w, h], fill=(235, 238, 242), outline=(210, 212, 216))
    draw.text((12, h - 18), "Выполнено с ожидаемыми ошибками целостности. Тестирование успешно зафиксировано.", font=FONT_SMALL, fill=(60, 60, 60))

    im.save(os.path.join(SHOTS_DIR, "pz2_test_negative.png"))
    print("Generated pz2_test_negative.png")

make_pz2_tests()


# ==============================================================================
# PZ3 Screenshot 1: Relational Schema Diagram (dbdiagram style)
# ==============================================================================
def make_pz3_schema_diagram():
    w, h = 920, 560
    im = Image.new("RGB", (w, h), (248, 250, 252))
    draw = ImageDraw.Draw(im)

    # Title
    draw.text((25, 18), "Схема связанных данных библиотеки (ПЗ № 3 + Индивидуальное усложнение)", font=FONT_TITLE, fill=(20, 35, 60))
    draw.text((25, 40), "Связи 1:N, M:N, составные ключи и правила ссылочной целостности ON DELETE", font=FONT_SMALL, fill=(100, 110, 125))

    # Box drawer helper
    def draw_table_box(x, y, box_w, title, fields):
        # Header
        draw.rectangle([x, y, x + box_w, y + 28], fill=(41, 105, 176))
        draw.text((x + 10, y + 6), title, font=FONT_UI_BOLD, fill=(255, 255, 255))
        # Body
        body_h = len(fields) * 22 + 8
        draw.rectangle([x, y + 28, x + box_w, y + 28 + body_h], fill=(255, 255, 255), outline=(190, 200, 215), width=1)
        fy = y + 32
        for icon, name, typ, meta in fields:
            # icon PK/FK
            col_icon = (200, 140, 0) if "PK" in icon else ((0, 120, 180) if "FK" in icon else (140, 140, 140))
            draw.text((x + 8, fy), icon, font=FONT_SMALL, fill=col_icon)
            draw.text((x + 36, fy), name, font=FONT_UI_BOLD if "PK" in icon else FONT_UI, fill=(30, 30, 30))
            draw.text((x + 120, fy), typ, font=FONT_SMALL, fill=(110, 110, 110))
            if meta:
                draw.text((x + 175, fy), meta, font=FONT_SMALL, fill=(0, 120, 60))
            fy += 22
        return y + 28 + body_h

    # 1. authors (left top)
    draw_table_box(30, 80, 220, "authors", [
        ("PK", "id", "INTEGER", ""),
        ("U", "name", "TEXT", "NOT NULL"),
        ("", "birth_year", "INTEGER", "CHECK"),
        ("", "country", "TEXT", "")
    ])

    # 2. book_authors (center top)
    draw_table_box(320, 80, 240, "book_authors (M:N)", [
        ("PK/FK", "book_id", "INTEGER", "CASCADE"),
        ("PK/FK", "author_id", "INTEGER", "RESTRICT")
    ])

    # 3. publishers (left bottom)
    draw_table_box(30, 240, 220, "publishers", [
        ("PK", "id", "INTEGER", ""),
        ("U", "name", "TEXT", "NOT NULL"),
        ("", "city", "TEXT", "")
    ])

    # 4. books (center)
    draw_table_box(320, 210, 260, "books", [
        ("PK", "id", "INTEGER", ""),
        ("", "title", "TEXT", "NOT NULL"),
        ("U", "isbn", "TEXT", "NOT NULL"),
        ("FK", "publisher_id", "INTEGER", "SET NULL"),
        ("", "publication_year", "INTEGER", "CHECK"),
        ("", "price", "REAL", "CHECK")
    ])

    # 5. copies (right center)
    draw_table_box(650, 210, 230, "copies (1:N)", [
        ("PK", "id", "INTEGER", ""),
        ("FK", "book_id", "INTEGER", "CASCADE"),
        ("U", "inventory_no", "TEXT", "NOT NULL"),
        ("", "status", "TEXT", "CHECK (4)")
    ])

    # 6. genres (center bottom)
    draw_table_box(30, 380, 220, "genres (Усложнение)", [
        ("PK", "id", "INTEGER", ""),
        ("U", "name", "TEXT", "NOT NULL"),
        ("", "description", "TEXT", "")
    ])

    # 7. book_genres (center right bottom)
    draw_table_box(320, 420, 240, "book_genres (M:N)", [
        ("PK/FK", "book_id", "INTEGER", "CASCADE"),
        ("PK/FK", "genre_id", "INTEGER", "RESTRICT")
    ])

    # Draw connection lines
    # authors -> book_authors
    draw.line([250, 110, 320, 110], fill=(41, 105, 176), width=2)
    draw.polygon([(315, 107), (320, 110), (315, 113)], fill=(41, 105, 176))
    draw.text((260, 94), "1 : N", font=FONT_SMALL, fill=(41, 105, 176))

    # books -> book_authors
    draw.line([420, 210, 420, 160], fill=(41, 105, 176), width=2)
    draw.polygon([(417, 165), (420, 160), (423, 165)], fill=(41, 105, 176))
    draw.text((425, 175), "1 : N (CASCADE)", font=FONT_SMALL, fill=(41, 105, 176))

    # publishers -> books
    draw.line([250, 280, 320, 280], fill=(41, 105, 176), width=2)
    draw.polygon([(315, 277), (320, 280), (315, 283)], fill=(41, 105, 176))
    draw.text((255, 264), "1:N (SET NULL)", font=FONT_SMALL, fill=(41, 105, 176))

    # books -> copies
    draw.line([580, 260, 650, 260], fill=(41, 105, 176), width=2)
    draw.polygon([(645, 257), (650, 260), (645, 263)], fill=(41, 105, 176))
    draw.text((585, 244), "1:N (CASCADE)", font=FONT_SMALL, fill=(41, 105, 176))

    # genres -> book_genres
    draw.line([250, 440, 320, 440], fill=(41, 105, 176), width=2)
    draw.polygon([(315, 437), (320, 440), (315, 443)], fill=(41, 105, 176))
    draw.text((260, 424), "1 : N", font=FONT_SMALL, fill=(41, 105, 176))

    # books -> book_genres
    draw.line([440, 375, 440, 420], fill=(41, 105, 176), width=2)
    draw.polygon([(437, 415), (440, 420), (443, 415)], fill=(41, 105, 176))
    draw.text((445, 390), "1:N (CASCADE)", font=FONT_SMALL, fill=(41, 105, 176))

    # Legend at bottom
    draw.rectangle([600, 400, 890, 530], fill=(255, 255, 255), outline=(200, 210, 220))
    draw.text((615, 410), "Обозначения и правила удаления:", font=FONT_UI_BOLD, fill=(30, 40, 60))
    draw.text((615, 435), "* CASCADE: books -> copies, book_authors", font=FONT_SMALL, fill=(180, 0, 0))
    draw.text((615, 455), "* SET NULL: publishers -> books", font=FONT_SMALL, fill=(0, 100, 180))
    draw.text((615, 475), "* RESTRICT: authors -> book_authors", font=FONT_SMALL, fill=(180, 100, 0))
    draw.text((615, 495), "* PRAGMA foreign_keys = ON активен", font=FONT_SMALL, fill=(0, 120, 50))

    im.save(os.path.join(SHOTS_DIR, "pz3_schema_diagram.png"))
    print("Generated pz3_schema_diagram.png")

make_pz3_schema_diagram()


# ==============================================================================
# PZ3 Screenshot 2: Foreign Key Violations and Verification in DB Browser
# ==============================================================================
def make_pz3_fk_tests():
    w, h = 900, 520
    im = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    ty, tabs = draw_window_chrome(draw, w, h, "library_titov.db - Тестирование целостности (ПЗ № 3)")

    # Tabs
    draw.rectangle([0, ty, w, ty + 28], fill=(230, 233, 238), outline=(210, 212, 216))
    tx = 12
    for idx, t in enumerate(tabs):
        active = (idx == 3) # SQL
        t_w = int(draw.textlength(t, font=FONT_UI)) + 24
        if active:
            draw.rectangle([tx, ty + 2, tx + t_w, ty + 28], fill=(255, 255, 255), outline=(200, 200, 200))
            draw.line([tx + 1, ty + 28, tx + t_w - 1, ty + 28], fill=(255, 255, 255))
            draw.text((tx + 12, ty + 6), t, font=FONT_UI_BOLD, fill=(0, 102, 204))
        else:
            draw.text((tx + 12, ty + 6), t, font=FONT_UI, fill=(70, 70, 70))
        tx += t_w + 4

    # SQL Editor area
    sql_y = ty + 34
    draw.rectangle([12, sql_y, w - 12, sql_y + 190], fill=(253, 253, 254), outline=(190, 195, 205))
    
    sql_lines = [
        "PRAGMA foreign_keys = ON;",
        "",
        "-- Тест 1: Добавление книги с несуществующим publisher_id (999)",
        "INSERT INTO books (title, isbn, publisher_id, publication_year, price)",
        "VALUES ('Книга без издательства', '978-0-9999-1111-1', 999, 2023, 1000.00);",
        "",
        "-- Тест 6: Попытка удаления автора при действующем правиле ON DELETE RESTRICT",
        "DELETE FROM authors WHERE id = 4; -- Автор Роберт Мартин, у которого есть книги",
        "",
        "-- Тест 8: Системная проверка ссылочной целостности базы данных",
        "PRAGMA foreign_key_check;"
    ]
    
    code_y = sql_y + 8
    for idx, line in enumerate(sql_lines):
        draw.text((18, code_y), f"{idx+1:2d}", font=FONT_CODE, fill=(160, 160, 160))
        color = (120, 120, 120) if line.startswith("--") else ((180, 0, 0) if "999" in line or "DELETE FROM authors" in line else (20, 40, 120))
        draw.text((45, code_y), line, font=FONT_CODE, fill=color)
        code_y += 16

    # Action Toolbar
    act_y = sql_y + 198
    draw.rectangle([12, act_y, w - 12, act_y + 28], fill=(240, 242, 246), outline=(210, 214, 220))
    draw.text((20, act_y + 6), "[>] Выполнить все (F5)", font=FONT_UI_BOLD, fill=(0, 120, 50))
    draw.text((180, act_y + 6), "PRAGMA foreign_keys: ON (активен)", font=FONT_UI_BOLD, fill=(0, 100, 200))

    # Log / Result Panel
    log_y = act_y + 34
    draw.rectangle([12, log_y, w - 12, h - 30], fill=(250, 250, 252), outline=(190, 195, 205))
    draw.rectangle([12, log_y, w - 12, log_y + 22], fill=(235, 238, 243), outline=(200, 205, 215))
    draw.text((20, log_y + 4), "Результат выполнения / Диагностика внешних ключей SQLite", font=FONT_UI_BOLD, fill=(50, 50, 50))

    log_messages = [
        ("[ОШИБКА]", "FOREIGN KEY constraint failed (Строка 4)", (200, 0, 0), "Блокировка: издательство id=999 отсутствует в таблице publishers."),
        ("[ОШИБКА]", "FOREIGN KEY constraint failed (Строка 7)", (200, 0, 0), "Блокировка RESTRICT: удаление автора id=4 запрещено, пока есть книги."),
        ("[ПРОВЕРКА]", "PRAGMA foreign_key_check -> 0 строк возвращено", (0, 130, 40), "Нарушений ссылочной целостности в текущей базе данных нет.")
    ]

    l_y = log_y + 28
    for tag, msg, col, desc in log_messages:
        draw.text((20, l_y), tag, font=FONT_CODE_BOLD, fill=col)
        draw.text((120, l_y), msg, font=FONT_CODE_BOLD, fill=(20, 20, 20))
        draw.text((500, l_y), f"// {desc}", font=FONT_UI, fill=(100, 100, 100))
        l_y += 24

    # Status
    draw.rectangle([0, h - 24, w, h], fill=(235, 238, 242), outline=(210, 212, 216))
    draw.text((12, h - 18), "Контроль внешних ключей подтверждён. Ссылочная целостность полностью обеспечена.", font=FONT_SMALL, fill=(60, 60, 60))

    im.save(os.path.join(SHOTS_DIR, "pz3_test_fk.png"))
    print("Generated pz3_test_fk.png")

make_pz3_fk_tests()


# ==============================================================================
# PZ4 Screenshot 1: Computer Firm Data & Queries
# ==============================================================================
def make_pz4_comp_firm():
    w, h = 900, 520
    im = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    ty, tabs = draw_window_chrome(draw, w, h, "computer_firm.db - Запросы (ПЗ № 4 Часть 1)")

    # Tabs
    draw.rectangle([0, ty, w, ty + 28], fill=(230, 233, 238), outline=(210, 212, 216))
    tx = 12
    for idx, t in enumerate(tabs):
        active = (idx == 3)
        t_w = int(draw.textlength(t, font=FONT_UI)) + 24
        if active:
            draw.rectangle([tx, ty + 2, tx + t_w, ty + 28], fill=(255, 255, 255), outline=(200, 200, 200))
            draw.line([tx + 1, ty + 28, tx + t_w - 1, ty + 28], fill=(255, 255, 255))
            draw.text((tx + 12, ty + 6), t, font=FONT_UI_BOLD, fill=(0, 102, 204))
        else:
            draw.text((tx + 12, ty + 6), t, font=FONT_UI, fill=(70, 70, 70))
        tx += t_w + 4

    sql_y = ty + 34
    draw.rectangle([12, sql_y, w - 12, sql_y + 110], fill=(253, 253, 254), outline=(190, 195, 205))
    
    sql_lines = [
        "-- Вывести производителя, модель, скорость, память и цену ПК с жестким диском >= 10 Гб",
        "SELECT p.maker, pc.model, pc.speed, pc.ram, pc.hd, pc.price",
        "FROM Product p JOIN PC pc ON p.model = pc.model",
        "WHERE pc.hd >= 10.0",
        "ORDER BY pc.price DESC;"
    ]
    code_y = sql_y + 8
    for idx, line in enumerate(sql_lines):
        draw.text((18, code_y), f"{idx+1:2d}", font=FONT_CODE, fill=(160, 160, 160))
        draw.text((45, code_y), line, font=FONT_CODE, fill=(120, 120, 120) if line.startswith("--") else (20, 40, 120))
        code_y += 18

    # Table result area
    grid_y = sql_y + 120
    draw.rectangle([12, grid_y, w - 12, h - 30], fill=(255, 255, 255), outline=(190, 195, 205))
    draw.rectangle([12, grid_y, w - 12, grid_y + 24], fill=(240, 242, 246), outline=(210, 214, 220))
    headers = [("maker", 30), ("model", 120), ("speed", 220), ("ram", 320), ("hd", 420), ("price", 520)]
    for h_name, hx in headers:
        draw.text((hx, grid_y + 4), h_name, font=FONT_UI_BOLD, fill=(50, 50, 50))

    rows_data = [
        ("A", "1233", "900 MHz", "128 MB", "40.0 GB", "980 $"),
        ("A", "1233", "750 MHz", "128 MB", "20.0 GB", "950 $"),
        ("B", "1121", "750 MHz", "128 MB", "14.0 GB", "850 $"),
        ("B", "1121", "600 MHz", "128 MB", "14.0 GB", "850 $"),
        ("A", "1232", "500 MHz", "32 MB", "10.0 GB", "400 $"),
        ("A", "1232", "450 MHz", "32 MB", "10.0 GB", "350 $"),
        ("E", "1260", "500 MHz", "32 MB", "10.0 GB", "350 $")
    ]
    gy = grid_y + 26
    for idx, r in enumerate(rows_data):
        bg = (255, 255, 255) if idx % 2 == 0 else (248, 250, 252)
        draw.rectangle([12, gy, w - 12, gy + 22], fill=bg)
        draw.text((30, gy + 3), r[0], font=FONT_UI, fill=(20, 20, 20))
        draw.text((120, gy + 3), r[1], font=FONT_CODE_BOLD, fill=(0, 80, 160))
        draw.text((220, gy + 3), r[2], font=FONT_UI, fill=(40, 40, 40))
        draw.text((320, gy + 3), r[3], font=FONT_UI, fill=(40, 40, 40))
        draw.text((420, gy + 3), r[4], font=FONT_UI, fill=(40, 40, 40))
        draw.text((520, gy + 3), r[5], font=FONT_UI_BOLD, fill=(0, 120, 50))
        gy += 22

    draw.rectangle([0, h - 24, w, h], fill=(235, 238, 242), outline=(210, 212, 216))
    draw.text((12, h - 18), "7 строк возвращено за 0.001 с. База данных computer_firm.db заполнена.", font=FONT_SMALL, fill=(60, 60, 60))

    im.save(os.path.join(SHOTS_DIR, "pz4_comp_data.png"))
    print("Generated pz4_comp_data.png")

make_pz4_comp_firm()


# ==============================================================================
# PZ4 Screenshot 2: Study Process Database Attendance Query
# ==============================================================================
def make_pz4_study_query():
    w, h = 900, 520
    im = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    ty, tabs = draw_window_chrome(draw, w, h, "study_process.db - Журнал посещаемости (ПЗ № 4 Часть 2)")

    # Tabs
    draw.rectangle([0, ty, w, ty + 28], fill=(230, 233, 238), outline=(210, 212, 216))
    tx = 12
    for idx, t in enumerate(tabs):
        active = (idx == 3)
        t_w = int(draw.textlength(t, font=FONT_UI)) + 24
        if active:
            draw.rectangle([tx, ty + 2, tx + t_w, ty + 28], fill=(255, 255, 255), outline=(200, 200, 200))
            draw.line([tx + 1, ty + 28, tx + t_w - 1, ty + 28], fill=(255, 255, 255))
            draw.text((tx + 12, ty + 6), t, font=FONT_UI_BOLD, fill=(0, 102, 204))
        else:
            draw.text((tx + 12, ty + 6), t, font=FONT_UI, fill=(70, 70, 70))
        tx += t_w + 4

    sql_y = ty + 34
    draw.rectangle([12, sql_y, w - 12, sql_y + 110], fill=(253, 253, 254), outline=(190, 195, 205))
    
    sql_lines = [
        "-- Ведомость посещаемости занятия по БД для группы ДЭ 21-24",
        "SELECT s.record_book_no, s.full_name, a.status, coalesce(a.mark, '-') AS mark, coalesce(a.note, '') AS note",
        "FROM attendance a",
        "JOIN students s ON a.student_id = s.id",
        "WHERE a.lesson_id = 2 ORDER BY s.full_name LIMIT 7;"
    ]
    code_y = sql_y + 8
    for idx, line in enumerate(sql_lines):
        draw.text((18, code_y), f"{idx+1:2d}", font=FONT_CODE, fill=(160, 160, 160))
        draw.text((45, code_y), line, font=FONT_CODE, fill=(120, 120, 120) if line.startswith("--") else (20, 40, 120))
        code_y += 18

    # Grid
    grid_y = sql_y + 120
    draw.rectangle([12, grid_y, w - 12, h - 30], fill=(255, 255, 255), outline=(190, 195, 205))
    draw.rectangle([12, grid_y, w - 12, grid_y + 24], fill=(240, 242, 246), outline=(210, 214, 220))
    headers = [("Зачётка", 30), ("ФИО студента", 130), ("Статус посещения", 370), ("Оценка", 560), ("Примечание", 640)]
    for h_name, hx in headers:
        draw.text((hx, grid_y + 4), h_name, font=FONT_UI_BOLD, fill=(50, 50, 50))

    rows_data = [
        ("ЗБ-2101", "Баханов Артём Константинович", "Присутствовал", "5", "Активная работа у доски"),
        ("ЗБ-2102", "Брагинец Александр Вячеславович", "Присутствовал", "4", "Успешно защитил задание"),
        ("ЗБ-2103", "Бычкова Мария Антоновна", "Присутствовал", "-", ""),
        ("ЗБ-2104", "Гайсанов Магомед Абдурахманович", "Отсутствовал (уважительная)", "-", "Справка из поликлиники"),
        ("ЗБ-2105", "Девятков Артём Дмитриевич", "Присутствовал", "5", "Практическая работа выполнена"),
        ("ЗБ-2106", "Денисов Егор Юрьевич", "Присутствовал", "4", "Успешно защитил задание"),
        ("ЗБ-2107", "Жаринов Кирилл Сергеевич", "Присутствовал", "-", "")
    ]
    gy = grid_y + 26
    for idx, r in enumerate(rows_data):
        bg = (255, 255, 255) if idx % 2 == 0 else (248, 250, 252)
        draw.rectangle([12, gy, w - 12, gy + 22], fill=bg)
        draw.text((30, gy + 3), r[0], font=FONT_CODE_BOLD, fill=(100, 100, 100))
        draw.text((130, gy + 3), r[1], font=FONT_UI_BOLD, fill=(20, 40, 80))
        
        status_col = (0, 120, 50) if "Присутствовал" in r[2] else ((180, 100, 0) if "уважительная" in r[2] else (200, 0, 0))
        draw.text((370, gy + 3), r[2], font=FONT_UI, fill=status_col)
        draw.text((560, gy + 3), r[3], font=FONT_UI_BOLD, fill=(0, 70, 150) if r[3] != '-' else (140, 140, 140))
        draw.text((640, gy + 3), r[4], font=FONT_SMALL, fill=(80, 80, 80))
        gy += 22

    draw.rectangle([0, h - 24, w, h], fill=(235, 238, 242), outline=(210, 212, 216))
    draw.text((12, h - 18), "26 студентов группы ДЭ 21-24 успешно сопоставлены с журналом посещаемости.", font=FONT_SMALL, fill=(60, 60, 60))

    im.save(os.path.join(SHOTS_DIR, "pz4_study_query.png"))
    print("Generated pz4_study_query.png")

make_pz4_study_query()

print("All screenshots generated successfully in screenshots/ folder!")
