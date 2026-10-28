# -*- coding: utf-8 -*-
"""
ПРАКТИЧЕСКАЯ РАБОТА № 6
Наполнение базы учебного процесса и справочно-статистический интерфейс на Python
Студент: Титов

Программа предоставляет удобный доступ к справочной информации и аналитической
статистике успеваемости и посещаемости занятий (включая дисциплину ТХиУД).
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "study_process.db"


def get_con():
    """Подключение к существующей базе данных учебного процесса."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Файл базы данных не найден: {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


# 1. Функции доступа к данным

def get_groups_summary(con) -> list:
    """
    Команда 1: Вывод всех учебных групп с количеством зачисленных студентов.
    """
    sql = """
    SELECT g.id, g.name AS group_name, g.course, g.faculty,
           COUNT(s.id) AS student_count
    FROM study_groups g
    LEFT JOIN students s ON g.id = s.group_id
    GROUP BY g.id, g.name, g.course, g.faculty
    ORDER BY g.name
    """
    return con.execute(sql).fetchall()


def get_students_by_group(con, group_id: int) -> list:
    """
    Команда 2: Список студентов выбранной группы.
    """
    sql = """
    SELECT s.id, s.record_book_no, s.full_name, s.status, g.name AS group_name
    FROM students s
    JOIN study_groups g ON s.group_id = g.id
    WHERE s.group_id = ?
    ORDER BY s.full_name
    """
    return con.execute(sql, (group_id,)).fetchall()


def find_students(con, query: str) -> list:
    """
    Команда 3: Поиск студентов по фрагменту ФИО.
    """
    sql = """
    SELECT s.id, s.record_book_no, s.full_name, g.name AS group_name, s.status
    FROM students s
    JOIN study_groups g ON s.group_id = g.id
    WHERE s.full_name LIKE ?
    ORDER BY g.name, s.full_name
    """
    return con.execute(sql, (f"%{query.strip()}%",)).fetchall()


def get_student_attendance_stats(con, student_id: int):
    """
    Команда 4: Детальная посещаемость и статистика пропусков конкретного студента.
    Возвращает кортеж: (student_info, attendance_records, summary_dict)
    """
    # 1. Инфо о студенте
    student = con.execute(
        """
        SELECT s.id, s.record_book_no, s.full_name, g.name AS group_name, s.status
        FROM students s
        JOIN study_groups g ON s.group_id = g.id
        WHERE s.id = ?
        """,
        (student_id,)
    ).fetchone()
    
    if not student:
        return None, [], {}

    # 2. Список посещений
    sql_records = """
    SELECT l.lesson_date, d.name AS discipline_name, l.lesson_topic,
           a.status, a.mark, a.note
    FROM attendance a
    JOIN lessons l ON a.lesson_id = l.id
    JOIN disciplines d ON l.discipline_id = d.id
    WHERE a.student_id = ?
    ORDER BY l.lesson_date
    """
    records = con.execute(sql_records, (student_id,)).fetchall()

    # 3. Агрегированная статистика
    total_lessons = len(records)
    attended = sum(1 for r in records if r["status"] == "Присутствовал")
    absent_excused = sum(1 for r in records if "уважительная" in r["status"])
    absent_unexcused = sum(1 for r in records if "неуважительная" in r["status"])
    pct = round((attended / total_lessons * 100), 1) if total_lessons > 0 else 0.0

    summary = {
        "total": total_lessons,
        "attended": attended,
        "excused": absent_excused,
        "unexcused": absent_unexcused,
        "percentage": pct
    }

    return student, records, summary


def get_group_attendance_analytics(con) -> list:
    """
    Команда 5: Сводная аналитика посещаемости по учебным группам (включая дисциплину ТХиУД).
    """
    sql = """
    SELECT g.name AS group_name,
           COUNT(a.id) AS total_records,
           SUM(CASE WHEN a.status = 'Присутствовал' THEN 1 ELSE 0 END) AS attended_count,
           SUM(CASE WHEN a.status LIKE 'Отсутствовал%' THEN 1 ELSE 0 END) AS absent_count,
           ROUND(100.0 * SUM(CASE WHEN a.status = 'Присутствовал' THEN 1 ELSE 0 END) / COUNT(a.id), 1) AS attendance_pct,
           ROUND(AVG(a.mark), 2) AS avg_mark
    FROM attendance a
    JOIN students s ON a.student_id = s.id
    JOIN study_groups g ON s.group_id = g.id
    GROUP BY g.id, g.name
    ORDER BY g.name
    """
    return con.execute(sql).fetchall()


