# -*- coding: utf-8 -*-
"""
Script to build all databases and export all SQL scripts for Titov:
- library_titov.db (PZ2 + PZ3)
- computer_firm.db (PZ4 Part 1)
- study_process.db (PZ4 Part 2)
- pz2.sql, pz3.sql, pz4_computer_firm.sql, pz4_study_process.sql, pz4.sql
"""
import os
import sqlite3
import zipfile
import xml.etree.ElementTree as ET

BASE_DIR = os.path.abspath(".")

print("--- Generating library_titov.db and pz2.sql, pz3.sql ---")

# ==============================================================================
# PZ 2 & PZ 3: library_titov.db
# ==============================================================================
db_library_path = os.path.join(BASE_DIR, "library_titov.db")
if os.path.exists(db_library_path):
    os.remove(db_library_path)

conn_lib = sqlite3.connect(db_library_path)
conn_lib.execute("PRAGMA foreign_keys = ON;")
cur_lib = conn_lib.cursor()

# ----------------- PZ 2 Tables -----------------
# 1. Legacy table
cur_lib.execute("""
CREATE TABLE books_legacy (
    Код_книги INTEGER PRIMARY KEY,
    Автор TEXT,
    Название TEXT,
    Издательство TEXT,
    Цена REAL,
    Остаток INTEGER
);
""")

legacy_books = [
    (1, "Лев Толстой", "Война и мир", "Эксмо", 1250.00, 15),
    (2, "Фёдор Достоевский", "Преступление и наказание", "АСТ", 850.50, 20),
    (3, "Михаил Булгаков", "Мастер и Маргарита", "Азбука", 920.00, 12),
    (4, "Александр Пушкин", "Евгений Онегин", "Питер", 650.00, 30),
    (5, "Николай Гоголь", "Мёртвые души", "Эксмо", 710.00, 8),
    (6, "Антон Чехов", "Вишнёвый сад", "АСТ", 540.00, 14),
    (7, "Иван Тургенев", "Отцы и дети", "Азбука", 680.00, 18),
    (8, "Роберт Мартин", "Чистый код", "Питер", 1850.00, 25),
    (9, "Эндрю Таненбаум", "Современные операционные системы", "Питер", 2950.00, 7),
    (10, "Дональд Кнут", "Искусство программирования", "Вильямс", 4500.00, 5)
]
cur_lib.executemany("INSERT INTO books_legacy VALUES (?, ?, ?, ?, ?, ?)", legacy_books)

# 2. Improved table
cur_lib.execute("""
CREATE TABLE books_improved (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
    author TEXT NOT NULL CHECK(length(trim(author)) > 0),
    publisher TEXT NOT NULL CHECK(length(trim(publisher)) > 0),
    isbn TEXT NOT NULL UNIQUE CHECK(length(trim(isbn)) >= 10),
    publication_year INTEGER NOT NULL CHECK(publication_year >= 1800 AND publication_year <= 2026),
    price REAL NOT NULL CHECK(price > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0)
);
""")

improved_books = [
    ("Война и мир", "Лев Толстой", "Эксмо", "978-5-699-12345-1", 2021, 1250.00, 15),
    ("Преступление и наказание", "Фёдор Достоевский", "АСТ", "978-5-17-098765-2", 2020, 850.50, 20),
    ("Мастер и Маргарита", "Михаил Булгаков", "Азбука", "978-5-389-11223-3", 2022, 920.00, 12),
    ("Евгений Онегин", "Александр Пушкин", "Питер", "978-5-4461-4455-4", 2019, 650.00, 30),
    ("Мёртвые души", "Николай Гоголь", "Эксмо", "978-5-699-55667-5", 2021, 710.00, 8),
    ("Вишнёвый сад", "Антон Чехов", "АСТ", "978-5-17-123488-6", 2018, 540.00, 14),
    ("Отцы и дети", "Иван Тургенев", "Азбука", "978-5-389-99881-7", 2022, 680.00, 18),
    ("Чистый код", "Роберт Мартин", "Питер", "978-5-4461-0987-8", 2023, 1850.00, 25),
    ("Современные операционные системы", "Эндрю Таненбаум", "Питер", "978-5-4461-1122-9", 2021, 2950.00, 7),
    ("Искусство программирования", "Дональд Кнут", "Вильямс", "978-5-8459-0081-0", 2020, 4500.00, 5)
]
cur_lib.executemany("""
INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", improved_books)

# 3. Individual table
cur_lib.execute("""
CREATE TABLE store_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE CHECK(length(trim(sku)) >= 4),
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    category TEXT NOT NULL CHECK(length(trim(category)) > 0),
    price REAL NOT NULL CHECK(price > 0),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    warranty_months INTEGER NOT NULL DEFAULT 12 CHECK(warranty_months >= 0 AND warranty_months <= 120),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1))
);
""")

store_products_data = [
    ("SKU-1001", "Игровой ноутбук ASUS ROG Strix", "Ноутбуки", 124990.00, 8, 24, 1),
    ("SKU-1002", "Смартфон Apple iPhone 15 128GB", "Смартфоны", 84990.00, 15, 12, 1),
    ("SKU-1003", "Монитор 27\" LG UltraGear 144Hz", "Мониторы", 23990.00, 12, 36, 1),
    ("SKU-1004", "Механическая клавиатура Dark Project", "Периферия", 7490.00, 25, 12, 1),
    ("SKU-1005", "Беспроводная мышь Logitech G Pro X", "Периферия", 11990.00, 18, 24, 1),
    ("SKU-1006", "Внешний SSD Kingston XS2000 1TB", "Накопители", 9890.00, 30, 60, 1),
    ("SKU-1007", "Наушники с микрофоном HyperX Cloud II", "Аудио", 8290.00, 14, 24, 1),
    ("SKU-1008", "Wi-Fi роутер Keenetic Giga KN-1011", "Сетевое оборудование", 13490.00, 9, 36, 1),
    ("SKU-1009", "Планшет Samsung Galaxy Tab S9", "Планшеты", 67990.00, 6, 12, 1),
    ("SKU-1010", "Лазерный принтер Pantum P2500W", "Оргтехника", 10490.00, 11, 12, 1)
]
cur_lib.executemany("""
INSERT INTO store_products (sku, name, category, price, quantity, warranty_months, is_active)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", store_products_data)

# ----------------- PZ 3 Relational Tables -----------------
cur_lib.execute("""
CREATE TABLE publishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    city TEXT CHECK(city IS NULL OR length(trim(city)) > 0)
);
""")

cur_lib.execute("""
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    birth_year INTEGER CHECK(birth_year IS NULL OR (birth_year >= 1800 AND birth_year <= 2026)),
    country TEXT CHECK(country IS NULL OR length(trim(country)) > 0)
);
""")

cur_lib.execute("""
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
    isbn TEXT NOT NULL UNIQUE CHECK(length(trim(isbn)) >= 10),
    publisher_id INTEGER,
    publication_year INTEGER CHECK(publication_year IS NULL OR (publication_year >= 1500 AND publication_year <= 2026)),
    price REAL NOT NULL CHECK(price > 0),
    FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE SET NULL
);
""")

cur_lib.execute("""
CREATE TABLE book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE RESTRICT
);
""")

