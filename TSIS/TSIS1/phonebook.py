import csv
import json
import os
import sys
from datetime import date, datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from config import load_config
from connect import connect as get_connection


def _conn():
    params = load_config()
    return get_connection(params)


def _serialize(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


def _input(prompt: str) -> str:
    return input(prompt).strip()


def _print_separator(char="─", width=60):
    print(char * width)


def _print_contacts(rows):
    if not rows:
        print("  (no results)")
        return
    _print_separator()
    for r in rows:
        phones = r.get("phones") or []
        phone_str = ", ".join(
            f"{p['phone']} [{p['type']}]" for p in phones
        ) if phones else "(no phones)"
        print(f"  ID      : {r['id']}")
        print(f"  Name    : {r['name']}")
        print(f"  Email   : {r.get('email') or '—'}")
        print(f"  Birthday: {r.get('birthday') or '—'}")
        print(f"  Group   : {r.get('group_name') or '—'}")
        print(f"  Phones  : {phone_str}")
        _print_separator()


def apply_schema():
    base = os.path.dirname(os.path.abspath(__file__))
    for filename in ("schema.sql", "procedures.sql"):
        path = os.path.join(base, filename)
        if not os.path.exists(path):
            print(f"[WARN] {filename} not found — skipping.")
            continue
        with open(path, "r", encoding="utf-8") as fh:
            sql = fh.read()
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        print(f"[OK] Applied {filename}")


def _fetch_phones(cur, contact_id: int) -> list:
    cur.execute(
        "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
        (contact_id,),
    )
    
    return [{"phone": r["phone"], "type": r["type"]} for r in cur.fetchall()]


def _enrich(rows, cur) -> list:
    result = []
    for r in rows:
        
        r["phones"] = _fetch_phones(cur, r["id"])
        result.append(r)
    return result


def _get_group_id(cur, group_name: str):
    cur.execute(
        "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,),
    )
    cur.execute("SELECT id FROM groups WHERE LOWER(name) = LOWER(%s)", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None


def add_contact_full():
    print("\n── Add Contact ──")
    name = _input("Name: ")
    if not name:
        print("[ERROR] Name is required.")
        return

    email = _input("Email (optional): ") or None
    birthday = _input("Birthday YYYY-MM-DD (optional): ") or None
    if birthday:
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            print("[ERROR] Invalid date format.")
            return

    list_groups()
    group_name = _input("Group (Family/Work/Friend/Other or new name): ") or None

    with _conn() as conn:
        with conn.cursor() as cur:
            group_id = _get_group_id(cur, group_name) if group_name else None
            cur.execute(
                """
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (name, email, birthday, group_id),
            )
            contact_id = cur.fetchone()[0]

            while True:
                phone = _input("Add phone (leave blank to stop): ")
                if not phone:
                    break
                ptype = _input("Type (home/work/mobile): ").lower()
                if ptype not in ("home", "work", "mobile"):
                    print("[WARN] Invalid type, defaulting to 'mobile'.")
                    ptype = "mobile"
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (contact_id, phone, ptype),
                )
        conn.commit()
    print(f"[OK] Contact '{name}' added (id={contact_id}).")


def list_groups() -> list:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name")
            rows = cur.fetchall()
    groups = [{"id": r[0], "name": r[1]} for r in rows]
    print("\nAvailable groups:", ", ".join(g["name"] for g in groups))
    return groups


SORT_COLUMNS = {
    "1": ("c.name", "Name"),
    "2": ("c.birthday", "Birthday"),
    "3": ("c.created_at", "Date Added"),
}


def _choose_sort() -> str:
    print("\nSort by:")
    for k, (_, label) in SORT_COLUMNS.items():
        print(f"  {k}. {label}")
    choice = _input("Choice [1]: ") or "1"
    return SORT_COLUMNS.get(choice, ("c.name", "Name"))[0]


def filter_by_group():
    list_groups()
    group_name = _input("Enter group name: ")
    order_col = _choose_sort()

    query = f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name AS group_name, c.created_at
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        WHERE  LOWER(g.name) = LOWER(%s)
        ORDER  BY {order_col}
    """
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (group_name,))
            rows = _enrich(cur.fetchall(), cur)
    print(f"\n── Contacts in group '{group_name}' ──")
    _print_contacts(rows)


def search_by_email():
    term = _input("Email search term: ")
    order_col = _choose_sort()

    query = f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name AS group_name, c.created_at
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        WHERE  LOWER(c.email) LIKE LOWER(%s)
        ORDER  BY {order_col}
    """
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (f"%{term}%",))
            rows = _enrich(cur.fetchall(), cur)
    print(f"\n── Email search: '{term}' ──")
    _print_contacts(rows)


def full_search():
    term = _input("Search (name / email / phone): ")
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (term,))
            rows = cur.fetchall()

    if not rows:
        print("  (no results)")
        return

    contacts: dict = {}
    for r in rows:
        cid = r["contact_id"]
        if cid not in contacts:
            contacts[cid] = {
                "id": cid,
                "name": r["name"],
                "email": r["email"],
                "birthday": r["birthday"],
                "group_name": r["group_name"],
                "phones": [],
            }
        if r["phone"]:
            contacts[cid]["phones"].append({"phone": r["phone"], "type": r["phone_type"]})

    print(f"\n── Search results for '{term}' ──")
    _print_contacts(list(contacts.values()))


def paginated_browse():
    PAGE_SIZE = 5
    offset = 0
    order_col = _choose_sort()

    while True:
        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = f"""
                    SELECT c.id, c.name, c.email, c.birthday,
                           g.name AS group_name, c.created_at
                    FROM   contacts c
                    LEFT   JOIN groups g ON g.id = c.group_id
                    ORDER  BY {order_col}
                    LIMIT  %s OFFSET %s
                """
                cur.execute(query, (PAGE_SIZE, offset))
                rows = _enrich(cur.fetchall(), cur)

                cur.execute("SELECT COUNT(*) FROM contacts")
                total = cur.fetchone()["count"]

        page_num = offset // PAGE_SIZE + 1
        total_pages = max(1, -(-total // PAGE_SIZE))
        print(f"\n── Page {page_num} / {total_pages}  (total contacts: {total}) ──")
        _print_contacts(rows)

        print("  [n]ext  [p]rev  [q]uit")
        cmd = _input(">> ").lower()
        if cmd in ("n", "next"):
            if offset + PAGE_SIZE < total:
                offset += PAGE_SIZE
            else:
                print("  Already on the last page.")
        elif cmd in ("p", "prev"):
            if offset > 0:
                offset = max(0, offset - PAGE_SIZE)
            else:
                print("  Already on the first page.")
        elif cmd in ("q", "quit"):
            break


def export_json():
    path = _input("Output JSON file path [contacts_export.json]: ") or "contacts_export.json"

    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT c.id, c.name, c.email, c.birthday,
                       g.name AS group_name, c.created_at
                FROM   contacts c
                LEFT   JOIN groups g ON g.id = c.group_id
                ORDER  BY c.id
                """
            )
            rows = _enrich(cur.fetchall(), cur)

    data = [dict(r) for r in rows]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, default=_serialize)

    print(f"[OK] Exported {len(data)} contacts → {path}")