def get_absentee_list(con, limit: int = 25) -> list:
    """
    Команда 6: Список студентов, имеющих зафиксированные пропуски занятий.
    """
    sql = """
    SELECT s.record_book_no, s.full_name, g.name AS group_name,
           l.lesson_date, d.name AS discipline_name, a.status, a.note
    FROM attendance a
    JOIN students s ON a.student_id = s.id
    JOIN study_groups g ON s.group_id = g.id
    JOIN lessons l ON a.lesson_id = l.id
    JOIN disciplines d ON l.discipline_id = d.id
    WHERE a.status LIKE 'Отсутствовал%'
    ORDER BY l.lesson_date DESC, g.name, s.full_name
    LIMIT ?
    """
    return con.execute(sql, (limit,)).fetchall()


# 2. Пользовательский консольный интерфейс

def print_line(char="=", length=80):
    print(char * length)


def ui_groups_summary(con):
    print("\n--- Сводка по учебным группам ---")
    rows = get_groups_summary(con)
    print_line("-")
    print(f"{'ID':<4} | {'Группа':<12} | {'Курс':<6} | {'Факультет':<32} | {'Студентов'}")
    print_line("-")
    total_st = 0
    for r in rows:
        print(f"{r['id']:<4} | {r['group_name']:<12} | {r['course']:<6} | {r['faculty'][:30]:<32} | {r['student_count']}")
        total_st += r['student_count']
    print_line("-")
    print(f"Всего групп: {len(rows)}, всего студентов в базе: {total_st}")


def ui_students_by_group(con):
    print("\n--- Список студентов выбранной группы ---")
    groups = get_groups_summary(con)
    print("Доступные группы:")
    for g in groups:
        print(f"  [{g['id']}] {g['group_name']} ({g['student_count']} чел.)")
    
    val = input("\nВведите ID группы: ").strip()
    if not val.isdigit():
        print("[!] Ошибка: ID группы должен быть целым числом.")
        return
    gid = int(val)
    
    students = get_students_by_group(con, gid)
    if not students:
        print(f"В группе с ID {gid} студентов не обнаружено.")
        return
    
    grp_name = students[0]['group_name']
    print_line("-")
    print(f"Студенты группы {grp_name} (всего {len(students)} чел.):")
    print_line("-")
    print(f"{'№':<4} | {'Зачётка':<10} | {'ФИО студента':<38} | {'Статус'}")
    print_line("-")
    for idx, s in enumerate(students, start=1):
        print(f"{idx:<4} | {s['record_book_no']:<10} | {s['full_name']:<38} | {s['status']}")
    print_line("-")


def ui_search_students(con):
    print("\n--- Поиск студента по части ФИО ---")
    q = input("Введите часть ФИО для поиска: ").strip()
    if not q:
        print("[!] Поисковый запрос не может быть пустым.")
        return
    
    res = find_students(con, q)
    if not res:
        print(f"Студентов с подстрокой '{q}' не найдено.")
        return
    
    print_line("-")
    print(f"Результаты поиска (найдено {len(res)}):")
    print_line("-")
    print(f"{'ID':<5} | {'Зачётка':<10} | {'ФИО студента':<36} | {'Группа':<10} | {'Статус'}")
    print_line("-")
    for r in res:
        print(f"{r['id']:<5} | {r['record_book_no']:<10} | {r['full_name']:<36} | {r['group_name']:<10} | {r['status']}")
    print_line("-")


def ui_student_attendance(con):
    print("\n--- Просмотр посещаемости и пропусков студента ---")
    val = input("Введите ID студента (или нажмите Enter для поиска по ФИО): ").strip()
    
    if not val:
        q = input("Введите фамилию студента: ").strip()
        res = find_students(con, q)
        if not res:
            print("Студент не найден.")
            return
        if len(res) == 1:
            sid = res[0]['id']
        else:
            print("Найдено несколько студентов:")
            for r in res:
                print(f"  [{r['id']}] {r['full_name']} ({r['group_name']})")
            val2 = input("Уточните ID студента: ").strip()
            if not val2.isdigit():
                return
            sid = int(val2)
    else:
        if not val.isdigit():
            print("[!] ID должен быть числом.")
            return
        sid = int(val)
    
    st, records, summary = get_student_attendance_stats(con, sid)
    if not st:
        print(f"[!] Студент с ID {sid} не найден.")
        return
    
    print_line("=")
    print(f"ЛИЧНАЯ КАРТОЧКА ПОСЕЩАЕМОСТИ: {st['full_name']}")
    print(f"Группа: {st['group_name']} | Зачётка: {st['record_book_no']} | Статус: {st['status']}")
    print_line("=")
    
    if not records:
        print("Отметок в журнале посещаемости для данного студента пока нет.")
        return
    
    print(f"{'Дата':<12} | {'Дисциплина':<32} | {'Статус':<28} | {'Оценка'} | {'Примечание'}")
    print_line("-")
    for r in records:
        m_str = str(r['mark']) if r['mark'] is not None else "-"
        note_str = r['note'] if r['note'] else ""
        print(f"{r['lesson_date']:<12} | {r['discipline_name'][:30]:<32} | {r['status']:<28} | {m_str:^6} | {note_str}")
    print_line("-")
    print("ИТОГОВАЯ СТАТИСТИКА ПОСЕЩАЕМОСТИ:")
    print(f"  - Всего занятий в журнале:        {summary['total']}")
    print(f"  - Посещено занятий:               {summary['attended']}")
    print(f"  - Пропущено по уважительной:      {summary['excused']}")
    print(f"  - Пропущено по неуважительной:    {summary['unexcused']}")
    print(f"  - Процент посещаемости студента:  {summary['percentage']}%")
    print_line("=")


