from pathlib import Path
from app.db import get_connection
import re


def curata_sql(text):
    """Elimină comentariile SQL și spațiile inutile pentru a evita erorile de sintaxă."""
    text = re.sub(r'--.*', '', text)
    return text.strip()


def create_tables():
    project_root = Path(__file__).resolve().parent.parent
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1. Executam Schema SQL (Tabele)
        schema_path = project_root / "sql" / "schema.sql"
        sql_text = schema_path.read_text(encoding="utf-8")
        statements = [s.strip() for s in sql_text.split(";") if s.strip()]

        for stmt in statements:
            cur.execute(stmt)
        print("OK: Tabelele au fost create cu succes!")

        # 2. Executăm Triggerele (Validari)
        triggers_path = project_root / "sql" / "triggers.sql"
        if triggers_path.exists():
            triggers_text = triggers_path.read_text(encoding="utf-8")
            trigger_blocks = [b.strip() for b in triggers_text.split("-- TRIGGER_END") if b.strip()]

            for block in trigger_blocks:
                sql_curat = curata_sql(block)
                if sql_curat:
                    cur.execute(sql_curat)
            print("OK: Triggerele au fost create cu succes!")

        # 3. Executăm Procedurile Stocate (Logica complexa)
        procedures_path = project_root / "sql" / "procedures.sql"
        if procedures_path.exists():
            procedures_text = procedures_path.read_text(encoding="utf-8")
            # Separăm după markerul special definit în fișierul .sql
            proc_blocks = [b.strip() for b in procedures_text.split("-- PROC_END") if b.strip()]

            for block in proc_blocks:
                sql_curat = curata_sql(block)
                if sql_curat:
                    cur.execute(sql_curat)
            print("OK: Procedurile stocate au fost create cu succes!")

        conn.commit()
        print("\n=== CONFIGURARE BAZĂ DE DATE FINALIZATĂ CU SUCCES ===")

    except Exception as e:
        conn.rollback()
        print(f"\nEROARE CRITICĂ: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    create_tables()