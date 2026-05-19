import json
from app.db import get_connection, run_select

print("=== SERVICIU PROGRAMĂRI CLINICĂ ===")


pacient_id = run_select("SELECT id_pacient FROM Pacienti LIMIT 1;")[0][0]
medic_id = run_select("SELECT id_medic FROM Medici LIMIT 1;")[0][0]


servicii = [
    {"nume": "Consultație Generală", "pret": 150.0},
    {"nume": "Ecografie Abdominală", "pret": 250.0},
    {"nume": "Analize Sânge - Set Complet", "pret": 320.0}
]
servicii_json = json.dumps(servicii)

print(f"Apelăm procedura pentru Pacient ID: {pacient_id}...")

conn = get_connection()
cur = conn.cursor()

try:

    cur.execute("CALL inregistreaza_programare_completa(%s, %s, %s);",
                (pacient_id, medic_id, servicii_json))


    row = cur.fetchone()
    prog_id = row[0]


    while cur.nextset():
        if cur.description is not None:
            cur.fetchall()

    conn.commit()
    print("OK: Programarea și facturile au fost create. ID Programare =", prog_id)

finally:
    cur.close()
    conn.close()

print("\n--- Verificare în DB (Facturi generate automat) ---")
rows = run_select("""
    SELECT f.id_factura, f.Suma, f.Data_platii
    FROM Facturi f
    WHERE f.id_consult = %s
    ORDER BY f.id_factura;
""", (prog_id,))

for r in rows:
    print(f"Factură găsită -> ID: {r[0]} | Sumă: {r[1]} RON | Data: {r[2]}")