import random
from app.db import run_execute, run_select


def populate_procedural():
    print("Generare medici...")
    specializari = ["Cardiologie", "Pediatrie", "Dermatologie", "Neurologie", "Ginecologie"]
    for i in range(1, 11):
        nume_medic = f"Dr. Medic_{i}"
        spec = random.choice(specializari)
        run_execute("INSERT INTO Medici (nume, specializare) VALUES (%s, %s);", param=(nume_medic, spec))

    print("Generare 100 pacienti...")
    for i in range(1, 101):
        nume_pacient = f"Pacient_Anonim_{i}"
        cnp_fictiv = f"{random.randint(1000000000000, 2999999999999)}"
        run_execute("INSERT INTO Pacienti (nume, cnp) VALUES (%s, %s);", param=(nume_pacient, cnp_fictiv))


    medic_ids = [row[0] for row in run_select("SELECT id_medic FROM Medici;")]
    pacient_ids = [row[0] for row in run_select("SELECT id_pacient FROM Pacienti;")]

    print(f"Generare programari (vă rugăm așteptați)...")
    count = 0
    for p_id in pacient_ids:

        for _ in range(5):
            m_id = random.choice(medic_ids)
            zi = random.randint(1, 28)
            ora = random.randint(8, 16)
            data_fictiva = f"2026-04-{zi:02d} {ora:02d}:00:00"

            run_execute("INSERT INTO Programari (id_medic, id_pacient, data_programare) VALUES (%s, %s, %s);",
                        param=(m_id, p_id, data_fictiva))


            run_execute("INSERT INTO user_log (id_pacient, action, detalii) VALUES (%s, %s, %s);",
                        param=(p_id, "PROGRAMARE_AUTOMATA", f"Programat la medicul ID: {m_id}"))

            count += 1
            if count % 100 == 0:
                print(f"Progres: {count} programări inserate...")

    print(f"Succes! Total înregistrări noi în Programari: {count}")


if __name__ == "__main__":
    populate_procedural()