cur_lib.execute("""
CREATE TABLE copies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    inventory_no TEXT NOT NULL UNIQUE CHECK(length(trim(inventory_no)) > 0),
    status TEXT NOT NULL CHECK(status IN ('доступна', 'выдана', 'в ремонте', 'списана')),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
""")

cur_lib.execute("""
CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    description TEXT
);
""")

cur_lib.execute("""
CREATE TABLE book_genres (
    book_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE RESTRICT
);
""")

publishers_data = [
    (1, "Питер", "Санкт-Петербург"),
    (2, "Эксмо", "Москва"),
    (3, "АСТ", "Москва"),
    (4, "Вильямс", "Москва"),
    (5, "Альпина Паблишер", "Москва")
]
cur_lib.executemany("INSERT INTO publishers (id, name, city) VALUES (?, ?, ?)", publishers_data)

authors_data = [
    (1, "Лев Толстой", 1828, "Россия"),
    (2, "Фёдор Достоевский", 1821, "Россия"),
    (3, "Михаил Булгаков", 1891, "СССР"),
    (4, "Роберт Мартин", 1952, "США"),
    (5, "Эндрю Таненбаум", 1944, "США"),
    (6, "Дональд Кнут", 1938, "США"),
    (7, "Эрих Гамма", 1961, "Швейцария"),
    (8, "Ричард Хелм", 1960, "США")
]
cur_lib.executemany("INSERT INTO authors (id, name, birth_year, country) VALUES (?, ?, ?, ?)", authors_data)

books_data = [
    (1, "Война и мир", "978-5-699-12345-1", 2, 2021, 1250.00),
    (2, "Преступление и наказание", "978-5-17-098765-2", 3, 2020, 850.50),
    (3, "Мастер и Маргарита", "978-5-389-11223-3", 2, 2022, 920.00),
    (4, "Чистый код", "978-5-4461-0987-8", 1, 2023, 1850.00),
    (5, "Идеальный программист", "978-5-4461-0555-1", 1, 2022, 1450.00),
    (6, "Современные операционные системы", "978-5-4461-1122-9", 1, 2021, 2950.00),
    (7, "Компьютерные сети", "978-5-4461-1155-7", 1, 2020, 3100.00),
    (8, "Искусство программирования. Том 1", "978-5-8459-0081-0", 4, 2020, 4500.00),
    (9, "Паттерны объектно-ориентированного проектирования", "978-5-4461-0112-2", 1, 2023, 2200.00),
    (10, "Архитектура корпоративных программных приложений", "978-5-8459-0777-2", 4, 2021, 2800.00)
]
cur_lib.executemany("INSERT INTO books (id, title, isbn, publisher_id, publication_year, price) VALUES (?, ?, ?, ?, ?, ?)", books_data)

book_authors_data = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 4),
    (6, 5),
    (7, 5),
    (8, 6),
    (9, 7),
    (9, 8),
    (10, 4),
    (10, 7)
]
cur_lib.executemany("INSERT INTO book_authors (book_id, author_id) VALUES (?, ?)", book_authors_data)

copies_data = [
    (1, 1, "INV-00101", "доступна"),
    (2, 1, "INV-00102", "выдана"),
    (3, 2, "INV-00201", "доступна"),
    (4, 2, "INV-00202", "доступна"),
    (5, 3, "INV-00301", "выдана"),
    (6, 4, "INV-00401", "доступна"),
    (7, 4, "INV-00402", "доступна"),
    (8, 4, "INV-00403", "в ремонте"),
    (9, 5, "INV-00501", "доступна"),
    (10, 6, "INV-00601", "доступна"),
    (11, 6, "INV-00602", "выдана"),
    (12, 7, "INV-00701", "доступна"),
    (13, 8, "INV-00801", "доступна"),
    (14, 9, "INV-00901", "доступна"),
    (15, 9, "INV-00902", "выдана"),
    (16, 10, "INV-01001", "доступна")
]
cur_lib.executemany("INSERT INTO copies (id, book_id, inventory_no, status) VALUES (?, ?, ?, ?)", copies_data)

genres_data = [
    (1, "Классическая литература", "Произведения признанных мировых и отечественных классиков"),
    (2, "Компьютерная литература", "Учебники и практические руководства по программированию и ИТ"),
    (3, "Программирование и архитектура", "Книги по чистому коду, паттернам и проектированию"),
    (4, "Системное администрирование и сети", "Архитектура ОС, сетевые протоколы и инфраструктура")
]
cur_lib.executemany("INSERT INTO genres (id, name, description) VALUES (?, ?, ?)", genres_data)

book_genres_data = [
    (1, 1), (2, 1), (3, 1),
    (4, 2), (4, 3),
    (5, 2), (5, 3),
    (6, 2), (6, 4),
    (7, 2), (7, 4),
    (8, 2), (8, 3),
    (9, 2), (9, 3),
    (10, 2), (10, 3)
]
cur_lib.executemany("INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)", book_genres_data)

conn_lib.commit()
conn_lib.close()
print("library_titov.db created successfully.")

