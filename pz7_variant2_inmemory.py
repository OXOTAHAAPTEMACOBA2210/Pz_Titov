# -*- coding: utf-8 -*-
"""
ПРАКТИЧЕСКАЯ РАБОТА № 7. Вариант 2: Полная загрузка данных в объекты Python (@dataclass)
Студент: Титов
СУБД: SQLite (parking_titov.db)

Особенности архитектуры Варианта 2:
- При запуске все существующие записи загружаются один раз из SQLite и трансформируются в объекты @dataclass.
- Все операции поиска, проверки лимита мест, въезда и выезда производятся НАД ОБЪЕКТАМИ В ОПЕРАТИВНОЙ ПАМЯТИ.
- В процессе работы приложения НИКАКИХ новых запросов SELECT к базе данных не выполняется.
- Имеется специальная команда «Сохранить изменения в БД».
- Реализована функция сравнения состояния оперативной памяти и файла базы данных, демонстрирующая расхождение до коммита.
- При выходе пользователю предлагается сохранить несохраненные данные.
"""

import os
import math
import sqlite3
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "parking_titov.db"
MAX_SPOTS = 10
HOURLY_RATE = 100.0
FREE_MINUTES = 15
DAILY_CAP = 1000.0


@dataclass
class ParkingSession:
    id: int | None
    car_model: str
    license_plate: str
    driver_name: str
    entry_time: str
    exit_time: str | None = None
    cost: float | None = None
    is_new: bool = False        # Новая сессия, которой еще нет в файле SQLite
    is_dirty: bool = False      # Завершенная сессия, требующая обновления UPDATE в SQLite

    @property
    def is_active(self) -> bool:
        """Автомобиль находится на парковке, если время выезда не заполнено."""
        return self.exit_time is None


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


