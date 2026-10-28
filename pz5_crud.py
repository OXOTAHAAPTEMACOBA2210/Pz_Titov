# -*- coding: utf-8 -*-
"""
ПРАКТИЧЕСКАЯ РАБОТА № 5
CRUD-приложение для базы данных учебного процесса (SQLite + Python)
Студент: Титов

Разделение на слои:
1. Слой доступа к данным (функции SQL без input(), параметризованные запросы)
2. Слой пользовательского интерфейса (консольное меню, валидация типов, обработка исключений)
"""

import os
import sqlite3
from pathlib import Path

# Путь к существующей базе данных учебного процесса
DB_PATH = Path(__file__).resolve().parent / "study_process.db"


def get_con():
    """Подключение к существующему файлу SQLite с контролем целостности."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Файл базы данных не найден по пути: {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


# 1. Функции доступа к данным

def create_student(con, full_name: str, group_id: int, record_book_no: str, status: str = "обучается") -> int:
    """
    Create: добавление нового студента в существующую группу.
    Возвращает идентификатор (id) созданной строки.
    """
    cur = con.execute(
        """
        INSERT INTO students (full_name, group_id, record_book_no, status)
        VALUES (?, ?, ?, ?)
        """,
        (full_name.strip(), group_id, record_book_no.strip(), status.strip())
    )
    con.commit()
    return cur.lastrowid


def list_students(con, limit: int = None) -> list:
    """
    Read: получение списка студентов со связанным наименованием группы.
    """
    sql = """
    SELECT s.id, s.record_book_no, s.full_name, g.name AS group_name, s.status
    FROM students s
    JOIN study_groups g ON s.group_id = g.id
    ORDER BY g.name, s.full_name
    """
    if limit is not None:
        sql += f" LIMIT {int(limit)}"
    return con.execute(sql).fetchall()


def get_student_by_id(con, student_id: int):
    """
    Read: получение подробных сведений об одном студенте по ID.
    """
    return con.execute(
        """
        SELECT s.id, s.record_book_no, s.full_name, s.group_id, g.name AS group_name, s.status
        FROM students s
        JOIN study_groups g ON s.group_id = g.id
        WHERE s.id = ?
        """,
        (student_id,)
    ).fetchone()


def search_students_by_name(con, query: str) -> list:
    """
    Read: поиск студентов по части ФИО с использованием LIKE.
    """
    return con.execute(
        """
        SELECT s.id, s.record_book_no, s.full_name, g.name AS group_name, s.status
        FROM students s
        JOIN study_groups g ON s.group_id = g.id
        WHERE s.full_name LIKE ?
        ORDER BY s.full_name
        """,
        (f"%{query.strip()}%",)
    ).fetchall()


def update_student(con, student_id: int, full_name: str, group_id: int, status: str) -> bool:
    """
    Update: изменение сведений о студенте.
    Возвращает True, если строка была найдена и обновлена, иначе False.
    """
    cur = con.execute(
        """
        UPDATE students
        SET full_name = ?, group_id = ?, status = ?
        WHERE id = ?
        """,
        (full_name.strip(), group_id, status.strip(), student_id)
    )
    con.commit()
    return cur.rowcount == 1


def delete_student(con, student_id: int) -> bool:
    """
    Delete: удаление студента по ID.
    Возвращает True, если строка была найдена и удалена, иначе False.
    """
    cur = con.execute("DELETE FROM students WHERE id = ?", (student_id,))
    con.commit()
    return cur.rowcount == 1


def list_groups(con) -> list:
    """Вспомогательный справочник групп."""
    return con.execute("SELECT id, name, course, faculty FROM study_groups ORDER BY id").fetchall()


def list_lessons(con, limit: int = 15) -> list:
    """Вспомогательный список занятий для регистрации посещаемости."""
    return con.execute(
        """
        SELECT l.id, l.lesson_date, d.name AS discipline_name, g.name AS group_name, l.lesson_topic
        FROM lessons l
        JOIN disciplines d ON l.discipline_id = d.id
        JOIN study_groups g ON l.group_id = g.id
        ORDER BY l.lesson_date DESC, l.id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()