# ----------------- Write pz2.sql -----------------
pz2_sql_content = """-- =====================================================================
-- ПРАКТИЧЕСКАЯ РАБОТА № 2
-- Тема: Проектирование структуры таблицы и контроль корректности данных в SQLite
-- Студент: Титов
-- Файл скрипта: pz2.sql
-- =====================================================================

-- ---------------------------------------------------------------------
-- Этап 1. Исходная таблица "Книги" (books_legacy) из ПЗ № 1
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS books_legacy;
CREATE TABLE books_legacy (
    Код_книги INTEGER PRIMARY KEY,
    Автор TEXT,
    Название TEXT,
    Издательство TEXT,
    Цена REAL,
    Остаток INTEGER
);

INSERT INTO books_legacy VALUES (1, 'Лев Толстой', 'Война и мир', 'Эксмо', 1250.00, 15);
INSERT INTO books_legacy VALUES (2, 'Фёдор Достоевский', 'Преступление и наказание', 'АСТ', 850.50, 20);
INSERT INTO books_legacy VALUES (3, 'Михаил Булгаков', 'Мастер и Маргарита', 'Азбука', 920.00, 12);
INSERT INTO books_legacy VALUES (4, 'Александр Пушкин', 'Евгений Онегин', 'Питер', 650.00, 30);
INSERT INTO books_legacy VALUES (5, 'Николай Гоголь', 'Мёртвые души', 'Эксмо', 710.00, 8);
INSERT INTO books_legacy VALUES (6, 'Антон Чехов', 'Вишнёвый сад', 'АСТ', 540.00, 14);
INSERT INTO books_legacy VALUES (7, 'Иван Тургенев', 'Отцы и дети', 'Азбука', 680.00, 18);
INSERT INTO books_legacy VALUES (8, 'Роберт Мартин', 'Чистый код', 'Питер', 1850.00, 25);
INSERT INTO books_legacy VALUES (9, 'Эндрю Таненбаум', 'Современные операционные системы', 'Питер', 2950.00, 7);
INSERT INTO books_legacy VALUES (10, 'Дональд Кнут', 'Искусство программирования', 'Вильямс', 4500.00, 5);

-- ---------------------------------------------------------------------
-- Этапы 3-5. Проектирование и создание улучшенной таблицы (books_improved)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS books_improved;
CREATE TABLE books_improved (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
    author TEXT NOT NULL CHECK(length(trim(author)) > 0),
    publisher TEXT NOT NULL CHECK(length(trim(publisher)) > 0),
    isbn TEXT NOT NULL UNIQUE CHECK(length(trim(isbn)) >= 10),
    publication_year INTEGER NOT NULL CHECK(publication_year >= 1800 AND publication_year <= 2026),
    price REAL NOT NULL CHECK(price > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0)
);

INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock) VALUES
('Война и мир', 'Лев Толстой', 'Эксмо', '978-5-699-12345-1', 2021, 1250.00, 15),
('Преступление и наказание', 'Фёдор Достоевский', 'АСТ', '978-5-17-098765-2', 2020, 850.50, 20),
('Мастер и Маргарита', 'Михаил Булгаков', 'Азбука', '978-5-389-11223-3', 2022, 920.00, 12),
('Евгений Онегин', 'Александр Пушкин', 'Питер', '978-5-4461-4455-4', 2019, 650.00, 30),
('Мёртвые души', 'Николай Гоголь', 'Эксмо', '978-5-699-55667-5', 2021, 710.00, 8),
('Вишнёвый сад', 'Антон Чехов', 'АСТ', '978-5-17-123488-6', 2018, 540.00, 14),
('Отцы и дети', 'Иван Тургенев', 'Азбука', '978-5-389-99881-7', 2022, 680.00, 18),
('Чистый код', 'Роберт Мартин', 'Питер', '978-5-4461-0987-8', 2023, 1850.00, 25),
('Современные операционные системы', 'Эндрю Таненбаум', 'Питер', '978-5-4461-1122-9', 2021, 2950.00, 7),
('Искусство программирования', 'Дональд Кнут', 'Вильямс', '978-5-8459-0081-0', 2020, 4500.00, 5);

-- ---------------------------------------------------------------------
-- Этап 6. Негативное тестирование ограничений целостности
-- ---------------------------------------------------------------------

-- Тест 1: Попытка повторить значение первичного ключа
-- Ожидание: ошибка PRIMARY KEY / UNIQUE
-- Сообщение SQLite: UNIQUE constraint failed: books_improved.id
-- INSERT INTO books_improved (id, title, author, publisher, isbn, publication_year, price, stock) 
-- VALUES (1, 'Тест повтора PK', 'Автор', 'Издательство', '978-0-0000-0001-1', 2022, 500, 10);

-- Тест 2: Попытка повторить значение поля с UNIQUE (дублирование ISBN)
-- Ожидание: ошибка UNIQUE
-- Сообщение SQLite: UNIQUE constraint failed: books_improved.isbn
-- INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock) 
-- VALUES ('Дубликат ISBN', 'Тест', 'Эксмо', '978-5-699-12345-1', 2022, 600, 5);

-- Тест 3: Попытка оставить обязательное поле NULL
-- Ожидание: ошибка NOT NULL
-- Сообщение SQLite: NOT NULL constraint failed: books_improved.title
-- INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock) 
-- VALUES (NULL, 'Тест', 'Эксмо', '978-0-0000-0003-3', 2022, 600, 5);

-- Тест 4: Попытка записать отрицательную цену
-- Ожидание: ошибка CHECK
-- Сообщение SQLite: CHECK constraint failed: price > 0
-- INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock) 
-- VALUES ('Некорректная цена', 'Тест', 'Эксмо', '978-0-0000-0004-4', 2022, -150.00, 5);

-- Тест 5: Попытка записать отрицательный остаток
-- Ожидание: ошибка CHECK
-- Сообщение SQLite: CHECK constraint failed: stock >= 0
-- INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock) 
-- VALUES ('Некорректный остаток', 'Тест', 'Эксмо', '978-0-0000-0005-5', 2022, 350.00, -10);

-- Тест 6: Добавление записи без значения поля, имеющего DEFAULT
-- Ожидание: успешная вставка, присвоение stock = 0
-- Результат: успешно вставлено, stock по умолчанию равен 0
INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price) 
VALUES ('Книга со значением DEFAULT', 'Роберт Мартин', 'Питер', '978-0-0000-0006-6', 2023, 750.00);

-- Тест 7: Дополнительный некорректный сценарий (пустая строка в названии CHECK(length(trim(title))>0))
-- Ожидание: ошибка CHECK
-- Сообщение SQLite: CHECK constraint failed: length(trim(title)) > 0
-- INSERT INTO books_improved (title, author, publisher, isbn, publication_year, price, stock) 
-- VALUES ('   ', 'Автор', 'Издательство', '978-0-0000-0007-7', 2022, 400.00, 5);

-- ---------------------------------------------------------------------
-- Индивидуальная часть: Таблица "Товары интернет-магазина" (store_products)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS store_products;
CREATE TABLE store_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE CHECK(length(trim(sku)) >= 4),
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    category TEXT NOT NULL CHECK(length(trim(category)) > 0),
    price REAL NOT NULL CHECK(price > 0),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    warranty_months INTEGER NOT NULL DEFAULT 12 CHECK(warranty_months >= 0 AND warranty_months <= 120),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1))
);

INSERT INTO store_products (sku, name, category, price, quantity, warranty_months, is_active) VALUES
('SKU-1001', 'Игровой ноутбук ASUS ROG Strix', 'Ноутбуки', 124990.00, 8, 24, 1),
('SKU-1002', 'Смартфон Apple iPhone 15 128GB', 'Смартфоны', 84990.00, 15, 12, 1),
('SKU-1003', 'Монитор 27" LG UltraGear 144Hz', 'Мониторы', 23990.00, 12, 36, 1),
('SKU-1004', 'Механическая клавиатура Dark Project', 'Периферия', 7490.00, 25, 12, 1),
('SKU-1005', 'Беспроводная мышь Logitech G Pro X', 'Периферия', 11990.00, 18, 24, 1),
('SKU-1006', 'Внешний SSD Kingston XS2000 1TB', 'Накопители', 9890.00, 30, 60, 1),
('SKU-1007', 'Наушники с микрофоном HyperX Cloud II', 'Аудио', 8290.00, 14, 24, 1),
('SKU-1008', 'Wi-Fi роутер Keenetic Giga KN-1011', 'Сетевое оборудование', 13490.00, 9, 36, 1),
('SKU-1009', 'Планшет Samsung Galaxy Tab S9', 'Планшеты', 67990.00, 6, 12, 1),
('SKU-1010', 'Лазерный принтер Pantum P2500W', 'Оргтехника', 10490.00, 11, 12, 1);
"""

with open(os.path.join(BASE_DIR, "pz2.sql"), "w", encoding="utf-8") as f:
    f.write(pz2_sql_content.strip())
print("pz2.sql written successfully.")

