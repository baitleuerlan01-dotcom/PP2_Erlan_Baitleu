import csv
import json
import os
import sys
from datetime import date, datetime

from connect import get_connection, get_cursor

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress Enter to continue...")

def print_contact_row(row):
    """Pretty-print one contact dict/row."""
    print(f"  ID       : {row['contact_id']}")
    print(f"  Username : {row['username']}")
    print(f"  Name     : {row.get('first_name', '')} {row.get('last_name', '')}")
    print(f"  Email    : {row.get('email') or '—'}")
    print(f"  Birthday : {row.get('birthday') or '—'}")
    print(f"  Group    : {row.get('group_name') or '—'}")
    print(f"  Phones   : {row.get('phones_list') or '—'}")
    print(f"  Added    : {row.get('created_at', '')}")
    print()

def get_group_id(cur, group_name):
    """Return group id; create group if absent."""
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


def add_contact(username, first_name="", last_name="",
                email="", birthday=None, group_name="",
                phones=None):
    """
    Insert a new contact with optional phones list.
    phones = [{"phone": "...", "type": "mobile"}, ...]
    """
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            group_id = get_group_id(cur, group_name)
            cur.execute(
                """INSERT INTO contacts (username, first_name, last_name,
                                         email, birthday, group_id)
                   VALUES (%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (username) DO NOTHING
                   RETURNING id""",
                (username, first_name, last_name, email or None,
                 birthday or None, group_id)
            )
            row = cur.fetchone()
            if row is None:
                print(f"  Contact '{username}' already exists — skipped.")
                return None
            contact_id = row[0]
            if phones:
                for p in phones:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                        (contact_id, p["phone"], p.get("type", "mobile"))
                    )
        conn.commit()
    print(f"  Contact '{username}' added (id={contact_id}).")
    return contact_id


def update_contact(username, **fields):
    """
    Update any combination of: first_name, last_name, email, birthday, group_name.
    """
    if not fields:
        return
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            if "group_name" in fields:
                fields["group_id"] = get_group_id(cur, fields.pop("group_name"))
            set_clause = ", ".join(f"{k} = %s" for k in fields)
            values = list(fields.values()) + [username]
            cur.execute(
                f"UPDATE contacts SET {set_clause} WHERE username = %s",
                values
            )
        conn.commit()
    print(f"  Contact '{username}' updated.")


