# -*- coding: utf-8 -*-
"""
ПРАКТИЧЕСКАЯ РАБОТА № 7. Вариант 3: Выборочная загрузка и кэширование
Студент: Титов
СУБД: SQLite (parking_titov.db)

Особенности архитектуры Варианта 3:
- База данных НЕ загружается целиком при старте программы (экономия памяти при миллионах записей).
- Результат наиболее часто вызываемого запроса (список машин на парковке и число свободных мест) кэшируется в памяти.
- При повторном обращении данные возвращаются из кэша мгновенно без обращения к диску (без SELECT).
- При регистрации заезда или выезда изменения СРАЗУ записываются в SQLite (commit), а кэш инвалидируется (сбрасывается).
- Ведется строгий счетчик выполненных SQL SELECT vs попаданий в кэш (Cache Hits) для наглядной демонстрации экономии дисковых операций.
"""

import os
import math
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "parking_titov.db"
MAX_SPOTS = 10
HOURLY_RATE = 100.0
FREE_MINUTES = 15
DAILY_CAP = 1000.0


def get_con():
    """Подключение к существующей базе данных парковки."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Файл БД не найден: {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def calculate_fee(entry_time_str: str, exit_time_str: str) -> tuple:
    """Расчет стоимости стоянки."""
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


class ParkingActiveCache:
    """Кэш часто запрашиваемых активных автомобилей на парковке."""
    
    def __init__(self):
        self._cached_cars: list[dict] | None = None
        self.select_count: int = 0         # Количество выполненных физических запросов SELECT
        self.cache_hit_count: int = 0     # Количество чтений из оперативной памяти без SELECT

    @property
    def is_valid(self) -> bool:
        """Кэш валиден, если он содержит актуальные данные."""
        return self._cached_cars is not None

    def invalidate(self):
        """Сброс кэша при любой модификации данных (въезд / выезд)."""
        self._cached_cars = None

    def get_active_cars(self, con) -> tuple[list[dict], bool]:
        """
        Получение списка машин на парковке.
        Возвращает (список_машин, from_cache_flag).
        """
        if self.is_valid:
            self.cache_hit_count += 1
            return list(self._cached_cars), True
        
        # Кэш пуст (Cache Miss) -> физический SELECT к SQLite
        self.select_count += 1
        rows = con.execute(
            """
            SELECT id, car_model, license_plate, driver_name, entry_time
            FROM parking_sessions
            WHERE exit_time IS NULL
            ORDER BY entry_time
            """
        ).fetchall()
        
        self._cached_cars = [dict(r) for r in rows]
        return list(self._cached_cars), False

    def get_free_spots(self, con) -> tuple[int, bool]:
        """Получение числа свободных мест с использованием кэша."""
        cars, from_cache = self.get_active_cars(con)
        return MAX_SPOTS - len(cars), from_cache


# Инициализация глобального кэша для приложения
cache = ParkingActiveCache()


# ==============================================================================
# Функции операций парковки
# ==============================================================================

def register_car_entry(con, car_model: str, license_plate: str, driver_name: str, entry_time_str: str = None) -> int:
    """Регистрация заезда с немедленной записью в SQLite и сбросом кэша."""
    # Получаем число мест (может использовать кэш или обновить его)
    free_spots, _ = cache.get_free_spots(con)
    if free_spots <= 0:
        raise ValueError(f"Парковка переполнена! Занято {MAX_SPOTS} из {MAX_SPOTS} мест.")

    # Проверка активного заезда в БД
    existing = con.execute(
        "SELECT id FROM parking_sessions WHERE UPPER(license_plate) = UPPER(?) AND exit_time IS NULL",
        (license_plate.strip(),)
    ).fetchone()
    if existing:
        raise ValueError(f"Автомобиль '{license_plate.upper()}' уже находится на парковке (активный заезд #{existing['id']})!")

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
    
    # СБРОС КЭША: база изменилась, следующий запрос должен перечитать актуальные данные!
    cache.invalidate()
    return cur.lastrowid


def register_car_exit(con, license_plate: str, exit_time_str: str = None) -> tuple:
    """Регистрация выезда с немедленной записью в SQLite и сбросом кэша."""
    active = con.execute(
        """
        SELECT id, car_model, license_plate, driver_name, entry_time
        FROM parking_sessions
        WHERE UPPER(license_plate) = UPPER(?) AND exit_time IS NULL
        """,
        (license_plate.strip(),)
    ).fetchone()
    
    if not active:
        raise LookupError(f"Автомобиль '{license_plate.upper()}' не найден среди находящихся на парковке!")

    if not exit_time_str:
        exit_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cost, billable_hours, dur_min = calculate_fee(active["entry_time"], exit_time_str)

    con.execute(
        """
        UPDATE parking_sessions
        SET exit_time = ?, cost = ?
        WHERE id = ?
        """,
        (exit_time_str, cost, active["id"])
    )
    con.commit()

    # СБРОС КЭША: освободилось место, кэш очищен
    cache.invalidate()
    return active["id"], active["car_model"], active["entry_time"], exit_time_str, dur_min, cost


def get_car_history(con, license_plate: str) -> list:
    """История стоянок автомобиля (обычный точечный SELECT, не кэшируется)."""
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
    """Выручка по завершенным стоянкам (агрегатный SELECT к БД)."""
    row = con.execute(
        """
        SELECT COUNT(*) AS cnt, COALESCE(SUM(cost), 0.0) AS total
        FROM parking_sessions
        WHERE exit_time IS NOT NULL
        """
    ).fetchone()
    return row["cnt"], row["total"]


# ==============================================================================
# Консольный интерфейс Варианта 3
# ==============================================================================

def print_separator(char="=", length=75):
    print(char * length)


def main():
    print_separator("=")
    print("  ВАРИАНТ 3: ВЫБОРОЧНАЯ ЗАГРУЗКА И КЭШИРОВАНИЕ ДАННЫХ")
    print("  Студент: Титов | Кэширование активной парковки с подсчетом Cache Hits")
    print_separator("=")

    try:
        con = get_con()
        print(f"[OK] Подключение к БД активно: {DB_PATH.name}")
    except Exception as e:
        print(f"[!] Ошибка подключения к базе: {e}")
        return

    try:
        while True:
            cache_status_str = "ВАЛИДЕН (в памяти)" if cache.is_valid else "СБРОШЕН (требует SELECT)"
            print("\n" + "=" * 55)
            print(f"      МЕНЮ УПРАВЛЕНИЯ ПАРКОВКОЙ (ВАРИАНТ 3)")
            print(f"      Состояние кэша: [{cache_status_str}]")
            print("=" * 55)
            print(" 1. Зарегистрировать заезд автомобиля (Запись в БД + сброс кэша)")
            print(" 2. Оформить выезд автомобиля (Запись в БД + сброс кэша)")
            print(" 3. Список автомобилей на парковке (ЧТЕНИЕ ИЗ КЭША / БД)")
            print(" 4. Узнать число свободных мест (ЧТЕНИЕ ИЗ КЭША / БД)")
            print(" 5. История стоянок автомобиля по госномеру (Точечный SELECT)")
            print(" 6. Общая сумма начислений (Агрегатный SELECT)")
            print(" 7. [СТАТИСТИКА КЭША] Показать число SELECT vs Cache Hits")
            print(" 8. [ДЕМОНСТРАЦИЯ] Принудительно очистить кэш (Invalidate)")
            print(" 0. Завершить работу")
            print("-" * 55)

            choice = input("Выберите команду (0-8): ").strip()

            if choice == "1":
                print("\n--- Регистрация заезда ---")
                model = input("Марка автомобиля: ").strip()
                plate = input("Государственный номер: ").strip()
                driver = input("ФИО водителя: ").strip()
                if not model or not plate or not driver:
                    print("[!] Все поля обязательны.")
                    continue
                custom_time = input("Время въезда (Enter - текущее): ").strip()
                t_in = custom_time if custom_time else None
                
                try:
                    sid = register_car_entry(con, model, plate, driver, t_in)
                    print(f"[+] Заезд #{sid} успешно сохранен в SQLite!")
                    print(f"    [КЭШ] Кэш активных машин автоматически сброшен (Invalidated).")
                except ValueError as ve:
                    print(f"[!] Отказ: {ve}")

            elif choice == "2":
                print("\n--- Оформление выезда ---")
                plate = input("Госномер выезжающего автомобиля: ").strip()
                if not plate:
                    continue
                custom_time = input("Время выезда (Enter - текущее): ").strip()
                t_out = custom_time if custom_time else None

                try:
                    sid, model, t_in, t_out, dur_min, fee = register_car_exit(con, plate, t_out)
                    print_separator("-")
                    print(f"[+] Выезд успешно зафиксирован в SQLite для сессии #{sid}!")
                    print(f"    Автомобиль: {model} [{plate.upper()}] | Оплата: {fee:.2f} руб.")
                    print(f"    [КЭШ] Кэш освободившихся мест автоматически инвалидирован.")
                    print_separator("-")
                except (LookupError, ValueError) as err:
                    print(f"[!] Ошибка: {err}")

            elif choice == "3":
                cars, from_cache = cache.get_active_cars(con)
                source_tag = "[КЭШ - память]" if from_cache else "[БАЗА ДАННЫХ - SQL SELECT]"
                color_info = "без обращения к диску!" if from_cache else f"выполнен физический SELECT #{cache.select_count}"
                
                print(f"\n--- Список машин на парковке {source_tag} ({color_info}) ---")
                occupied = len(cars)
                print(f"Занято мест: {occupied} из {MAX_SPOTS} | Свободно: {MAX_SPOTS - occupied}")
                if not cars:
                    print("Парковка пуста.")
                else:
                    print_separator("-")
                    print(f"{'ID':<4} | {'Марка авто':<20} | {'Госномер':<12} | {'Водитель':<26} | {'Время заезда'}")
                    print_separator("-")
                    for c in cars:
                        print(f"{c['id']:<4} | {c['car_model'][:18]:<20} | {c['license_plate']:<12} | {c['driver_name'][:24]:<26} | {c['entry_time']}")
                    print_separator("-")

            elif choice == "4":
                free, from_cache = cache.get_free_spots(con)
                source_tag = "[КЭШ ПАМЯТИ]" if from_cache else "[SQL SELECT К ДИСКУ]"
                print(f"\n{source_tag} Свободных мест: {free} из {MAX_SPOTS} (Занято: {MAX_SPOTS - free})")

            elif choice == "5":
                plate = input("\nВведите госномер для выборки истории: ").strip()
                history = get_car_history(con, plate)
                print(f"[БД] Выполнен прямой точечный SELECT по номеру '{plate.upper()}'.")
                if not history:
                    print("Записей не найдено.")
                else:
                    print_separator("-")
                    print(f"История стоянок {plate.upper()} ({len(history)} записей):")
                    print_separator("-")
                    for h in history:
                        t_out = h['exit_time'] if h['exit_time'] else "НА ПАРКОВКЕ"
                        cost_str = f"{h['cost']:.2f} руб." if h['cost'] is not None else "—"
                        print(f"#{h['id']:<3} | {h['car_model'][:14]:<16} | Въезд: {h['entry_time']} | Выезд: {t_out:<19} | {cost_str}")
                    print_separator("-")

            elif choice == "6":
                cnt, total = get_total_revenue(con)
                print("\n[БД] Выполнен агрегатный SQL SELECT подсчета выручки.")
                print(f"Завершенных стоянок: {cnt} | Сумма начислений: {total:.2f} руб.")

            elif choice == "7":
                print("\n" + "=" * 60)
                print("       СТАТИСТИКА ЭФФЕКТИВНОСТИ КЭШИРОВАНИЯ")
                print("=" * 60)
                total_reads = cache.select_count + cache.cache_hit_count
                pct = (cache.cache_hit_count / total_reads * 100) if total_reads > 0 else 0.0
                print(f"• Физических запросов SELECT к диску:    {cache.select_count}")
                print(f"• Мгновенных чтений из кэша памяти:     {cache.cache_hit_count}")
                print(f"• Всего обращений к данным парковки:    {total_reads}")
                print(f"• Доля попаданий в кэш (Cache Hit Rate): {pct:.1f}%")
                print("-" * 60)
                print("В отличие от полной загрузки всех объектов (Вариант 2),")
                print("кэширование не потребляет память под миллионы старых записей,")
                print("а хранит лишь снимок наиболее горячих и частых данных.")
                print("=" * 60)

            elif choice == "8":
                cache.invalidate()
                print("\n[КЭШ] Кэш успешно принудительно очищен. Следующий просмотр парковки выполнит новый SELECT.")

            elif choice == "0":
                print("\nРабота завершена. До свидания!")
                break
            else:
                print("[!] Неверный выбор. Введите число от 0 до 8.")
    finally:
        con.close()
        print("[OK] Соединение с SQLite закрыто.")


if __name__ == "__main__":
    main()
