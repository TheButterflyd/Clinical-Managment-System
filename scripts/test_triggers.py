from app.db import run_execute, run_select

print("--- TEST TRIGGER BEFORE INSERT (Facturi) ---")
res_cons = run_select("SELECT id_consult FROM Consultatii LIMIT 1;")
if not res_cons:
    print("EROARE: Nu exista consultatii in DB. Ruleaza seed.py mai intai!")
    exit()

id_c = res_cons[0][0]

print(f"1. Inserare valida (Suma = 200)")
try:
    run_execute(
        "INSERT INTO Facturi (id_consult, Suma, Data_platii) VALUES (%s, %s, CURRENT_DATE);",
        (id_c, 200)
    )
    print("OK: Inserarea valida a reusit")
except Exception as e:
    print("EROARE (nu trebuia):", e)

print(f"\n2. Inserare invalida (Suma = -50)")
try:
    run_execute(
        "INSERT INTO Facturi (id_consult, Suma, Data_platii) VALUES (%s, %s, CURRENT_DATE);",
        (id_c, -50)
    )
    print("EROARE: Inserarea invalida a trecut (Trigger-ul NU functioneaza!)")
except Exception as e:
    print("OK: Inserarea a fost respinsa de trigger (asa cum trebuia)")
    print("Mesaj baza de date:", e)


print("\n--- TEST TRIGGER AFTER UPDATE (Pacienti) ---")
res_pac = run_select("SELECT id_pacient, nume FROM Pacienti LIMIT 1;")
id_p = res_pac[0][0]
nume_vechi = res_pac[0][1]

print(f"Facem update pe pacientul: {nume_vechi}")
run_execute("UPDATE Pacienti SET nume=%s WHERE id_pacient=%s;", (nume_vechi + " (Modificat)", id_p))

print("Verificam daca trigger-ul a scris in user_log...")
logs = run_select("SELECT action, detalii FROM user_log ORDER BY id DESC LIMIT 1;")

if logs:
    print(f"LOG GASIT: Actiune: {logs[0][0]} | Detalii: {logs[0][1]}")
else:
    print("EROARE: Nu s-a gasit niciun log in tabelul user_log!")

print("\n--- TEST TRIGGERE FINALIZAT ---")