def search_all(query):
    """Use the DB function search_contacts() — searches name, email, phones."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            return cur.fetchall()


def filter_by_group(group_name):
    """Return contacts belonging to a specific group."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """SELECT c.id AS contact_id, c.username, c.first_name, c.last_name,
                          c.email, c.birthday, g.name AS group_name,
                          STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones_list,
                          c.created_at
                   FROM contacts c
                   LEFT JOIN groups g ON g.id = c.group_id
                   LEFT JOIN phones p ON p.contact_id = c.id
                   WHERE g.name ILIKE %s
                   GROUP BY c.id, g.name
                   ORDER BY c.username""",
                (group_name,)
            )
            return cur.fetchall()


def search_by_email(partial_email):
    """Partial email match (e.g. 'gmail' matches all Gmail contacts)."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """SELECT c.id AS contact_id, c.username, c.first_name, c.last_name,
                          c.email, c.birthday, g.name AS group_name,
                          STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones_list,
                          c.created_at
                   FROM contacts c
                   LEFT JOIN groups g ON g.id = c.group_id
                   LEFT JOIN phones p ON p.contact_id = c.id
                   WHERE c.email ILIKE %s
                   GROUP BY c.id, g.name
                   ORDER BY c.username""",
                (f"%{partial_email}%",)
            )
            return cur.fetchall()


def paginated_browse(page_size=5, group_filter=None, sort_by="username"):
    """Console loop: next / prev / quit with DB-side pagination."""
    offset = 0
    while True:
        clear()
        with get_connection() as conn:
            with get_cursor(conn) as cur:
                cur.execute(
                    "SELECT * FROM get_contacts_page(%s, %s, %s, %s)",
                    (page_size, offset, group_filter, sort_by)
                )
                rows = cur.fetchall()

        if not rows and offset == 0:
            print("  No contacts found.")
            pause()
            return

        page_num = offset // page_size + 1
        print(f"=== Contacts (page {page_num}, sorted by {sort_by}) ===\n")
        for row in rows:
            print_contact_row(row)

        nav = []
        if offset > 0:
            nav.append("[p] Previous")
        if len(rows) == page_size:
            nav.append("[n] Next")
        nav.append("[q] Quit")
        print("  ".join(nav))
        choice = input("> ").strip().lower()

        if choice == "n" and len(rows) == page_size:
            offset += page_size
        elif choice == "p" and offset > 0:
            offset -= page_size
        elif choice == "q":
            return


def export_to_json(filepath="contacts_export.json"):
    """Export all contacts (with phones and group) to a JSON file."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """SELECT c.id, c.username, c.first_name, c.last_name,
                          c.email,
                          TO_CHAR(c.birthday, 'YYYY-MM-DD') AS birthday,
                          g.name AS group_name,
                          c.created_at::TEXT
                   FROM contacts c
                   LEFT JOIN groups g ON g.id = c.group_id
                   ORDER BY c.username"""
            )
            contacts = [dict(r) for r in cur.fetchall()]

            for contact in contacts:
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
                    (contact["id"],)
                )
                contact["phones"] = [dict(r) for r in cur.fetchall()]
                del contact["id"]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print(f"  Exported {len(contacts)} contacts to '{filepath}'.")


def import_from_json(filepath="contacts_export.json"):
    """Import contacts from JSON. On duplicate username: ask skip or overwrite."""
    if not os.path.exists(filepath):
        print(f"  File '{filepath}' not found.")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    skipped = inserted = overwritten = 0

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            for c in data:
                username = c.get("username", "").strip()
                if not username:
                    continue

                cur.execute("SELECT id FROM contacts WHERE username = %s", (username,))
                existing = cur.fetchone()

                if existing:
                    choice = input(
                        f"  '{username}' already exists. [s]kip / [o]verwrite? "
                    ).strip().lower()
                    if choice != "o":
                        skipped += 1
                        continue
                    cur.execute("DELETE FROM phones WHERE contact_id = %s", (existing[0],))
                    group_id = get_group_id(cur, c.get("group_name"))
                    cur.execute(
                        """UPDATE contacts
                           SET first_name=%s, last_name=%s, email=%s,
                               birthday=%s, group_id=%s
                           WHERE id=%s""",
                        (c.get("first_name"), c.get("last_name"),
                         c.get("email"), c.get("birthday"),
                         group_id, existing[0])
                    )
                    contact_id = existing[0]
                    overwritten += 1
                else:
                    group_id = get_group_id(cur, c.get("group_name"))
                    cur.execute(
                        """INSERT INTO contacts
                               (username, first_name, last_name, email, birthday, group_id)
                           VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
                        (username, c.get("first_name"), c.get("last_name"),
                         c.get("email"), c.get("birthday"), group_id)
                    )
                    contact_id = cur.fetchone()[0]
                    inserted += 1

                for p in c.get("phones", []):
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                        (contact_id, p["phone"], p.get("type", "mobile"))
                    )

        conn.commit()

    print(f"  Import complete: {inserted} inserted, {overwritten} overwritten, {skipped} skipped.")