def register_attendance(con, lesson_id: int, student_id: int, status: str, mark: int = None, note: str = None) -> int:
    """
    Операция учебного процесса: внесение отметки о посещении занятия.
    """
    cur = con.execute(
        """
        INSERT INTO attendance (lesson_id, student_id, status, mark, note)
        VALUES (?, ?, ?, ?, ?)
        """,
        (lesson_id, student_id, status.strip(), mark, note.strip() if note else None)
    )
    con.commit()
    return cur.lastrowid


def get_student_attendance(con, student_id: int) -> list:
    """
    Просмотр истории посещаемости и оценок конкретного студента.
    """
    return con.execute(
        """
        SELECT l.lesson_date, d.name AS discipline_name, l.lesson_topic, a.status, a.mark, a.note
        FROM attendance a
        JOIN lessons l ON a.lesson_id = l.id
        JOIN disciplines d ON l.discipline_id = d.id
        WHERE a.student_id = ?
        ORDER BY l.lesson_date
        """,
        (student_id,)
    ).fetchall()


# 2. Пользовательский интерфейс (консоль)

def print_separator(char="=", length=75):
    print(char * length)


def ui_list_students(con):
    print("\n--- Список студентов учебного процесса ---")
    limit_str = input("Сколько записей вывести (Enter - первые 20, 'all' - все 115): ").strip().lower()
    limit = None if limit_str == "all" else (int(limit_str) if limit_str.isdigit() else 20)
    
    rows = list_students(con, limit=limit)
    if not rows:
        print("В базе данных пока нет студентов.")
        return
    
    print_separator("-")
    print(f"{'ID':<5} | {'Зачётка':<10} | {'ФИО студента':<35} | {'Группа':<10} | {'Статус'}")
    print_separator("-")
    for r in rows:
        print(f"{r['id']:<5} | {r['record_book_no']:<10} | {r['full_name']:<35} | {r['group_name']:<10} | {r['status']}")
    print_separator("-")
    print(f"Показано записей: {len(rows)}")


def ui_get_student(con):
    print("\n--- Просмотр сведений о студенте по ID ---")
    val = input("Введите ID студента: ").strip()
    if not val.isdigit():
        print("[!] Ошибка: ID должен быть целым положительным числом.")
        return
    
    student = get_student_by_id(con, int(val))
    if student is None:
        print(f"[!] Студент с ID {val} не найден в базе данных.")
        return
    
    print_separator("-")
    print(f"ID студента:       {student['id']}")
    print(f"ФИО студента:      {student['full_name']}")
    print(f"Номер зачётки:     {student['record_book_no']}")
    print(f"Группа:            {student['group_name']} (group_id={student['group_id']})")
    print(f"Статус:            {student['status']}")
    print_separator("-")


def ui_search_students(con):
    print("\n--- Поиск студента по части ФИО ---")
    q = input("Введите часть фамилии или имени: ").strip()
    if not q:
        print("[!] Поисковый запрос не может быть пустым.")
        return
    
    results = search_students_by_name(con, q)
    if not results:
        print(f"По запросу '{q}' ничего не найдено.")
        return
    
    print_separator("-")
    print(f"Найдено записей: {len(results)}")
    print(f"{'ID':<5} | {'Зачётка':<10} | {'ФИО студента':<35} | {'Группа':<10} | {'Статус'}")
    print_separator("-")
    for r in results:
        print(f"{r['id']:<5} | {r['record_book_no']:<10} | {r['full_name']:<35} | {r['group_name']:<10} | {r['status']}")
    print_separator("-")


def ui_create_student(con):
    print("\n--- Добавление нового студента (Create) ---")
    print("Доступные учебные группы:")
    for g in list_groups(con):
        print(f"  [{g['id']}] {g['name']} ({g['course']} курс, {g['faculty']})")
    
    fio = input("Введите полное ФИО студента: ").strip()
    if not fio:
        print("[!] ФИО не может быть пустым.")
        return
    
    gid_str = input("Введите ID группы: ").strip()
    if not gid_str.isdigit():
        print("[!] Некорректный ID группы.")
        return
    
    rec_no = input("Введите номер зачетной книжки (например ЗБ-2299): ").strip()
    if not rec_no:
        print("[!] Номер зачетки обязателен.")
        return
    
    status_choice = input("Статус [1 - обучается, 2 - в академическом отпуске, 3 - отчислен] (Enter - 1): ").strip()
    status_map = {"1": "обучается", "2": "в академическом отпуске", "3": "отчислен", "": "обучается"}
    status = status_map.get(status_choice, "обучается")
    
    try:
        new_id = create_student(con, fio, int(gid_str), rec_no, status)
        print(f"[+] Студент успешно добавлен! Присвоен ID: {new_id}")
    except sqlite3.IntegrityError as exc:
        con.rollback()
        print(f"[!] Ошибка целостности SQLite (IntegrityError): {exc}")
        print("Операция отклонена базой данных (проверьте уникальность зачётки или корректность ID группы).")


