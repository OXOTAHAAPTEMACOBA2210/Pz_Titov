-- =====================================================================
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