def ui_group_attendance_analytics(con):
    print("\n--- Сводная аналитика посещаемости по учебным группам ---")
    rows = get_group_attendance_analytics(con)
    print_line("-")
    print(f"{'Группа':<12} | {'Всего отметок':<14} | {'Присутствий':<12} | {'Пропусков':<10} | {'Посещаемость %':<15} | {'Ср. балл'}")
    print_line("-")
    for r in rows:
        avg_m = f"{r['avg_mark']:.2f}" if r['avg_mark'] else "-"
        print(f"{r['group_name']:<12} | {r['total_records']:<14} | {r['attended_count']:<12} | {r['absent_count']:<10} | {r['attendance_pct']:>6.1f} %        | {avg_m}")
    print_line("-")


def ui_absentee_report(con):
    print("\n--- Сводный реестр зафиксированных пропусков занятий ---")
    limit_str = input("Сколько последних пропусков вывести (Enter - 15): ").strip()
    limit = int(limit_str) if limit_str.isdigit() else 15
    rows = get_absentee_list(con, limit=limit)
    if not rows:
        print("Пропусков занятий не обнаружено.")
        return
    
    print_line("-")
    print(f"{'Дата':<11} | {'Группа':<10} | {'ФИО студента':<30} | {'Статус':<28} | {'Примечание'}")
    print_line("-")
    for r in rows:
        note_str = r['note'] if r['note'] else "-"
        print(f"{r['lesson_date']:<11} | {r['group_name']:<10} | {r['full_name'][:28]:<30} | {r['status']:<28} | {note_str}")
    print_line("-")
    print(f"Показано записей о пропусках: {len(rows)}")


def main():
    print("=" * 80)
    print("  ИНФОРМАЦИОННО-АНАЛИТИЧЕСКАЯ СИСТЕМА УЧЕБНОГО ПРОЦЕССА (ПЗ № 6)")
    print("  Студент: Титов | Дисциплина: ТХиУД | База: study_process.db")
    print("=" * 80)
    
    try:
        con = get_con()
        print(f"[OK] Подключение к базе данных выполнено: {DB_PATH.name}")
    except Exception as exc:
        print(f"[!] Ошибка подключения: {exc}")
        return

    try:
        while True:
            print("\n" + "=" * 55)
            print("                 ГЛАВНОЕ МЕНЮ СТАТИСТИКИ")
            print("=" * 55)
            print(" 1. Сводка по учебным группам и численности студентов")
            print(" 2. Список студентов выбранной группы")
            print(" 3. Поиск студента по части ФИО")
            print(" 4. Посещаемость студента (детально + статистика %)")
            print(" 5. Аналитика посещаемости по учебным группам (%)")
            print(" 6. Реестр зафиксированных пропусков занятий")
            print(" 0. Завершить работу")
            print("-" * 55)
            
            cmd = input("Выберите команду (0-6): ").strip()
            if cmd == "1":
                ui_groups_summary(con)
            elif cmd == "2":
                ui_students_by_group(con)
            elif cmd == "3":
                ui_search_students(con)
            elif cmd == "4":
                ui_student_attendance(con)
            elif cmd == "5":
                ui_group_attendance_analytics(con)
            elif cmd == "6":
                ui_absentee_report(con)
            elif cmd == "0":
                print("\nРабота завершена. До свидания!")
                break
            else:
                print("[!] Неверная команда. Введите номер от 0 до 6.")
    finally:
        con.close()
        print("[OK] Соединение с базой данных закрыто.")


if __name__ == "__main__":
    main()