# ----------------- Write pz3.sql -----------------
pz3_sql_content = """-- =====================================================================
-- ПРАКТИЧЕСКАЯ РАБОТА № 3
-- Тема: Связи между таблицами и ссылочная целостность в SQLite
-- Студент: Титов
-- Файл скрипта: pz3.sql
-- =====================================================================

-- Обязательное включение контроля внешних ключей в SQLite
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- 1. Удаление дочерних и родительских таблиц (в порядке зависимостей)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS book_genres;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS copies;
DROP TABLE IF EXISTS book_authors;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS publishers;

-- ---------------------------------------------------------------------
-- 2. Создание связанных таблиц схемы библиотеки
-- ---------------------------------------------------------------------

-- Родительская таблица: Издательства
CREATE TABLE publishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    city TEXT CHECK(city IS NULL OR length(trim(city)) > 0)
);

-- Родительская таблица: Авторы
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    birth_year INTEGER CHECK(birth_year IS NULL OR (birth_year >= 1800 AND birth_year <= 2026)),
    country TEXT CHECK(country IS NULL OR length(trim(country)) > 0)
);

-- Таблица библиографического описания: Книги
-- Связь с publishers (1:N) с правилом ON DELETE SET NULL
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
    isbn TEXT NOT NULL UNIQUE CHECK(length(trim(isbn)) >= 10),
    publisher_id INTEGER,
    publication_year INTEGER CHECK(publication_year IS NULL OR (publication_year >= 1500 AND publication_year <= 2026)),
    price REAL NOT NULL CHECK(price > 0),
    FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE SET NULL
);

-- Связующая таблица отношения M:N между books и authors
-- Составной PRIMARY KEY (book_id, author_id)
-- ON DELETE CASCADE для книги, ON DELETE RESTRICT для автора
CREATE TABLE book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE RESTRICT
);

-- Таблица физических экземпляров: copies
-- Связь с books (1:N) с правилом ON DELETE CASCADE
CREATE TABLE copies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    inventory_no TEXT NOT NULL UNIQUE CHECK(length(trim(inventory_no)) > 0),
    status TEXT NOT NULL CHECK(status IN ('доступна', 'выдана', 'в ремонте', 'списана')),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Индивидуальное усложнение: Вариант A (Жанры книг M:N)
CREATE TABLE genres (
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
);

-- ---------------------------------------------------------------------
-- 3. Наполнение данными
-- ---------------------------------------------------------------------

-- Издательства (5 записей >= 4)
INSERT INTO publishers (id, name, city) VALUES
(1, 'Питер', 'Санкт-Петербург'),
(2, 'Эксмо', 'Москва'),
(3, 'АСТ', 'Москва'),
(4, 'Вильямс', 'Москва'),
(5, 'Альпина Паблишер', 'Москва');

-- Авторы (8 записей >= 6)
INSERT INTO authors (id, name, birth_year, country) VALUES
(1, 'Лев Толстой', 1828, 'Россия'),
(2, 'Фёдор Достоевский', 1821, 'Россия'),
(3, 'Михаил Булгаков', 1891, 'СССР'),
(4, 'Роберт Мартин', 1952, 'США'),
(5, 'Эндрю Таненбаум', 1944, 'США'),
(6, 'Дональд Кнут', 1938, 'США'),
(7, 'Эрих Гамма', 1961, 'Швейцария'),
(8, 'Ричард Хелм', 1960, 'США');

-- Книги (10 записей >= 10)
INSERT INTO books (id, title, isbn, publisher_id, publication_year, price) VALUES
(1, 'Война и мир', '978-5-699-12345-1', 2, 2021, 1250.00),
(2, 'Преступление и наказание', '978-5-17-098765-2', 3, 2020, 850.50),
(3, 'Мастер и Маргарита', '978-5-389-11223-3', 2, 2022, 920.00),
(4, 'Чистый код', '978-5-4461-0987-8', 1, 2023, 1850.00),
(5, 'Идеальный программист', '978-5-4461-0555-1', 1, 2022, 1450.00),
(6, 'Современные операционные системы', '978-5-4461-1122-9', 1, 2021, 2950.00),
(7, 'Компьютерные сети', '978-5-4461-1155-7', 1, 2020, 3100.00),
(8, 'Искусство программирования. Том 1', '978-5-8459-0081-0', 4, 2020, 4500.00),
(9, 'Паттерны объектно-ориентированного проектирования', '978-5-4461-0112-2', 1, 2023, 2200.00),
(10, 'Архитектура корпоративных программных приложений', '978-5-8459-0777-2', 4, 2021, 2800.00);

-- Связи книга-автор (12 записей >= 12, у книг 9 и 10 - по 2 автора)
INSERT INTO book_authors (book_id, author_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 4),
(6, 5),
(7, 5),
(8, 6),
(9, 7),
(9, 8),
(10, 4),
(10, 7);

-- Экземпляры (16 записей >= 15, у книг 1, 2, 4, 6, 9 - более одного экземпляра)
INSERT INTO copies (id, book_id, inventory_no, status) VALUES
(1, 1, 'INV-00101', 'доступна'),
(2, 1, 'INV-00102', 'выдана'),
(3, 2, 'INV-00201', 'доступна'),
(4, 2, 'INV-00202', 'доступна'),
(5, 3, 'INV-00301', 'выдана'),
(6, 4, 'INV-00401', 'доступна'),
(7, 4, 'INV-00402', 'доступна'),
(8, 4, 'INV-00403', 'в ремонте'),
(9, 5, 'INV-00501', 'доступна'),
(10, 6, 'INV-00601', 'доступна'),
(11, 6, 'INV-00602', 'выдана'),
(12, 7, 'INV-00701', 'доступна'),
(13, 8, 'INV-00801', 'доступна'),
(14, 9, 'INV-00901', 'доступна'),
(15, 9, 'INV-00902', 'выдана'),
(16, 10, 'INV-01001', 'доступна');

-- Жанры и связи книга-жанр (Индивидуальное усложнение)
INSERT INTO genres (id, name, description) VALUES
(1, 'Классическая литература', 'Произведения признанных мировых и отечественных классиков'),
(2, 'Компьютерная литература', 'Учебники и практические руководства по программированию и ИТ'),
(3, 'Программирование и архитектура', 'Книги по чистому коду, паттернам и проектированию'),
(4, 'Системное администрирование и сети', 'Архитектура ОС, сетевые протоколы и инфраструктура');

INSERT INTO book_genres (book_id, genre_id) VALUES
(1, 1), (2, 1), (3, 1),
(4, 2), (4, 3),
(5, 2), (5, 3),
(6, 2), (6, 4),
(7, 2), (7, 4),
(8, 2), (8, 3),
(9, 2), (9, 3),
(10, 2), (10, 3);

-- ---------------------------------------------------------------------
-- 4. Негативное тестирование ссылочной целостности
-- ---------------------------------------------------------------------

-- Тест 1: Добавить книгу со ссылкой на несуществующее издательство
-- Сообщение SQLite: FOREIGN KEY constraint failed
-- INSERT INTO books (title, isbn, publisher_id, publication_year, price) 
-- VALUES ('Книга без издательства', '978-0-9999-1111-1', 999, 2023, 1000.00);

-- Тест 2: Добавить связь book_authors с несуществующим book_id или author_id
-- Сообщение SQLite: FOREIGN KEY constraint failed
-- INSERT INTO book_authors (book_id, author_id) VALUES (999, 1);

-- Тест 3: Повторно добавить уже существующую пару book_id + author_id
-- Сообщение SQLite: UNIQUE constraint failed: book_authors.book_id, book_authors.author_id
-- INSERT INTO book_authors (book_id, author_id) VALUES (1, 1);

-- Тест 4: Удалить издательство, на которое ссылаются книги (проверка ON DELETE SET NULL)
-- Издательство id=3 удаляется, у книги id=2 поле publisher_id становится NULL
-- DELETE FROM publishers WHERE id = 3;

-- Тест 5: Удалить книгу, для которой существуют строки book_authors (проверка ON DELETE CASCADE)
-- При удалении книги id=1 строки в book_authors и copies удаляются автоматически
-- DELETE FROM books WHERE id = 1;

-- Тест 6: Попытаться удалить автора, у которого существуют связанные книги (проверка ON DELETE RESTRICT)
-- Сообщение SQLite: FOREIGN KEY constraint failed
-- DELETE FROM authors WHERE id = 4;

-- Тест 7: Создать второй экземпляр с уже существующим inventory_no
-- Сообщение SQLite: UNIQUE constraint failed: copies.inventory_no
-- INSERT INTO copies (book_id, inventory_no, status) VALUES (2, 'INV-00201', 'доступна');

-- Тест 8: Общая проверка целостности внешних ключей средствами SQLite
-- Возвращает 0 строк при корректной базе данных
PRAGMA foreign_key_check;

-- Проверка списков внешних ключей для таблиц
PRAGMA foreign_key_list(books);
PRAGMA foreign_key_list(book_authors);
PRAGMA foreign_key_list(copies);
"""

