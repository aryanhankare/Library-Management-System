from datetime import date, timedelta
from database import create_tables, get_connection


def seed():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()

    members = [
        ("STU001", "Aaryan Hankare", "aryanhankare@gmail.com", "7720078525"),
        ("STU002", "Sanmeet Jeswani", "sanmeetjeswani2505@gmail.com", "8767678010"),
        ("STU003", "Aniket Dhamange", "aniketdhamange2007@gmail.com", "9075695355"),
        ("STU004", "Balu Motar", "balumore@gmail.com", "----------"),
        ("STU005", "Pranit Shetty", "pranitshetty@gmail.com", "----------"),
    ]

    for mid, name, email, phone in members:
        cursor.execute("""
            INSERT IGNORE INTO member (member_id, member_name, member_email,
            member_phone, gender, expire_date, input_date)
            VALUES (%s, %s, %s, %s, 1, %s, %s)
        """, (mid, name, email, phone, today + timedelta(days=365), today))

    books = [
        (1, "Introduction to Python Programming", "978-0134444321"),
        (2, "Data Structures and Algorithms", "978-0262033848"),
        (3, "Database Management Systems", "978-0073523323"),
        (4, "Computer Networks", "978-0132126953"),
        (5, "Operating System Concepts", "978-1118063330"),
    ]

    for bid, title, isbn in books:
        cursor.execute("""
            INSERT IGNORE INTO biblio (biblio_id, title, isbn_issn, input_date)
            VALUES (%s, %s, %s, NOW())
        """, (bid, title, isbn))

    items = [
        (1, 1, "BK001"), (2, 2, "BK002"), (3, 3, "BK003"),
        (4, 4, "BK004"), (5, 5, "BK005"), (6, 1, "BK006"),
        (7, 2, "BK007"), (8, 3, "BK008"),
    ]

    for iid, bid, code in items:
        cursor.execute("""
            INSERT IGNORE INTO item (item_id, biblio_id, item_code, input_date)
            VALUES (%s, %s, %s, NOW())
        """, (iid, bid, code))

    loans = [
        (1, "BK001", "STU001", today - timedelta(days=12), today + timedelta(days=1), 0),
        (2, "BK002", "STU001", today - timedelta(days=10), today + timedelta(days=2), 0),
        (3, "BK003", "STU002", today - timedelta(days=14), today + timedelta(days=1), 0),
        (4, "BK004", "STU003", today - timedelta(days=7), today + timedelta(days=5), 0),
        (5, "BK005", "STU004", today - timedelta(days=15), today - timedelta(days=1), 0),
        (6, "BK006", "STU005", today - timedelta(days=13), today + timedelta(days=2), 0),
        (7, "BK007", "STU002", today - timedelta(days=5), today + timedelta(days=7), 0),
        (8, "BK008", "STU003", today - timedelta(days=10), today + timedelta(days=1), 0),
    ]

    for lid, item, member, loan_dt, due_dt, is_ret in loans:
        cursor.execute("""
            INSERT IGNORE INTO loan (loan_id, item_code, member_id, loan_date,
            due_date, is_lent, is_return)
            VALUES (%s, %s, %s, %s, %s, 1, %s)
        """, (lid, item, member, loan_dt, due_dt, is_ret))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Seeded: {len(members)} members, {len(books)} books, {len(loans)} loans.")
    print(f"Loans due tomorrow: STU001 (BK001), STU002 (BK003), STU003 (BK008)")
    print(f"Loans due in 2 days: STU001 (BK002), STU005 (BK006)")


if __name__ == "__main__":
    seed()