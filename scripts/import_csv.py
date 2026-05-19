import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.db import get_connection

ALLOWED_TABLES = {"Pacienti", "Medici", "Programari", "Consultatii", "Facturi", "user_log"}

# Coloane controlate de DB care trebuie ignorate la import[cite: 1]
AUTO_SKIP_COLS = {"id_pacient", "id_medic", "id_programare", "id_consult", "id_factura", "created_at"}


def get_table_columns(cur, table: str) -> set[str]:
    # Interogare dinamică a schemei tabelului[cite: 1]
    cur.execute(f"DESCRIBE {table};")
    return {row[0] for row in cur.fetchall()}


def import_table_from_csv(table: str, csv_path: Path, truncate_first: bool = False):
    table = table.strip()

    if table not in ALLOWED_TABLES:
        raise ValueError(f"Tabel invalid. Alege din: {sorted(ALLOWED_TABLES)}")

    if not csv_path.exists():
        raise FileNotFoundError(f"Nu exista CSV: {csv_path}")

    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    skipped = 0

    try:
        table_cols = get_table_columns(cur, table)

        with csv_path.open(mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames:
                raise ValueError("CSV invalid: lipseste header-ul.")

            # Filtrare header CSV pentru a obține doar coloanele valide[cite: 1]
            cols = []
            for c in reader.fieldnames:
                c = c.strip()
                if c in AUTO_SKIP_COLS: continue
                if c in table_cols: cols.append(c)

            if not cols:
                raise ValueError("Nu am coloane importabile.")

            # Construire dinamică interogare parametrizată[cite: 1]
            placeholders = ", ".join(["%s"] * len(cols))
            col_list = ", ".join(cols)
            sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders});"

            # Start tranzacție (Atomicitate)[cite: 1]
            conn.begin()

            if truncate_first:
                cur.execute(f"TRUNCATE TABLE {table};")

            for i, row in enumerate(reader, start=2):
                values = []
                empty_row = True

                # Curățare și pregătire date (Data Sanitization)[cite: 1]
                for c in cols:
                    val = row.get(c)
                    if val is None: val = ""
                    val = val.strip()
                    if val != "": empty_row = False
                    values.append(val if val != "" else None)  # NULL în DB[cite: 1]

                if empty_row:
                    skipped += 1
                    continue

                cur.execute(sql, tuple(values))
                inserted += 1

            # Validare permanentă a datelor[cite: 1]
            conn.commit()
            print(f"IMPORT OK -> table={table}, inserted={inserted}, skipped={skipped}")

    except Exception as e:
        # Anulare totală în caz de eroare (Rollback)[cite: 1]
        conn.rollback()
        print(f" IMPORT FAIL -> rollback. Eroare: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    t_input = input(f"Tabel ({', '.join(sorted(ALLOWED_TABLES))}): ").strip()
    p_input = input("Cale CSV (ex: exports/Medici.csv): ").strip()
    truncate = input("TRUNCATE inainte? (y/n): ").strip().lower() == "y"

    try:
        import_table_from_csv(t_input, Path(p_input), truncate_first=truncate)
    except Exception as e:
        print(f"Eroare: {e}")