def ui_update_student(con):
    print("\n--- Изменение сведений о студенте (Update) ---")
    val = input("Введите ID студента для редактирования: ").strip()
    if not val.isdigit():
        print("[!] Ошибка: ID должен быть числом.")
        return
    sid = int(val)
    st = get_student_by_id(con, sid)
    if st is None:
        print(f"[!] Студент с ID {sid} не найден (rowcount=0).")
        return
    
    print(f"Текущие данные: {st['full_name']} | Группа: {st['group_name']} (ID={st['group_id']}) | Статус: {st['status']}")
    
    new_fio = input(f"Новое ФИО (Enter, чтобы оставить '{st['full_name']}'): ").strip()
    if not new_fio:
        new_fio = st['full_name']
        
    print("Доступные группы: " + ", ".join([f"{g['id']}: {g['name']}" for g in list_groups(con)]))
    new_gid_str = input(f"Новый ID группы (Enter, чтобы оставить {st['group_id']}): ").strip()
    new_gid = int(new_gid_str) if new_gid_str.isdigit() else st['group_id']
    
    new_status = input(f"Новый статус (обучается / в академическом отпуске / отчислен) (Enter - без изм.): ").strip()
    if not new_status:
        new_status = st['status']
        
    try:
        updated = update_student(con, sid, new_fio, new_gid, new_status)
        if updated:
            print(f"[+] Данные студента с ID {sid} успешно обновлены.")
        else:
            print(f"[!] Запись с ID {sid} не была изменена.")
    except sqlite3.IntegrityError as exc:
        con.rollback()
        print(f"[!] Ошибка целостности SQLite: {exc}")


def ui_delete_student(con):
    print("\n--- Удаление студента (Delete) ---")
    val = input("Введите ID студента для удаления: ").strip()
    if not val.isdigit():
        print("[!] Некорректный ID.")
        return
    sid = int(val)
    
    st = get_student_by_id(con, sid)
    if st is None:
        print(f"[!] Студент с ID {sid} не найден (rowcount=0). Удаление невозможно.")
        return
    
    confirm = input(f"Вы действительно хотите удалить студента '{st['full_name']}' (ID={sid})? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Удаление отменено пользователем.")
        return
    
    try:
        deleted = delete_student(con, sid)
        if deleted:
            print(f"[+] Студент с ID {sid} и все связанные отметки успешно удалены.")
        else:
            print(f"[!] Не удалось удалить студента с ID {sid} (rowcount=0).")
    except sqlite3.IntegrityError as exc:
        con.rollback()
        print(f"[!] Операция отклонена СУБД (IntegrityError): {exc}")
        print("Причина: на запись студента ссылаются связанные таблицы, а ограничение RESTRICT блокирует удаление.")


