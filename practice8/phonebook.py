# phonebook.py
from connect import get_connection

def search_contacts(pattern):
    """
    Search contacts by name or phone pattern.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
            return cur.fetchall()

def upsert_contact(name, phone):
    """
    Insert or update a contact by name.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        # Changes will be committed on exiting the with-block.

def bulk_insert(contacts):
    """
    Bulk insert contacts. Each contact is a tuple (name, phone).
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for name, phone in contacts:
                try:
                    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
                except Exception as e:
                    print(f"Error inserting {name} ({phone}): {e}")
        # Changes will be committed on exit.

def get_contacts_paginated(limit, offset):
    """
    Retrieve contacts with pagination.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
            return cur.fetchall()

def delete_contact(name=None, phone=None):
    """
    Delete a contact by name or phone.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s, %s)", (name, phone))
        # Changes will be committed on exit.

if __name__ == "__main__":
    # Example usage
    print(search_contacts("John"))
    upsert_contact("Alice", "555-1234")
    bulk_insert([
        ("Bob", "999-9999"),
        ("Carol", "invalid_phone")
    ])
    print(get_contacts_paginated(10, 0))
    delete_contact(name="Alice")