with open(os.path.join(BASE_DIR, "pz3.sql"), "w", encoding="utf-8") as f:
    f.write(pz3_sql_content.strip())
print("pz3.sql written successfully.")


# ==============================================================================
# PZ 4: computer_firm.db & pz4_computer_firm.sql
# ==============================================================================
print("--- Generating computer_firm.db and pz4_computer_firm.sql ---")

db_comp_path = os.path.join(BASE_DIR, "computer_firm.db")
if os.path.exists(db_comp_path):
    os.remove(db_comp_path)

conn_comp = sqlite3.connect(db_comp_path)
conn_comp.execute("PRAGMA foreign_keys = ON;")
cur_comp = conn_comp.cursor()

cur_comp.execute("""
CREATE TABLE Product (
    maker VARCHAR(10) NOT NULL,
    model VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50) NOT NULL CHECK(type IN ('PC', 'Laptop', 'Printer'))
);
""")

cur_comp.execute("""
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
""")

cur_comp.execute("""
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
""")

cur_comp.execute("""
CREATE TABLE Printer (
    code INT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    color CHAR(1) NOT NULL CHECK(color IN ('y', 'n')),
    type VARCHAR(10) NOT NULL CHECK(type IN ('Laser', 'Jet', 'Matrix')),
    price REAL CHECK(price IS NULL OR price >= 0),
    FOREIGN KEY (model) REFERENCES Product(model) ON DELETE CASCADE
);
""")

# Parse Excel Компьютерная фирма.xlsx
with zipfile.ZipFile(r"c:\Users\mrspa\Downloads\Компьютерная фирма.xlsx") as z:
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root:
            ss.append(''.join(si.itertext()))
            
    def get_sheet_rows(sheet_name):
        res = []
        sheet = ET.fromstring(z.read(sheet_name))
        for row in sheet.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            vals = []
            for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                t = c.attrib.get('t')
                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = v.text if v is not None else ''
                if t == 's' and val:
                    val = ss[int(val)]
                vals.append(val)
            res.append(vals)
        return res

    sheet1_rows = get_sheet_rows('xl/worksheets/sheet1.xml')
    sheet2_rows = get_sheet_rows('xl/worksheets/sheet2.xml')
    sheet3_rows = get_sheet_rows('xl/worksheets/sheet3.xml')
    sheet4_rows = get_sheet_rows('xl/worksheets/sheet4.xml')

# Product rows
prod_data = []
for r in sheet1_rows[1:]:
    if len(r) >= 3 and r[0] and r[1]:
        prod_data.append((r[0], r[1], r[2]))
cur_comp.executemany("INSERT INTO Product (maker, model, type) VALUES (?, ?, ?)", prod_data)

# PC rows: code, model, speed, ram, hd, cd, price
pc_data = []
for r in sheet2_rows[1:]:
    if len(r) >= 7 and r[0]:
        pc_data.append((int(r[0]), r[1], int(r[2]), int(r[3]), float(r[4]), r[5], float(r[6])))
cur_comp.executemany("INSERT INTO PC (code, model, speed, ram, hd, cd, price) VALUES (?, ?, ?, ?, ?, ?, ?)", pc_data)

# Laptop rows: code, model, speed, ram, hd, price, screen
laptop_data = []
for r in sheet3_rows[1:]:
    if len(r) >= 7 and r[0]:
        laptop_data.append((int(r[0]), r[1], int(r[2]), int(r[3]), float(r[4]), float(r[5]), int(r[6])))
cur_comp.executemany("INSERT INTO Laptop (code, model, speed, ram, hd, price, screen) VALUES (?, ?, ?, ?, ?, ?, ?)", laptop_data)

# Printer rows: code, model, color, type, price
printer_data = []
for r in sheet4_rows[1:]:
    if len(r) >= 5 and r[0]:
        printer_data.append((int(r[0]), r[1], r[2], r[3], float(r[4])))
cur_comp.executemany("INSERT INTO Printer (code, model, color, type, price) VALUES (?, ?, ?, ?, ?)", printer_data)

conn_comp.commit()
conn_comp.close()
print("computer_firm.db created successfully.")