class InMemoryParkingManager:
    """Менеджер парковки, работающий исключительно с объектами в памяти Python."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.sessions: list[ParkingSession] = []
        self._load_all_from_db()

    def _load_all_from_db(self):
        """Единоразовая полная загрузка всех записей из SQLite при старте приложения."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Файл БД не найден: {self.db_path}")
        
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        cur = con.execute("SELECT id, car_model, license_plate, driver_name, entry_time, exit_time, cost FROM parking_sessions")
        rows = cur.fetchall()
        con.close()

        self.sessions = [
            ParkingSession(
                id=r["id"],
                car_model=r["car_model"],
                license_plate=r["license_plate"],
                driver_name=r["driver_name"],
                entry_time=r["entry_time"],
                exit_time=r["exit_time"],
                cost=r["cost"],
                is_new=False,
                is_dirty=False
            )
            for r in rows
        ]
        print(f"[ПАМЯТЬ] Успешно загружено {len(self.sessions)} сессий парковки в объекты Python.")

    def count_active_cars(self) -> int:
        """Подсчет машин на парковке (фильтрация списка объектов в памяти)."""
        return sum(1 for s in self.sessions if s.is_active)

    def count_free_spots(self) -> int:
        """Число свободных мест."""
        return MAX_SPOTS - self.count_active_cars()

    def find_active_by_plate(self, plate: str) -> ParkingSession | None:
        """Поиск активного автомобиля в памяти по номеру."""
        p_clean = plate.strip().upper()
        for s in self.sessions:
            if s.is_active and s.license_plate.upper() == p_clean:
                return s
        return None

    def register_entry(self, car_model: str, license_plate: str, driver_name: str, entry_time_str: str = None) -> ParkingSession:
        """Регистрация въезда в оперативной памяти."""
        if self.count_active_cars() >= MAX_SPOTS:
            raise ValueError(f"Парковка переполнена! Занято {MAX_SPOTS} из {MAX_SPOTS} мест.")

        existing = self.find_active_by_plate(license_plate)
        if existing:
            raise ValueError(f"Автомобиль '{license_plate.upper()}' уже на парковке (сессия ID {existing.id or 'новая'})!")

        if not entry_time_str:
            entry_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        session = ParkingSession(
            id=None, # Присвоится базой при сохранении
            car_model=car_model.strip(),
            license_plate=license_plate.strip().upper(),
            driver_name=driver_name.strip(),
            entry_time=entry_time_str,
            exit_time=None,
            cost=None,
            is_new=True,
            is_dirty=False
        )
        self.sessions.append(session)
        return session

    def register_exit(self, license_plate: str, exit_time_str: str = None) -> tuple:
        """Оформление выезда автомобиля в оперативной памяти."""
        session = self.find_active_by_plate(license_plate)
        if not session:
            raise LookupError(f"Автомобиль с номером '{license_plate.upper()}' не найден среди находящихся на парковке!")

        if not exit_time_str:
            exit_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cost, hours, duration_min = calculate_fee(session.entry_time, exit_time_str)
        session.exit_time = exit_time_str
        session.cost = cost
        session.is_dirty = True
        return session, duration_min, cost

    def get_active_cars_list(self) -> list[ParkingSession]:
        """Список объектов автомобилей, находящихся на парковке."""
        return [s for s in self.sessions if s.is_active]

    def get_car_history(self, license_plate: str) -> list[ParkingSession]:
        """История стоянок автомобиля из памяти."""
        p_clean = license_plate.strip().upper()
        return [s for s in self.sessions if s.license_plate.upper() == p_clean]

    def get_total_revenue(self) -> tuple[int, float]:
        """Агрегация выручки в памяти Python."""
        completed = [s for s in self.sessions if not s.is_active and s.cost is not None]
        return len(completed), sum(s.cost for s in completed)

    def has_unsaved_changes(self) -> bool:
        """Проверка наличия несохраненных изменений."""
        return any(s.is_new or s.is_dirty for s in self.sessions)

    def count_unsaved(self) -> tuple[int, int]:
        """Число новых и измененных объектов."""
        new_cnt = sum(1 for s in self.sessions if s.is_new)
        dirty_cnt = sum(1 for s in self.sessions if s.is_dirty and not s.is_new)
        return new_cnt, dirty_cnt

    def save_changes(self) -> tuple[int, int]:
        """
        Сохранение несохраненных объектов в файл SQLite:
        - Новые объекты вставляются (INSERT) и получают сгенерированный id;
        - Измененные объекты обновляются (UPDATE).
        """
        if not self.has_unsaved_changes():
            return 0, 0

        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA foreign_keys = ON;")
        cur = con.cursor()
        
        inserted_count = 0
        updated_count = 0

        try:
            for s in self.sessions:
                if s.is_new:
                    # Вставка новой записи
                    cur.execute(
                        """
                        INSERT INTO parking_sessions (car_model, license_plate, driver_name, entry_time, exit_time, cost)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (s.car_model, s.license_plate, s.driver_name, s.entry_time, s.exit_time, s.cost)
                    )
                    s.id = cur.lastrowid
                    s.is_new = False
                    s.is_dirty = False
                    inserted_count += 1
                elif s.is_dirty:
                    # Обновление завершенной стоянки
                    cur.execute(
                        """
                        UPDATE parking_sessions
                        SET exit_time = ?, cost = ?
                        WHERE id = ?
                        """,
                        (s.exit_time, s.cost, s.id)
                    )
                    s.is_dirty = False
                    updated_count += 1
            
            con.commit()
        finally:
            con.close()

        return inserted_count, updated_count

    def compare_memory_and_db(self) -> dict:
        """
        Демонстрация расхождения между оперативной памятью Python и файлом SQLite.
        Сравнивает текущие данные объектов и фактические строки в таблице.
        """
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        cur = con.execute("SELECT id, license_plate, exit_time FROM parking_sessions")
        db_rows = cur.fetchall()
        con.close()

        db_active_plates = set(r["license_plate"] for r in db_rows if r["exit_time"] is None)
        mem_active_plates = set(s.license_plate for s in self.sessions if s.is_active)
        
        return {
            "db_total_rows": len(db_rows),
            "mem_total_objects": len(self.sessions),
            "db_active_count": len(db_active_plates),
            "mem_active_count": len(mem_active_plates),
            "db_active_plates": sorted(list(db_active_plates)),
            "mem_active_plates": sorted(list(mem_active_plates)),
            "unsaved_new": [s.license_plate for s in self.sessions if s.is_new],
            "unsaved_exited": [s.license_plate for s in self.sessions if s.is_dirty and not s.is_new]
        }


# ==============================================================================
# Консольное меню Варианта 2
# ==============================================================================

def print_separator(char="=", length=75):
    print(char * length)


def main():
    print_separator("=")
    print("  ВАРИАНТ 2: ПОЛНАЯ ЗАГРУЗКА ДАННЫХ В ОБЪЕКТЫ PYTHON (@dataclass)")
    print("  Студент: Титов | Работа с памятью без повторных SELECT к БД")
    print_separator("=")
    
    try:
        mgr = InMemoryParkingManager(DB_PATH)
    except Exception as e:
        print(f"[!] Ошибка запуска менеджера памяти: {e}")
        return

    while True:
        new_cnt, dirty_cnt = mgr.count_unsaved()
        unsaved_label = f" [Есть несохраненные: +{new_cnt} новых, ~{dirty_cnt} выездов]" if (new_cnt + dirty_cnt > 0) else " [БД синхронизирована]"

        print("\n" + "=" * 55)
        print(f"      МЕНЮ УПРАВЛЕНИЯ ПАРКОВКОЙ (ВАРИАНТ 2){unsaved_label}")
        print("=" * 55)
        print(" 1. Зарегистрировать заезд автомобиля (в память)")
        print(" 2. Оформить выезд автомобиля (в память)")
        print(" 3. Список автомобилей на парковке (из памяти)")
        print(" 4. Число свободных мест (из памяти)")
        print(" 5. История стоянок автомобиля по госномеру (из памяти)")
        print(" 6. Общая сумма начислений (расчет в памяти)")
        print(" 7. [ДЕМОНСТРАЦИЯ] Сравнить состояние памяти и базы SQLite")
        print(" 8. [СОХРАНЕНИЕ] Записать накопленные изменения в БД")
        print(" 0. Завершить работу")
        print("-" * 55)

        choice = input("Выберите команду (0-8): ").strip()

        if choice == "1":
            print("\n--- Регистрация заезда в память ---")
            model = input("Марка автомобиля: ").strip()
            plate = input("Государственный номер: ").strip()
            driver = input("ФИО водителя: ").strip()
            if not model or not plate or not driver:
                print("[!] Все поля обязательны.")
                continue
            
            custom_time = input("Время въезда (Enter - текущее): ").strip()
            t_in = custom_time if custom_time else None
            
            try:
                s = mgr.register_entry(model, plate, driver, t_in)
                print(f"[+] Автомобиль {s.car_model} [{s.license_plate}] добавлен в объекты памяти!")
                print(f"    (Запись пока НЕ сохранена в SQLite. Нажмите 8 для фиксации в файле)")
            except ValueError as ve:
                print(f"[!] Отказ: {ve}")

        elif choice == "2":
            print("\n--- Оформление выезда в памяти ---")
            plate = input("Введите госномер автомобиля: ").strip()
            if not plate:
                continue
            custom_time = input("Время выезда (Enter - текущее): ").strip()
            t_out = custom_time if custom_time else None
            
            try:
                s, dur_min, fee = mgr.register_exit(plate, t_out)
                print_separator("-")
                print(f"[+] Выезд оформлен в памяти для {s.car_model} [{s.license_plate}]!")
                print(f"    Длительность: {dur_min} мин | К оплате: {fee:.2f} руб.")
                print(f"    (Статус выезда в файле SQLite обновится только после сохранения команды 8)")
                print_separator("-")
            except (LookupError, ValueError) as err:
                print(f"[!] Ошибка: {err}")

        elif choice == "3":
            print("\n--- Автомобили на парковке (фильтрация объектов @dataclass) ---")
            active = mgr.get_active_cars_list()
            print(f"Занято: {len(active)} из {MAX_SPOTS} мест (Свободно: {MAX_SPOTS - len(active)})")
            if not active:
                print("На парковке нет автомобилей.")
            else:
                print_separator("-")
                print(f"{'ID':<6} | {'Марка':<18} | {'Госномер':<12} | {'Водитель':<24} | {'Въезд':<19} | {'Статус'}")
                print_separator("-")
                for s in active:
                    sid_str = str(s.id) if s.id is not None else "[NEW]"
                    status_str = "Новый (не сохранен)" if s.is_new else "Сохранен в БД"
                    print(f"{sid_str:<6} | {s.car_model[:16]:<18} | {s.license_plate:<12} | {s.driver_name[:22]:<24} | {s.entry_time} | {status_str}")
                print_separator("-")

        elif choice == "4":
            free = mgr.count_free_spots()
            print(f"\n[ПАМЯТЬ] Свободно мест: {free} из {MAX_SPOTS} (Занято: {MAX_SPOTS - free})")

        elif choice == "5":
            plate = input("\nВведите госномер для просмотра истории: ").strip()
            hist = mgr.get_car_history(plate)
            if not hist:
                print(f"В памяти нет сессий для номера '{plate.upper()}'.")
            else:
                print_separator("-")
                print(f"История стоянок для {plate.upper()} (найдено {len(hist)} сессий):")
                print_separator("-")
                for s in hist:
                    t_out = s.exit_time if s.exit_time else "НА ПАРКОВКЕ"
                    cost_str = f"{s.cost:.2f} руб." if s.cost is not None else "—"
                    new_tag = " (НОВАЯ)" if s.is_new else (" (ИЗМЕНЕНА)" if s.is_dirty else "")
                    print(f"ID={s.id or '[NEW]'}: {s.car_model} | Въезд: {s.entry_time} | Выезд: {t_out:<19} | {cost_str}{new_tag}")
                print_separator("-")

        elif choice == "6":
            cnt, total = mgr.get_total_revenue()
            print_separator("-")
            print(f"Завершенных стоянок в памяти: {cnt}")
            print(f"Сумма начислений:             {total:.2f} руб.")
            print_separator("-")

        elif choice == "7":
            print("\n" + "=" * 65)
            print("  ДЕМОНСТРАЦИЯ РАСХОЖДЕНИЯ МЕЖДУ ПАМЯТЬЮ И БАЗОЙ SQLITE")
            print("=" * 65)
            comp = mgr.compare_memory_and_db()
            print(f"В файле SQLite: всего строк: {comp['db_total_rows']} | на парковке: {comp['db_active_count']}")
            print(f"В памяти Python: всего объектов: {comp['mem_total_objects']} | на парковке: {comp['mem_active_count']}")
            print(f"\nНовые автомобили, которых ЕЩЕ НЕТ в SQLite:  {comp['unsaved_new'] or 'нет'}")
            print(f"Автомобили, выехавшие в памяти, но в БД числящиеся активными: {comp['unsaved_exited'] or 'нет'}")
            print("-" * 65)
            print("Вывод: данные в памяти уже актуальны для пользователя,")
            print("но дисковый файл SQLite пока сохраняет прежнее неизменное состояние.")
            print("=" * 65)

        elif choice == "8":
            print("\n--- Фиксация изменений в файле SQLite (COMMIT) ---")
            ins, upd = mgr.save_changes()
            if ins == 0 and upd == 0:
                print("[ИНФО] Несохраненных изменений нет. База данных уже актуальна.")
            else:
                print(f"[+] Изменения успешно сохранены в SQLite!")
                print(f"    • Добавлено новых записей (INSERT): {ins}")
                print(f"    • Обновлено завершенных сессий (UPDATE): {upd}")

        elif choice == "0":
            if mgr.has_unsaved_changes():
                n_new, n_dirty = mgr.count_unsaved()
                print(f"\n[ВНИМАНИЕ] Имеются несохраненные данные: {n_new} новых заездов и {n_dirty} завершенных выездов!")
                save_ans = input("Сохранить изменения перед выходом? (y/n): ").strip().lower()
                if save_ans == 'y':
                    ins, upd = mgr.save_changes()
                    print(f"[+] Успешно сохранено: {ins} новых, {upd} обновленных записей.")
                else:
                    print("Изменения сброшены (не сохранены в файл БД).")
            print("\nРабота завершена. До свидания!")
            break
        else:
            print("[!] Неверная команда. Введите число от 0 до 8.")


if __name__ == "__main__":
    main()
