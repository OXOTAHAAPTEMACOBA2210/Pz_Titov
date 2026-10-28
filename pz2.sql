-- =====================================================================
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