def import_json():
    path = _input("JSON file path [contacts_export.json]: ") or "contacts_export.json"
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as fh:
        records = json.load(fh)

    inserted = skipped = overwritten = 0
    with _conn() as conn:
        with conn.cursor() as cur:
            for rec in records:
                name = rec.get("name", "").strip()
                if not name:
                    continue

                cur.execute(
                    "SELECT id FROM contacts WHERE LOWER(name) = LOWER(%s) LIMIT 1",
                    (name,),
                )
                existing = cur.fetchone()

                if existing:
                    print(f"\n  Duplicate found: '{name}'")
                    choice = _input("  [s]kip / [o]verwrite? ").lower()
                    if choice != "o":
                        skipped += 1
                        continue
                    cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
                    overwritten += 1

                group_id = _get_group_id(cur, rec["group_name"]) if rec.get("group_name") else None
                cur.execute(
                    """
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (name, rec.get("email"), rec.get("birthday"), group_id),
                )
                contact_id = cur.fetchone()[0]

                for ph in rec.get("phones", []):
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, ph.get("phone"), ph.get("type")),
                    )
                inserted += 1
        conn.commit()
    print(f"\n[OK] JSON import complete — inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}")


def import_csv():
    path = _input("CSV file path [contacts.csv]: ") or "contacts.csv"
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return

    contacts: dict = {}
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                continue
            if name not in contacts:
                contacts[name] = {
                    "email": (row.get("email") or "").strip() or None,
                    "birthday": (row.get("birthday") or "").strip() or None,
                    "group": (row.get("group") or "").strip() or None,
                    "phones": [],
                }
            phone = (row.get("phone") or "").strip()
            if phone:
                ptype = (row.get("phone_type") or "mobile").strip().lower()
                if ptype not in ("home", "work", "mobile"):
                    ptype = "mobile"
                contacts[name]["phones"].append((phone, ptype))

    inserted = updated = 0
    with _conn() as conn:
        with conn.cursor() as cur:
            for name, data in contacts.items():
                group_id = _get_group_id(cur, data["group"]) if data["group"] else None
                cur.execute(
                    """
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                    """,
                    (name, data["email"], data["birthday"], group_id),
                )
                row = cur.fetchone()
                if row:
                    contact_id = row[0]
                    inserted += 1
                else:
                    cur.execute(
                        """
                        UPDATE contacts
                        SET    email    = COALESCE(%s, email),
                               birthday = COALESCE(%s, birthday),
                               group_id = COALESCE(%s, group_id)
                        WHERE  LOWER(name) = LOWER(%s)
                        RETURNING id
                        """,
                        (data["email"], data["birthday"], group_id, name),
                    )
                    row = cur.fetchone()
                    contact_id = row[0]
                    updated += 1

                for phone, ptype in data["phones"]:
                    cur.execute(
                        """
                        INSERT INTO phones (contact_id, phone, type)
                        SELECT %s, %s, %s
                        WHERE  NOT EXISTS (
                            SELECT 1 FROM phones
                            WHERE contact_id = %s AND phone = %s
                        )
                        """,
                        (contact_id, phone, ptype, contact_id, phone),
                    )
        conn.commit()
    print(f"[OK] CSV import complete — inserted: {inserted}, updated: {updated}")


def call_add_phone():
    contact_name = _input("Contact name: ")
    phone = _input("Phone number: ")
    ptype = _input("Type (home/work/mobile): ").lower()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, ptype))
        conn.commit()
    print("[OK] add_phone executed.")


def call_move_to_group():
    contact_name = _input("Contact name: ")
    group_name = _input("Group name: ")
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
        conn.commit()
    print("[OK] move_to_group executed.")


MENU = """
╔══════════════════════════════════════════╗
║         PhoneBook  —  TSIS 1             ║
╠══════════════════════════════════════════╣
║  1.  Add contact (full)                  ║
║  2.  Search (name / email / phone)       ║
║  3.  Filter by group                     ║
║  4.  Search by email                     ║
║  5.  Browse contacts (paged)             ║
║──────────────────────────────────────────║
║  6.  Add phone to contact                ║
║  7.  Move contact to group               ║
║──────────────────────────────────────────║
║  8.  Import from CSV                     ║
║  9.  Export to JSON                      ║
║  10. Import from JSON                    ║
║──────────────────────────────────────────║
║  0.  Apply schema & procedures           ║
║  q.  Quit                                ║
╚══════════════════════════════════════════╝
"""

ACTIONS = {
    "1": add_contact_full,
    "2": full_search,
    "3": filter_by_group,
    "4": search_by_email,
    "5": paginated_browse,
    "6": call_add_phone,
    "7": call_move_to_group,
    "8": import_csv,
    "9": export_json,
    "10": import_json,
    "0": apply_schema,
}


def main():
    while True:
        print(MENU)
        choice = _input("Select option: ").lower()
        if choice in ("q", "quit", "exit"):
            print("Goodbye!")
            sys.exit(0)
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except psycopg2.Error as exc:
                print(f"[DB ERROR] {exc}")
            except KeyboardInterrupt:
                print("\n  Interrupted.")
        else:
            print("  Invalid option — try again.")


if __name__ == "__main__":
    main()