-- =====================================================================
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