def ui_attendance_operation(con):
    print("\n--- Операция с учебным процессом и посещаемостью ---")
    print("1. Посмотреть историю посещаемости и оценки студента")
    print("2. Зарегистрировать новую отметку в журнале посещаемости")
    sub_choice = input("Выберите действие: ").strip()
    
    if sub_choice == "1":
        sid_str = input("Введите ID студента: ").strip()
        if not sid_str.isdigit():
            print("[!] Некорректный ID.")
            return
        sid = int(sid_str)
        st = get_student_by_id(con, sid)
        if not st:
            print(f"[!] Студент с ID {sid} не найден.")
            return
        
        att_list = get_student_attendance(con, sid)
        print_separator("-")
        print(f"Журнал студента: {st['full_name']} (Группа: {st['group_name']})")
        print_separator("-")
        if not att_list:
            print("У данного студента пока нет записей в журнале посещаемости.")
        else:
            print(f"{'Дата':<12} | {'Дисциплина':<30} | {'Статус':<28} | {'Оц.':<4} | {'Примечание'}")
            print_separator("-")
            for a in att_list:
                mark_str = str(a['mark']) if a['mark'] is not None else "-"
                note_str = a['note'] if a['note'] else ""
                print(f"{a['lesson_date']:<12} | {a['discipline_name'][:28]:<30} | {a['status']:<28} | {mark_str:<4} | {note_str}")
        print_separator("-")
        
    elif sub_choice == "2":
        print("\nПоследние проведенные занятия:")
        lessons = list_lessons(con, limit=10)
        for l in lessons:
            print(f"  [{l['id']}] {l['lesson_date']} | {l['group_name']} | {l['discipline_name']} | {l['lesson_topic']}")
        
        lid_str = input("\nВведите ID занятия: ").strip()
        sid_str = input("Введите ID студента: ").strip()
        if not lid_str.isdigit() or not sid_str.isdigit():
            print("[!] ID занятия и студента должны быть числами.")
            return
            
        status = input("Статус [1 - Присутствовал, 2 - Отсутствовал (уважительная), 3 - Отсутствовал (неуважительная)]: ").strip()
        st_map = {
            "1": "Присутствовал",
            "2": "Отсутствовал (уважительная)",
            "3": "Отсутствовал (неуважительная)"
        }
        status_val = st_map.get(status, "Присутствовал")
        
        mark_str = input("Оценка (2-5, или Enter если без оценки): ").strip()
        mark = int(mark_str) if mark_str in ["2", "3", "4", "5"] else None
        note = input("Примечание (Enter если нет): ").strip()
        
        try:
            aid = register_attendance(con, int(lid_str), int(sid_str), status_val, mark, note)
            print(f"[+] Отметка в журнале успешно зарегистрирована! ID записи: {aid}")
        except sqlite3.IntegrityError as exc:
            con.rollback()
            print(f"[!] Ошибка целостности SQLite: {exc}")
            print("Возможные причины: студент уже отмечен на этом занятии (UNIQUE), либо указан несуществующий ID.")


def main():
    print("=" * 75)
    print("  СИСТЕМА УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ УЧЕБНОГО ПРОЦЕССА (ПЗ № 5)")
    print("  Студент: Титов | СУБД: SQLite | Доступ: Python sqlite3")
    print("=" * 75)
    
    try:
        con = get_con()
        print(f"[OK] Успешное подключение к БД: {DB_PATH.name}")
        print(f"[OK] Контроль внешних ключей активирован (PRAGMA foreign_keys = ON)")
    except Exception as exc:
        print(f"[!] Критическая ошибка при подключении к базе: {exc}")
        return

    try:
        while True:
            print("\n" + "=" * 45)
            print("                МЕНЮ ДЕЙСТВИЙ")
            print("=" * 45)
            print(" 1. Вывести список студентов (Read)")
            print(" 2. Найти студента по ID (Read)")
            print(" 3. Найти студента по части ФИО (Read / LIKE)")
            print(" 4. Добавить нового студента (Create)")
            print(" 5. Редактировать данные студента (Update)")
            print(" 6. Удалить студента (Delete)")
            print(" 7. Операции с журналом посещаемости (Attendance)")
            print(" 0. Завершить работу")
            print("-" * 45)
            
            cmd = input("Выберите команду: ").strip()
            if cmd == "1":
                ui_list_students(con)
            elif cmd == "2":
                ui_get_student(con)
            elif cmd == "3":
                ui_search_students(con)
            elif cmd == "4":
                ui_create_student(con)
            elif cmd == "5":
                ui_update_student(con)
            elif cmd == "6":
                ui_delete_student(con)
            elif cmd == "7":
                ui_attendance_operation(con)
            elif cmd == "0":
                print("\nРабота с базой данных завершена. До свидания!")
                break
            else:
                print("[!] Неизвестная команда. Введите число от 0 до 7.")
    finally:
        con.close()
        print("[OK] Соединение с базой данных безопасно закрыто.")


if __name__ == "__main__":
    main()
