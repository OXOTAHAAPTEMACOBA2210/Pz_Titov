-- =====================================================================
-- ПРАКТИЧЕСКАЯ РАБОТА № 7
-- Тема: Разработка приложения с использованием Python и sqlite3
-- Предметная область: Платная парковка на 10 машиномест
-- Студент: Титов
-- Файл скрипта: pz7_parking.sql
-- =====================================================================

DROP TABLE IF EXISTS parking_sessions;

-- Таблица сессий парковки
CREATE TABLE parking_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_model TEXT NOT NULL CHECK(length(trim(car_model)) > 0),
    license_plate TEXT NOT NULL CHECK(length(trim(license_plate)) >= 5),
    driver_name TEXT NOT NULL CHECK(length(trim(driver_name)) > 0),
    entry_time TEXT NOT NULL CHECK(entry_time LIKE '____-__-__ __:__:__'),
    exit_time TEXT CHECK(exit_time IS NULL OR exit_time LIKE '____-__-__ __:__:__'),
    cost REAL CHECK(cost IS NULL OR cost >= 0)
);

-- Частичный уникальный индекс: блокирует повторный активный заезд одной машины,
-- но разрешает повторные въезды после закрытия предыдущей сессии (когда exit_time NOT NULL)
CREATE UNIQUE INDEX idx_active_license_plate 
ON parking_sessions (license_plate) 
WHERE exit_time IS NULL;

-- ---------------------------------------------------------------------
-- Первоначальное наполнение (демонстрационные данные)
-- ---------------------------------------------------------------------
INSERT INTO parking_sessions (car_model, license_plate, driver_name, entry_time, exit_time, cost) VALUES
('Toyota Camry', 'А123ВС777', 'Иванов Иван Иванович', '2026-10-28 07:15:00', '2026-10-28 09:00:00', 200.0),
('BMW X5', 'В456ОК199', 'Петров Алексей Сергеевич', '2026-10-28 06:30:00', '2026-10-28 10:30:00', 400.0),
('Lada Vesta', 'С789МН77', 'Сидоров Михаил Николаевич', '2026-10-28 08:20:00', '2026-10-28 08:30:00', 0.0),
('Kia Rio', 'Е012КХ799', 'Смирнова Анна Павловна', '2026-10-28 05:40:00', '2026-10-28 08:40:00', 300.0),
('Hyundai Solaris', 'К345ТУ177', 'Кузнецов Дмитрий Владимирович', '2026-10-28 04:10:00', '2026-10-28 04:40:00', 100.0),
('Volkswagen Tiguan', 'М678ОР797', 'Морозов Роман Игоревич', '2026-10-28 09:10:00', '2026-10-28 10:40:00', 200.0),
('Mercedes-Benz E200', 'О999ОО77', 'Титов Артём Сергеевич', '2026-10-28 10:45:00', NULL, NULL),
('Skoda Octavia', 'Т111ТТ777', 'Васильев Олег Петрович', '2026-10-28 10:20:00', NULL, NULL),
('Audi Q7', 'У555УУ199', 'Новиков Кирилл Антонович', '2026-10-28 11:50:00', NULL, NULL),
('Toyota Camry', 'А123ВС777', 'Иванов Иван Иванович', '2026-10-28 12:05:00', NULL, NULL);

-- Проверочные запросы:
-- 1. Число занятых мест сейчас:
SELECT COUNT(*) AS occupied_spots FROM parking_sessions WHERE exit_time IS NULL;

-- 2. Список активных автомобилей:
SELECT id, car_model, license_plate, driver_name, entry_time
FROM parking_sessions
WHERE exit_time IS NULL
ORDER BY entry_time;

-- 3. Выручка по завершенным парковкам:
SELECT COUNT(*) AS completed_parkings, SUM(cost) AS total_revenue
FROM parking_sessions
WHERE exit_time IS NOT NULL;