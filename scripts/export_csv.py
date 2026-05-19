import csv
import sys
from pathlib import Path

# Adăugăm rădăcina proiectului în path pentru a importa conexiunea
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.db import get_connection

# Securitate: Whitelist pentru tabelele sistemului medical
ALLOWED_TABLES = {
    "Pacienti",
    "Medici",
    "Programari",
    "Consultatii",
    "Facturi",
    "user_log"
}


def export_table(table: str, out_dir: Path = Path("exports")):
    table = table.strip()


    if table not in ALLOWED_TABLES:
        raise ValueError(f"Tabel invalid. Alege din: {sorted(ALLOWED_TABLES)}")


    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{table}.csv"

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(f"SELECT * FROM {table};")
        rows = cur.fetchall()


        cols = [d[0] for d in cur.description]


        with out_path.open(mode="w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)

        print(f"EXPORT OK -> {out_path} (randuri: {len(rows)})")

    finally:

        cur.close()
        conn.close()


if __name__ == "__main__":
    t_input = input(f"Tabel ({', '.join(sorted(ALLOWED_TABLES))}): ").strip()
    try:
        export_table(t_input)
    except Exception as e:
        print(f" Eroare: {e}")