# Write pz4_computer_firm.sql
pz4_comp_sql = """-- =====================================================================
-- ПРАКТИЧЕСКОЕ ЗАНЯТИЕ 4. Часть 1
-- База данных: Компьютерная фирма (Computer Firm)
-- Студент: Титов
-- Файл скрипта: pz4_computer_firm.sql
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Printer;
DROP TABLE IF EXISTS Laptop;
DROP TABLE IF EXISTS PC;
DROP TABLE IF EXISTS Product;

-- 1. Таблица Product(maker, model, type)
CREATE TABLE Product (
    maker VARCHAR(10) NOT NULL,
    model VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50) NOT NULL CHECK(type IN ('PC', 'Laptop', 'Printer'))
);

-- 2. Таблица PC(code, model, speed, ram, hd, cd, price)
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

-- 3. Таблица Laptop(code, model, speed, ram, hd, price, screen)
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

-- 4. Таблица Printer(code, model, color, type, price)
CREATE TABLE Printer (
    code INT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    color CHAR(1) NOT NULL CHECK(color IN ('y', 'n')),
    type VARCHAR(10) NOT NULL CHECK(type IN ('Laser', 'Jet', 'Matrix')),
    price REAL CHECK(price IS NULL OR price >= 0),
    FOREIGN KEY (model) REFERENCES Product(model) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Наполнение таблицы Product
-- ---------------------------------------------------------------------
INSERT INTO Product (maker, model, type) VALUES
('B', '1121', 'PC'),
('A', '1232', 'PC'),
('A', '1233', 'PC'),
('E', '1260', 'PC'),
('A', '1276', 'Printer'),
('D', '1288', 'Printer'),
('A', '1298', 'Laptop'),
('C', '1321', 'Laptop'),
('A', '1401', 'Printer'),
('A', '1408', 'Printer'),
('D', '1433', 'Printer'),
('E', '1434', 'Printer'),
('B', '1750', 'Laptop'),
('A', '1752', 'Laptop'),
('E', '2111', 'PC'),
('E', '2112', 'PC');

-- ---------------------------------------------------------------------
-- Наполнение таблицы PC
-- ---------------------------------------------------------------------
INSERT INTO PC (code, model, speed, ram, hd, cd, price) VALUES
(1, '1232', 500, 64, 5.0, '12x', 600.0),
(2, '1121', 750, 128, 14.0, '40x', 850.0),
(3, '1233', 500, 64, 5.0, '12x', 600.0),
(4, '1121', 600, 128, 14.0, '40x', 850.0),
(5, '1121', 600, 128, 8.0, '40x', 850.0),
(6, '1233', 750, 128, 20.0, '50x', 950.0),
(7, '1232', 500, 32, 10.0, '12x', 400.0),
(8, '1232', 450, 64, 8.0, '24x', 350.0),
(9, '1232', 450, 32, 10.0, '24x', 350.0),
(10, '1260', 500, 32, 10.0, '12x', 350.0),
(11, '1233', 900, 128, 40.0, '40x', 980.0);

-- ---------------------------------------------------------------------
-- Наполнение таблицы Laptop
-- ---------------------------------------------------------------------
INSERT INTO Laptop (code, model, speed, ram, hd, price, screen) VALUES
(1, '1298', 350, 32, 4.0, 700.0, 11),
(2, '1321', 500, 64, 8.0, 970.0, 12),
(3, '1750', 750, 128, 12.0, 1200.0, 14),
(4, '1298', 600, 64, 10.0, 1050.0, 15),
(5, '1752', 750, 128, 10.0, 1150.0, 14),
(6, '1298', 450, 64, 10.0, 950.0, 12);

-- ---------------------------------------------------------------------
-- Наполнение таблицы Printer
-- ---------------------------------------------------------------------
INSERT INTO Printer (code, model, color, type, price) VALUES
(1, '1276', 'n', 'Laser', 400.0),
(2, '1433', 'y', 'Jet', 270.0),
(3, '1434', 'y', 'Jet', 290.0),
(4, '1401', 'n', 'Matrix', 150.0),
(5, '1408', 'n', 'Matrix', 270.0),
(6, '1288', 'n', 'Laser', 400.0);

-- ---------------------------------------------------------------------
-- Примеры аналитических запросов
-- ---------------------------------------------------------------------
-- 1. Вывести всех производителей ПК с объемом жесткого диска не менее 10 Гб
SELECT DISTINCT p.maker, pc.model, pc.speed, pc.ram, pc.hd, pc.price
FROM Product p
JOIN PC pc ON p.model = pc.model
WHERE pc.hd >= 10
ORDER BY pc.price DESC;

-- 2. Средняя цена ПК и ноутбуков по каждому производителю
SELECT p.maker, p.type, COUNT(*) AS count_models, ROUND(AVG(coalesce(pc.price, lp.price)), 2) AS avg_price
FROM Product p
LEFT JOIN PC pc ON p.model = pc.model
LEFT JOIN Laptop lp ON p.model = lp.model
WHERE p.type IN ('PC', 'Laptop')
GROUP BY p.maker, p.type;
"""

with open(os.path.join(BASE_DIR, "pz4_computer_firm.sql"), "w", encoding="utf-8") as f:
    f.write(pz4_comp_sql.strip())
print("pz4_computer_firm.sql written successfully.")


# ==============================================================================
# PZ 4: study_process.db & pz4_study_process.sql
# ==============================================================================
print("--- Generating study_process.db and pz4_study_process.sql ---")

db_study_path = os.path.join(BASE_DIR, "study_process.db")
if os.path.exists(db_study_path):
    os.remove(db_study_path)

conn_study = sqlite3.connect(db_study_path)
conn_study.execute("PRAGMA foreign_keys = ON;")
cur_study = conn_study.cursor()

# 1. study_groups
cur_study.execute("""
CREATE TABLE study_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    course INTEGER NOT NULL CHECK(course >= 1 AND course <= 6),
    faculty TEXT NOT NULL CHECK(length(trim(faculty)) > 0)
);
""")

# 2. disciplines
cur_study.execute("""
CREATE TABLE disciplines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    hours INTEGER NOT NULL CHECK(hours > 0),
    reporting_form TEXT NOT NULL CHECK(reporting_form IN ('Экзамен', 'Зачет', 'Диф. зачет'))
);
""")

# 3. teachers
cur_study.execute("""
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
    department TEXT NOT NULL CHECK(length(trim(department)) > 0),
    academic_degree TEXT
);
""")

