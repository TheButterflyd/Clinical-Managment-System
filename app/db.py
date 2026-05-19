import os
import mariadb
import sys
from dotenv import load_dotenv

# Încarcă variabilele din fișierul .env
load_dotenv()


def get_connection():
    """
    Creează și returnează o conexiune către baza de date MariaDB.
    """
    try:
        conn = mariadb.connect(
            host=os.getenv('DB_HOST', "127.0.0.1"),
            port=int(os.getenv('DB_PORT', "3307")),
            user=os.getenv('DB_USER', "root"),
            password=os.getenv('DB_PASSWORD', "rootpass"),
            # Am schimbat DB_DATABASE în DB_NAME pentru a se potrivi cu fișierul tău .env
            database=os.getenv('DB_NAME', "inventory_system"),
        )
        return conn
    except mariadb.Error as e:
        print(f"Eroare la conectarea cu MariaDB: {e}")
        sys.exit(1)


def run_select(sql, param=()):
    """
    Execută un query SQL de tip SELECT și returnează toate rândurile găsite.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql, param)
        rows = cur.fetchall()
        return rows
    except mariadb.Error as e:
        print(f"Eroare la execuția SELECT: {e}")
        return []
    finally:
        # Închidem resursele o singură dată pentru a evita ProgrammingError
        cur.close()
        conn.close()


def run_execute(sql, param=()):
    """
    Execută comenzi SQL de tip INSERT, UPDATE sau DELETE (cu commit).
    Returnează numărul de rânduri afectate.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql, param)
        conn.commit()
        affected = cur.rowcount
        return affected
    except mariadb.Error as e:
        print(f"Eroare la execuția SQL: {e}")
        conn.rollback()  # Anulează modificările în caz de eroare
        return 0
    finally:
        cur.close()
        conn.close()


def cleanup_database():
    print("=== Începere ștergere tabele clinică ===")


    run_execute("DROP TABLE IF EXISTS Facturi;")
    run_execute("DROP TABLE IF EXISTS user_log;")
    run_execute("DROP TABLE IF EXISTS Tratamente_Retete;")


    run_execute("DROP TABLE IF EXISTS Consultatii;")


    run_execute("DROP TABLE IF EXISTS Programari;")


    run_execute("DROP TABLE IF EXISTS Medici;")
    run_execute("DROP TABLE IF EXISTS Pacienti;")

    print("=== Baza de date a fost curățată cu succes! ===")


if __name__ == "__main__":
    cleanup_database()