def import_from_csv(filepath="contacts.csv"):
    """
    Extended CSV import supporting new fields.
    Expected columns (order-independent, header required):
      username, first_name, last_name, email, birthday,
      group, phone, phone_type
    Multiple phones per contact: repeat rows with same username.
    """
    if not os.path.exists(filepath):
        print(f"  File '{filepath}' not found.")
        return

    inserted = skipped = 0

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    contacts_map = {}
    for row in rows:
        uname = row.get("username", "").strip()
        if not uname:
            continue
        if uname not in contacts_map:
            contacts_map[uname] = {
                "first_name": row.get("first_name", ""),
                "last_name":  row.get("last_name", ""),
                "email":      row.get("email", ""),
                "birthday":   row.get("birthday", "") or None,
                "group":      row.get("group", ""),
                "phones":     [],
            }
        phone = row.get("phone", "").strip()
        if phone:
            contacts_map[uname]["phones"].append({
                "phone": phone,
                "type":  row.get("phone_type", "mobile") or "mobile",
            })

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            for username, data in contacts_map.items():
                cur.execute(
                    "SELECT id FROM contacts WHERE username = %s", (username,)
                )
                if cur.fetchone():
                    skipped += 1
                    continue
                group_id = get_group_id(cur, data["group"])
                cur.execute(
                    """INSERT INTO contacts
                           (username, first_name, last_name, email, birthday, group_id)
                       VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (username, data["first_name"], data["last_name"],
                     data["email"] or None, data["birthday"], group_id)
                )
                contact_id = cur.fetchone()[0]
                for p in data["phones"]:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                        (contact_id, p["phone"], p["type"])
                    )
                inserted += 1
        conn.commit()

    print(f"  CSV import: {inserted} inserted, {skipped} skipped (duplicate usernames).")


def call_add_phone(contact_name, phone, phone_type="mobile"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL add_phone(%s, %s, %s)",
                (contact_name, phone, phone_type)
            )
        conn.commit()


def call_move_to_group(contact_name, group_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL move_to_group(%s, %s)",
                (contact_name, group_name)
            )
        conn.commit()


def show_results(rows, title="Results"):
    clear()
    print(f"=== {title} ({len(rows)} found) ===\n")
    if not rows:
        print("  Nothing found.")
    for row in rows:
        print_contact_row(row)
    pause()


def menu_search():
    while True:
        clear()
        print("=== Search & Filter ===")
        print("  1. Search all fields (name / email / phone)")
        print("  2. Filter by group")
        print("  3. Search by email")
        print("  4. Browse with pagination")
        print("  0. Back")
        choice = input("> ").strip()

        if choice == "1":
            q = input("Search query: ").strip()
            show_results(search_all(q), f"Search: '{q}'")

        elif choice == "2":
            group = input("Group name (Family/Work/Friend/Other): ").strip()
            show_results(filter_by_group(group), f"Group: {group}")

        elif choice == "3":
            email = input("Email fragment: ").strip()
            show_results(search_by_email(email), f"Email contains: '{email}'")

        elif choice == "4":
            clear()
            size = input("Page size [5]: ").strip() or "5"
            g_filter = input("Group filter (leave blank for all): ").strip() or None
            sort = input("Sort by (username/birthday/created_at) [username]: ").strip() or "username"
            paginated_browse(int(size), g_filter, sort)

        elif choice == "0":
            return


def menu_add_contact():
    clear()
    print("=== Add New Contact ===")
    username   = input("Username (required): ").strip()
    if not username:
        print("  Username cannot be empty.")
        pause()
        return
    first_name = input("First name: ").strip()
    last_name  = input("Last name : ").strip()
    email      = input("Email     : ").strip()
    birthday   = input("Birthday (YYYY-MM-DD, or blank): ").strip() or None
    group      = input("Group (Family/Work/Friend/Other): ").strip()

    phones = []
    while True:
        phone = input("Phone number (blank to stop): ").strip()
        if not phone:
            break
        ptype = input("  Type (home/work/mobile) [mobile]: ").strip() or "mobile"
        phones.append({"phone": phone, "type": ptype})

    add_contact(username, first_name, last_name, email, birthday, group, phones)
    pause()


def menu_add_phone():
    clear()
    print("=== Add Phone to Existing Contact ===")
    uname = input("Username: ").strip()
    phone = input("Phone   : ").strip()
    ptype = input("Type (home/work/mobile) [mobile]: ").strip() or "mobile"
    try:
        call_add_phone(uname, phone, ptype)
        print("  Done.")
    except Exception as e:
        print(f"  Error: {e}")
    pause()


def menu_move_group():
    clear()
    print("=== Move Contact to Group ===")
    uname = input("Username  : ").strip()
    group = input("Group name: ").strip()
    try:
        call_move_to_group(uname, group)
        print("  Done.")
    except Exception as e:
        print(f"  Error: {e}")
    pause()


def menu_import_export():
    while True:
        clear()
        print("=== Import / Export ===")
        print("  1. Export contacts to JSON")
        print("  2. Import contacts from JSON")
        print("  3. Import contacts from CSV")
        print("  0. Back")
        choice = input("> ").strip()

        if choice == "1":
            path = input("Output file [contacts_export.json]: ").strip() or "contacts_export.json"
            export_to_json(path)
            pause()
        elif choice == "2":
            path = input("Input file [contacts_export.json]: ").strip() or "contacts_export.json"
            import_from_json(path)
            pause()
        elif choice == "3":
            path = input("CSV file [contacts.csv]: ").strip() or "contacts.csv"
            import_from_csv(path)
            pause()
        elif choice == "0":
            return


def main_menu():
    while True:
        clear()
        print("╔══════════════════════════════╗")
        print("║   PhoneBook — TSIS 1         ║")
        print("╠══════════════════════════════╣")
        print("║  1. Add contact              ║")
        print("║  2. Add phone to contact     ║")
        print("║  3. Move contact to group    ║")
        print("║  4. Search & Filter          ║")
        print("║  5. Import / Export          ║")
        print("║  0. Exit                     ║")
        print("╚══════════════════════════════╝")
        choice = input("> ").strip()

        if choice == "1":
            menu_add_contact()
        elif choice == "2":
            menu_add_phone()
        elif choice == "3":
            menu_move_group()
        elif choice == "4":
            menu_search()
        elif choice == "5":
            menu_import_export()
        elif choice == "0":
            print("Bye!")
            sys.exit(0)


if __name__ == "__main__":
    main_menu()