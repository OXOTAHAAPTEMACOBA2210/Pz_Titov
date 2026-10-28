# -*- coding: utf-8 -*-
"""
ПРАКТИЧЕСКАЯ РАБОТА № 7. Вариант 1: Прямое обращение к базе данных
Студент: Титов
СУБД: SQLite (parking_titov.db)

Особенности архитектуры Варианта 1:
- База данных SQLite выступает единственным и постоянным источником актуальных данных.
- Каждое действие пользователя выполняет соответствующий SQL-запрос (SELECT / INSERT / UPDATE).
- Подсчет свободных мест, поиск активных сессий и агрегация выручки производятся СУБД.
- В память приложения данные загружаются точечно под конкретную операцию (без полного журнала).
- Изменения фиксируются в БД немедленно (commit).
"""

import os
import math
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "parking_titov.db"
MAX_SPOTS = 10
HOURLY_RATE = 100.0   # 100 руб/час
FREE_MINUTES = 15     # первые 15 минут бесплатно
DAILY_CAP = 1000.0    # максимум 1000 руб/сутки


def get_con():
    """Подключение к существующей базе данных парковки."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Файл БД не найден: {DB_PATH}. Сначала инициализируйте базу.")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def calculate_fee(entry_time_str: str, exit_time_str: str) -> tuple:
    """
    Расчет стоимости стоянки по тарифу:
    - Первые 15 минут: бесплатно (0 руб.);
    - Далее: 100 руб. за каждый полный или неполный час;
    - Суточный максимум: 1000 руб./24 часа.
    Возвращает (сумма, часы, минуты).
    """
    t_in = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
    t_out = datetime.strptime(exit_time_str, "%Y-%m-%d %H:%M:%S")
    duration = t_out - t_in
    total_minutes = max(0, int(duration.total_seconds() // 60))
    
    if total_minutes <= FREE_MINUTES:
        return 0.0, 0, total_minutes
    
    billable_hours = math.ceil(total_minutes / 60)
    days = billable_hours // 24
    rem_hours = billable_hours % 24
    
    fee = days * DAILY_CAP + min(rem_hours * HOURLY_RATE, DAILY_CAP)
    return round(fee, 2), billable_hours, total_minutes


# ==============================================================================
# Функции доступа к данным (Direct SQL Queries)
# ==============================================================================

def get_occupied_spots_count(con) -> int:
    """SQL-подсчет количества занятых мест."""
    cur = con.execute("SELECT COUNT(*) AS cnt FROM parking_sessions WHERE exit_time IS NULL")
    return cur.fetchone()["cnt"]


def find_active_car(con, license_plate: str):
    """SQL-поиск активного заезда по государственному номеру."""
    return con.execute(
        """
        SELECT id, car_model, license_plate, driver_name, entry_time
        FROM parking_sessions
        WHERE UPPER(license_plate) = UPPER(?) AND exit_time IS NULL
        """,
        (license_plate.strip(),)
    ).fetchone()


def register_car_entry(con, car_model: str, license_plate: str, driver_name: str, entry_time_str: str = None) -> int:
    """
    Регистрация въезда автомобиля в БД.
    Проверяет лимит вместимости и отсутствие повторного активного заезда.
    """
    # 1. Проверка лимита 10 мест через SQL
    occupied = get_occupied_spots_count(con)
    if occupied >= MAX_SPOTS:
        raise ValueError(f"Парковка переполнена! Занято {occupied} из {MAX_SPOTS} мест.")
    
    # 2. Проверка активного заезда
    existing = find_active_car(con, license_plate)
    if existing:
        raise ValueError(f"Автомобиль с номером '{license_plate.upper()}' уже находится на парковке (заезд #{existing['id']} от {existing['entry_time']})!")

    if not entry_time_str:
        entry_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur = con.execute(
        """
        INSERT INTO parking_sessions (car_model, license_plate, driver_name, entry_time)
        VALUES (?, ?, ?, ?)
        """,
        (car_model.strip(), license_plate.strip().upper(), driver_name.strip(), entry_time_str)
    )
    con.commit()
    return cur.lastrowid


def register_car_exit(con, license_plate: str, exit_time_str: str = None) -> tuple:
    """
    Регистрация выезда автомобиля из БД.
    Возвращает (session_id, car_model, entry_time, exit_time, duration_min, cost).
    """
    active = find_active_car(con, license_plate)
    if not active:
        raise LookupError(f"Автомобиль с номером '{license_plate.upper()}' не найден среди припаркованных!")
    
    if not exit_time_str:
        exit_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cost, billable_hours, duration_min = calculate_fee(active["entry_time"], exit_time_str)
    
    con.execute(
        """
        UPDATE parking_sessions
        SET exit_time = ?, cost = ?
        WHERE id = ?
        """,
        (exit_time_str, cost, active["id"])
    )
    con.commit()
    
    return active["id"], active["car_model"], active["entry_time"], exit_time_str, duration_min, cost


def list_active_cars(con) -> list:
    """SQL-выборка всех автомобилей, находящихся сейчас на парковке."""
    return con.execute(
        """
        SELECT id, car_model, license_plate, driver_name, entry_time
        FROM parking_sessions
        WHERE exit_time IS NULL
        ORDER BY entry_time
        """
    ).fetchall()


def get_car_history(con, license_plate: str) -> list:
    """SQL-выборка истории стоянок выбранного автомобиля."""
    return con.execute(
        """
        SELECT id, car_model, license_plate, driver_name, entry_time, exit_time, cost
        FROM parking_sessions
        WHERE UPPER(license_plate) = UPPER(?)
        ORDER BY entry_time DESC
        """,
        (license_plate.strip(),)
    ).fetchall()


def get_total_revenue(con) -> tuple:
    """SQL-агрегация общей суммы начислений по завершенным стоянкам."""
    row = con.execute(
        """
        SELECT COUNT(*) AS total_count, COALESCE(SUM(cost), 0.0) AS total_sum
        FROM parking_sessions
        WHERE exit_time IS NOT NULL
        """
    ).fetchone()
    return row["total_count"], row["total_sum"]


# ==============================================================================
# Пользовательский интерфейс (Консольное меню)
# ==============================================================================

def print_separator(char="=", length=75):
    print(char * length)


def main():
    print_separator("=")
    print("  ВАРИАНТ 1: ПРЯМОЕ ОБРАЩЕНИЕ К БАЗЕ ДАННЫХ SQLITE (ПЗ № 7)")
    print("  Студент: Титов | Парковка: 10 мест | Тариф: 100 руб/час (15 мин бесплатно)")
    print_separator("=")
    
    try:
        con = get_con()
        print(f"[OK] Подключение к БД активно: {DB_PATH.name}")
    except Exception as e:
        print(f"[!] Ошибка подключения: {e}")
        return

    try:
        while True:
            print("\n" + "=" * 50)
            print("         МЕНЮ УПРАВЛЕНИЯ ПАРКОВКОЙ (ВАРИАНТ 1)")
            print("=" * 50)
            print(" 1. Зарегистрировать заезд автомобиля (Въезд)")
            print(" 2. Оформить выезд автомобиля (Выезд и оплата)")
            print(" 3. Список автомобилей на парковке")
            print(" 4. Узнать число свободных мест")
            print(" 5. История стоянок автомобиля по госномеру")
            print(" 6. Общая сумма начислений (Выручка)")
            print(" 0. Завершить работу")
            print("-" * 50)

            choice = input("Выберите команду (0-6): ").strip()
            
            if choice == "1":
                print("\n--- Регистрация заезда (Въезд) ---")
                model = input("Марка автомобиля (например, Toyota Camry): ").strip()
                plate = input("Государственный номер (например, А123ВС777): ").strip()
                driver = input("ФИО водителя: ").strip()
                
                if not model or not plate or not driver:
                    print("[!] Все поля обязательны для заполнения.")
                    continue
                
                custom_time = input("Время въезда (Enter - текущее системное время): ").strip()
                entry_time = custom_time if custom_time else None
                
                try:
                    new_id = register_car_entry(con, model, plate, driver, entry_time)
                    occupied = get_occupied_spots_count(con)
                    print(f"[+] Заезд #{new_id} успешно зарегистрирован!")
                    print(f"    Автомобиль: {model} [{plate.upper()}], Водитель: {driver}")
                    print(f"    Занято мест: {occupied} из {MAX_SPOTS} (Свободно: {MAX_SPOTS - occupied})")
                except ValueError as ve:
                    print(f"[!] Отказ в регистрации: {ve}")
                except sqlite3.IntegrityError as ie:
                    con.rollback()
                    print(f"[!] Ошибка ограничения БД: {ie}")
                    
            elif choice == "2":
                print("\n--- Оформление выезда автомобиля ---")
                plate = input("Введите государственный номер автомобиля: ").strip()
                if not plate:
                    print("[!] Номер автомобиля обязателен.")
                    continue
                
                custom_time = input("Время выезда (Enter - текущее системное время): ").strip()
                exit_time = custom_time if custom_time else None
                
                try:
                    sid, model, t_in, t_out, dur_min, fee = register_car_exit(con, plate, exit_time)
                    print_separator("-")
                    print(f"[+] Выезд оформлен успешно для заезда #{sid}!")
                    print(f"    Автомобиль:        {model} [{plate.upper()}]")
                    print(f"    Время въезда:      {t_in}")
                    print(f"    Время выезда:      {t_out}")
                    print(f"    Длительность:      {dur_min} мин ({math.ceil(dur_min/60)} ч тарифицируемых)")
                    print(f"    ИТОГО К ОПЛАТЕ:    {fee:.2f} руб.")
                    print_separator("-")
                except (LookupError, ValueError) as err:
                    print(f"[!] Ошибка выезда: {err}")
                    
            elif choice == "3":
                print("\n--- Автомобили на парковке (SQL SELECT) ---")
                cars = list_active_cars(con)
                occupied = len(cars)
                print(f"Занято мест: {occupied} из {MAX_SPOTS} | Свободно: {MAX_SPOTS - occupied}")
                if not cars:
                    print("Парковка абсолютно пуста.")
                else:
                    print_separator("-")
                    print(f"{'ID':<4} | {'Марка авто':<20} | {'Госномер':<12} | {'Водитель':<26} | {'Время заезда'}")
                    print_separator("-")
                    for c in cars:
                        print(f"{c['id']:<4} | {c['car_model'][:18]:<20} | {c['license_plate']:<12} | {c['driver_name'][:24]:<26} | {c['entry_time']}")
                    print_separator("-")
                    
            elif choice == "4":
                occupied = get_occupied_spots_count(con)
                free = MAX_SPOTS - occupied
                print(f"\n[ИНФО] Свободных мест: {free} из {MAX_SPOTS} (Занято: {occupied})")
                
            elif choice == "5":
                print("\n--- История стоянок автомобиля ---")
                plate = input("Введите госномер автомобиля: ").strip()
                if not plate:
                    continue
                history = get_car_history(con, plate)
                if not history:
                    print(f"В истории парковки записей для номера '{plate.upper()}' не найдено.")
                else:
                    print_separator("-")
                    print(f"История заездов для {plate.upper()} (всего {len(history)}):")
                    print_separator("-")
                    print(f"{'ID':<4} | {'Марка':<16} | {'Въезд':<19} | {'Выезд':<19} | {'Оплата'}")
                    print_separator("-")
                    for h in history:
                        t_out = h['exit_time'] if h['exit_time'] else "НА ПАРКОВКЕ"
                        cost_str = f"{h['cost']:.2f} руб." if h['cost'] is not None else "—"
                        print(f"{h['id']:<4} | {h['car_model'][:14]:<16} | {h['entry_time']} | {t_out:<19} | {cost_str}")
                    print_separator("-")
                    
            elif choice == "6":
                print("\n--- Финансовый отчет по завершенным стоянкам ---")
                cnt, total = get_total_revenue(con)
                print_separator("-")
                print(f"Всего завершенных стоянок: {cnt}")
                print(f"Общая сумма начислений:    {total:.2f} руб.")
                if cnt > 0:
                    print(f"Средний чек стоянки:       {(total/cnt):.2f} руб.")
                print_separator("-")
                
            elif choice == "0":
                print("\nРабота завершена. До свидания!")
                break
            else:
                print("[!] Неверный выбор. Введите число от 0 до 6.")
    finally:
        con.close()
        print("[OK] Соединение с SQLite закрыто.")


if __name__ == "__main__":
    main()