# 4. students
cur_study.execute("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
    record_book_no TEXT NOT NULL UNIQUE CHECK(length(trim(record_book_no)) >= 5),
    status TEXT NOT NULL DEFAULT 'обучается' CHECK(status IN ('обучается', 'в академическом отпуске', 'отчислен')),
    FOREIGN KEY (group_id) REFERENCES study_groups(id) ON DELETE RESTRICT
);
""")

# 5. lessons
cur_study.execute("""
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    discipline_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    lesson_date TEXT NOT NULL CHECK(lesson_date LIKE '____-__-__'),
    lesson_topic TEXT NOT NULL CHECK(length(trim(lesson_topic)) > 0),
    lesson_type TEXT NOT NULL CHECK(lesson_type IN ('Лекция', 'Практика', 'Лабораторная работа')),
    room TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES study_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (discipline_id) REFERENCES disciplines(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT
);
""")

# 6. attendance
cur_study.execute("""
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Присутствовал', 'Отсутствовал (уважительная)', 'Отсутствовал (неуважительная)')),
    mark INTEGER CHECK(mark IS NULL OR (mark >= 2 AND mark <= 5)),
    note TEXT,
    UNIQUE (lesson_id, student_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
""")

# Populate groups
groups_info = [
    (1, "ДЭ 21-24", 2, "Информационные технологии"),
    (2, "ДЭ 22-24", 2, "Информационные технологии"),
    (3, "ДЭ 23-24", 2, "Информационные технологии"),
    (4, "ДЭ 24-24", 2, "Информационные технологии"),
    (5, "ДЭ 25-24", 2, "Информационные технологии")
]
cur_study.executemany("INSERT INTO study_groups (id, name, course, faculty) VALUES (?, ?, ?, ?)", groups_info)

# Populate disciplines
disciplines_info = [
    (1, "Базы данных и СУБД", 108, "Экзамен"),
    (2, "Операционные системы", 72, "Зачет"),
    (3, "Программирование на языках высокого уровня", 144, "Экзамен"),
    (4, "Компьютерные сети", 72, "Диф. зачет"),
    (5, "Дискретная математика", 108, "Экзамен")
]
cur_study.executemany("INSERT INTO disciplines (id, name, hours, reporting_form) VALUES (?, ?, ?, ?)", disciplines_info)

# Populate teachers
teachers_info = [
    (1, "Иванов Сергей Петрович", "Кафедра программной инженерии", "к.т.н., доцент"),
    (2, "Смирнова Елена Александровна", "Кафедра вычислительных систем", "д.т.н., профессор"),
    (3, "Кузнецов Михаил Васильевич", "Кафедра информационной безопасности", "к.ф.-м.н., доцент"),
    (4, "Попова Ольга Николаевна", "Кафедра высшей математики", "к.ф.-м.н., доцент")
]
cur_study.executemany("INSERT INTO teachers (id, full_name, department, academic_degree) VALUES (?, ?, ?, ?)", teachers_info)

# Parse students from Студенты.xlsx
group_id_map = {
    "ДЭ 21-24": 1,
    "ДЭ 22-24": 2,
    "ДЭ 23-24": 3,
    "ДЭ 24-24": 4,
    "ДЭ 25-24": 5
}

students_parsed = []
with zipfile.ZipFile(r"c:\Users\mrspa\Downloads\Студенты.xlsx") as z:
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root:
            ss.append(''.join(si.itertext()))
    sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    student_counter = 1
    for row in sheet.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        vals = []
        for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            t = c.attrib.get('t')
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = v.text if v is not None else ''
            if t == 's' and val:
                val = ss[int(val)]
            vals.append(val)
        if len(vals) >= 3 and vals[0] != '№' and vals[1] in group_id_map:
            num = vals[0]
            grp_name = vals[1]
            fio = vals[2]
            grp_id = group_id_map[grp_name]
            # Form record book: e.g. ЗБ-2101, ЗБ-2201 etc.
            grp_prefix = grp_name.split()[1].split('-')[0] # '21', '22', etc.
            record_book = f"ЗБ-{grp_prefix}{int(num):02d}"
            students_parsed.append((student_counter, grp_id, fio, record_book, "обучается"))
            student_counter += 1

cur_study.executemany("""
INSERT INTO students (id, group_id, full_name, record_book_no, status)
VALUES (?, ?, ?, ?, ?)
""", students_parsed)

# Populate lessons (e.g. 10 lessons for different groups)
lessons_info = [
    (1, 1, 1, 1, "2026-10-05", "Реляционная модель данных и нормализация", "Лекция", "Ауд. 301"),
    (2, 1, 1, 1, "2026-10-12", "Проектирование связей 1:N и M:N в SQLite", "Практика", "Лаб. 204"),
    (3, 1, 2, 2, "2026-10-07", "Процессы и потоки в ОС Linux", "Лекция", "Ауд. 305"),
    (4, 1, 3, 3, "2026-10-09", "Объектно-ориентированное программирование", "Лабораторная работа", "Лаб. 208"),
    (5, 2, 1, 1, "2026-10-06", "Ограничения целостности PRIMARY KEY и CHECK", "Практика", "Лаб. 204"),
    (6, 2, 2, 2, "2026-10-08", "Управление памятью и виртуальная память", "Лекция", "Ауд. 301"),
    (7, 3, 1, 1, "2026-10-10", "Внешние ключи и каскадное удаление данных", "Практика", "Лаб. 206"),
    (8, 3, 4, 2, "2026-10-14", "Сетевая модель OSI и стек TCP/IP", "Лекция", "Ауд. 310"),
    (9, 4, 1, 1, "2026-10-15", "Составные ключи и связь M:N", "Практика", "Лаб. 205"),
    (10, 5, 5, 4, "2026-10-16", "Теория графов и алгоритмы поиска", "Лекция", "Ауд. 402")
]
cur_study.executemany("""
INSERT INTO lessons (id, group_id, discipline_id, teacher_id, lesson_date, lesson_topic, lesson_type, room)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", lessons_info)

# Populate attendance for Lesson 2 (Group ДЭ 21-24, 26 students) and Lesson 5 (Group ДЭ 22-24, 22 students)
# Fetch students of group 1
cur_study.execute("SELECT id FROM students WHERE group_id = 1")
grp1_student_ids = [r[0] for r in cur_study.fetchall()]

attendance_records = []
att_id = 1
for idx, st_id in enumerate(grp1_student_ids):
    if idx == 3:
        status = "Отсутствовал (уважительная)"
        mark = None
        note = "Справка из поликлиники"
    elif idx == 7:
        status = "Отсутствовал (неуважительная)"
        mark = None
        note = "Без объяснения причины"
    elif idx % 4 == 0:
        status = "Присутствовал"
        mark = 5
        note = "Активная работа у доски"
    elif idx % 4 == 1:
        status = "Присутствовал"
        mark = 4
        note = "Успешно защитил задание"
    else:
        status = "Присутствовал"
        mark = None
        note = None
    attendance_records.append((att_id, 2, st_id, status, mark, note))
    att_id += 1

# Fetch students of group 2
cur_study.execute("SELECT id FROM students WHERE group_id = 2")
grp2_student_ids = [r[0] for r in cur_study.fetchall()]
for idx, st_id in enumerate(grp2_student_ids):
    if idx == 2:
        status = "Отсутствовал (уважительная)"
        mark = None
        note = "Заявление в деканат"
    elif idx == 5:
        status = "Отсутствовал (неуважительная)"
        mark = None
        note = None
    else:
        status = "Присутствовал"
        mark = 5 if idx % 3 == 0 else 4
        note = "Практическая работа выполнена"
    attendance_records.append((att_id, 5, st_id, status, mark, note))
    att_id += 1

cur_study.executemany("""
INSERT INTO attendance (id, lesson_id, student_id, status, mark, note)
VALUES (?, ?, ?, ?, ?, ?)
""", attendance_records)

conn_study.commit()
conn_study.close()
print(f"study_process.db created successfully with {len(students_parsed)} students and {len(attendance_records)} attendance records.")

# Write pz4_study_process.sql
pz4_study_sql_lines = [
"""-- =====================================================================
-- ПРАКТИЧЕСКОЕ ЗАНЯТИЕ 4. Часть 2
-- База данных: Учебный процесс (Study Process)
-- Студент: Титов
-- Файл скрипта: pz4_study_process.sql
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS disciplines;
DROP TABLE IF EXISTS study_groups;

-- 1. Таблица учебных групп
CREATE TABLE study_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    course INTEGER NOT NULL CHECK(course >= 1 AND course <= 6),
    faculty TEXT NOT NULL CHECK(length(trim(faculty)) > 0)
);

-- 2. Таблица дисциплин
CREATE TABLE disciplines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    hours INTEGER NOT NULL CHECK(hours > 0),
    reporting_form TEXT NOT NULL CHECK(reporting_form IN ('Экзамен', 'Зачет', 'Диф. зачет'))
);

-- 3. Таблица преподавателей
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
    department TEXT NOT NULL CHECK(length(trim(department)) > 0),
    academic_degree TEXT
);

-- 4. Таблица студентов (114 студентов из 5 групп)
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
    record_book_no TEXT NOT NULL UNIQUE CHECK(length(trim(record_book_no)) >= 5),
    status TEXT NOT NULL DEFAULT 'обучается' CHECK(status IN ('обучается', 'в академическом отпуске', 'отчислен')),
    FOREIGN KEY (group_id) REFERENCES study_groups(id) ON DELETE RESTRICT
);

-- 5. Таблица занятий (расписание)
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    discipline_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    lesson_date TEXT NOT NULL CHECK(lesson_date LIKE '____-__-__'),
    lesson_topic TEXT NOT NULL CHECK(length(trim(lesson_topic)) > 0),
    lesson_type TEXT NOT NULL CHECK(lesson_type IN ('Лекция', 'Практика', 'Лабораторная работа')),
    room TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES study_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (discipline_id) REFERENCES disciplines(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT
);

-- 6. Таблица журнала посещаемости
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Присутствовал', 'Отсутствовал (уважительная)', 'Отсутствовал (неуважительная)')),
    mark INTEGER CHECK(mark IS NULL OR (mark >= 2 AND mark <= 5)),
    note TEXT,
    UNIQUE (lesson_id, student_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Наполнение групп
INSERT INTO study_groups (id, name, course, faculty) VALUES
(1, 'ДЭ 21-24', 2, 'Информационные технологии'),
(2, 'ДЭ 22-24', 2, 'Информационные технологии'),
(3, 'ДЭ 23-24', 2, 'Информационные технологии'),
(4, 'ДЭ 24-24', 2, 'Информационные технологии'),
(5, 'ДЭ 25-24', 2, 'Информационные технологии');

-- Наполнение дисциплин
INSERT INTO disciplines (id, name, hours, reporting_form) VALUES
(1, 'Базы данных и СУБД', 108, 'Экзамен'),
(2, 'Операционные системы', 72, 'Зачет'),
(3, 'Программирование на языках высокого уровня', 144, 'Экзамен'),
(4, 'Компьютерные сети', 72, 'Диф. зачет'),
(5, 'Дискретная математика', 108, 'Экзамен');

-- Наполнение преподавателей
INSERT INTO teachers (id, full_name, department, academic_degree) VALUES
(1, 'Иванов Сергей Петрович', 'Кафедра программной инженерии', 'к.т.н., доцент'),
(2, 'Смирнова Елена Александровна', 'Кафедра вычислительных систем', 'д.т.н., профессор'),
(3, 'Кузнецов Михаил Васильевич', 'Кафедра информационной безопасности', 'к.ф.-м.н., доцент'),
(4, 'Попова Ольга Николаевна', 'Кафедра высшей математики', 'к.ф.-м.н., доцент');
"""
]

# Add student inserts
pz4_study_sql_lines.append("\n-- Наполнение студентов (114 студентов из Студенты.xlsx)")
pz4_study_sql_lines.append("INSERT INTO students (id, group_id, full_name, record_book_no, status) VALUES")
st_rows_sql = []
for st in students_parsed:
    st_rows_sql.append(f"({st[0]}, {st[1]}, '{st[2]}', '{st[3]}', '{st[4]}')")
pz4_study_sql_lines.append(",\n".join(st_rows_sql) + ";\n")

# Add lessons
pz4_study_sql_lines.append("""-- Наполнение занятий
INSERT INTO lessons (id, group_id, discipline_id, teacher_id, lesson_date, lesson_topic, lesson_type, room) VALUES
(1, 1, 1, 1, '2026-10-05', 'Реляционная модель данных и нормализация', 'Лекция', 'Ауд. 301'),
(2, 1, 1, 1, '2026-10-12', 'Проектирование связей 1:N и M:N в SQLite', 'Практика', 'Лаб. 204'),
(3, 1, 2, 2, '2026-10-07', 'Процессы и потоки в ОС Linux', 'Лекция', 'Ауд. 305'),
(4, 1, 3, 3, '2026-10-09', 'Объектно-ориентированное программирование', 'Лабораторная работа', 'Лаб. 208'),
(5, 2, 1, 1, '2026-10-06', 'Ограничения целостности PRIMARY KEY и CHECK', 'Практика', 'Лаб. 204'),
(6, 2, 2, 2, '2026-10-08', 'Управление памятью и виртуальная память', 'Лекция', 'Ауд. 301'),
(7, 3, 1, 1, '2026-10-10', 'Внешние ключи и каскадное удаление данных', 'Практика', 'Лаб. 206'),
(8, 3, 4, 2, '2026-10-14', 'Сетевая модель OSI и стек TCP/IP', 'Лекция', 'Ауд. 310'),
(9, 4, 1, 1, '2026-10-15', 'Составные ключи и связь M:N', 'Практика', 'Лаб. 205'),
(10, 5, 5, 4, '2026-10-16', 'Теория графов и алгоритмы поиска', 'Лекция', 'Ауд. 402');
""")

# Add attendance
pz4_study_sql_lines.append("""-- Наполнение журнала посещаемости
INSERT INTO attendance (id, lesson_id, student_id, status, mark, note) VALUES""")
att_rows_sql = []
for a in attendance_records:
    mark_val = str(a[4]) if a[4] is not None else "NULL"
    note_val = f"'{a[5]}'" if a[5] is not None else "NULL"
    att_rows_sql.append(f"({a[0]}, {a[1]}, {a[2]}, '{a[3]}', {mark_val}, {note_val})")
pz4_study_sql_lines.append(",\n".join(att_rows_sql) + ";\n")

# Queries
pz4_study_sql_lines.append("""-- ---------------------------------------------------------------------
-- Примеры практических запросов к учебной базе
-- ---------------------------------------------------------------------
-- 1. Сводный список студентов по группам с номерами зачетных книжек
SELECT g.name AS group_name, s.record_book_no, s.full_name, s.status
FROM students s
JOIN study_groups g ON s.group_id = g.id
ORDER BY g.name, s.full_name;

-- 2. Ведомость посещаемости и оценок занятия по базам данных
SELECT l.lesson_date, d.name AS discipline, l.lesson_topic, s.full_name, a.status, coalesce(a.mark, '-') AS mark, coalesce(a.note, '') AS note
FROM attendance a
JOIN lessons l ON a.lesson_id = l.id
JOIN disciplines d ON l.discipline_id = d.id
JOIN students s ON a.student_id = s.id
WHERE l.id = 2
ORDER BY s.full_name;

-- 3. Статистика посещаемости по группам
SELECT g.name AS group_name,
       COUNT(a.id) AS total_records,
       SUM(CASE WHEN a.status = 'Присутствовал' THEN 1 ELSE 0 END) AS attended,
       SUM(CASE WHEN a.status LIKE 'Отсутствовал%' THEN 1 ELSE 0 END) AS absent,
       ROUND(100.0 * SUM(CASE WHEN a.status = 'Присутствовал' THEN 1 ELSE 0 END) / COUNT(a.id), 1) AS attendance_percentage
FROM attendance a
JOIN students s ON a.student_id = s.id
JOIN study_groups g ON s.group_id = g.id
GROUP BY g.name;
""")

with open(os.path.join(BASE_DIR, "pz4_study_process.sql"), "w", encoding="utf-8") as f:
    f.write("\n".join(pz4_study_sql_lines))
print("pz4_study_process.sql written successfully.")

# Also combine into pz4.sql for user convenience
with open(os.path.join(BASE_DIR, "pz4.sql"), "w", encoding="utf-8") as f:
    f.write(pz4_comp_sql + "\n\n" + "\n".join(pz4_study_sql_lines))
print("pz4.sql (combined) written successfully.")

print("All databases and SQL scripts generated without errors!")
