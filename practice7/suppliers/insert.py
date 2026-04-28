import psycopg2
from config import load_config

def contact_info():
    """ Create tables in the PostgreSQL database"""
    command1 = """INSERT INTO contacts (contact_name, contact_number) VALUES(%s,%s)"""
    command2 = """SELECT * FROM contacts"""
    command3 = """DELETE FROM contacts WHERE contact_name=%s"""
    command4 = """UPDATE contacts SET contact_name=%s WHERE contact_name=%s"""
    command5 = """UPDATE contacts SET contact_number=%s WHERE contact_name=%s"""

    a = int(input("1.Add contact\n2.Show contacts\n3.Delete contact\n4.Update name\n5.Update number\n"))

    if a == 1:
        name = input("Contact name: ")
        number = input("Contact number: ")
        try:
            config = load_config()
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.execute(command1, (name, number))
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

    elif a == 2:
        try:
            config = load_config()
            with psycopg2.connect(**config) as conn:  # ← был пустой connect()
                with conn.cursor() as cur:            # ← не было cursor()
                    cur.execute(command2)             # ← не был выполнен запрос
                    rows = cur.fetchall()
                    print("\n----Список контактов---")
                    for row in rows:
                        print(*row)
                    print("--------------------------\n")
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

    elif a == 3:
        dname = input("Name to delete: ")
        try:
            config = load_config()
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.execute(command3, (dname,))
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

    elif a == 4:
        uname = input("Name to update: ")   # ← была надпись "Name to delete" — опечатка
        nname = input("New name: ")
        try:
            config = load_config()
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.execute(command4, (nname, uname))
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

    elif a == 5:
        u_name = input("Name of contact: ")
        nnumber = input("New number: ")
        try:
            config = load_config()
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.execute(command5, (nnumber, u_name))
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

if __name__ == '__main__':
    contact_info()