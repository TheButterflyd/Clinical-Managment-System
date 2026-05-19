import random
from faker import Faker
from app.db import run_execute, run_select

fake = Faker('ro_RO')

NUM_MEDICI = 10
NUM_PACIENTI = 50
NUM_PROGRAMARI = 100

print("--- 1. Inseram Medici ---")
specializari = ["Cardiologie", "Dermatologie", "Pediatrie", "Neurologie", "ORL", "Gastroenterologie"]
for _ in range(NUM_MEDICI):
    run_execute(
        "INSERT INTO Medici (nume, specializare) VALUES (%s, %s);",
        ("Dr. " + fake.last_name(), random.choice(specializari))
    )

print("--- 2. Inseram Pacienti ---")
for _ in range(NUM_PACIENTI):
    run_execute(
        "INSERT INTO Pacienti (nume, cnp) VALUES (%s, %s);",
        (fake.name(), fake.unique.numerify(text="###########"))
    )

print("--- 3. Generam Programari, Consultatii si Facturi ---")
medici_ids = [row[0] for row in run_select("SELECT id_medic FROM Medici;")]
pacienti_ids = [row[0] for row in run_select("SELECT id_pacient FROM Pacienti;")]

for _ in range(NUM_PROGRAMARI):
    m_id = random.choice(medici_ids)
    p_id = random.choice(pacienti_ids)
    data_falsa = fake.date_time_between(start_date='-60d', end_date='+30d')
    data_str = data_falsa.strftime('%Y-%m-%d %H:%M:%S')

    # 1. Inserăm Programarea
    run_execute("""
        INSERT INTO Programari (id_medic, id_pacient, data_programare) 
        VALUES (%s, %s, %s);
    """, (m_id, p_id, data_str))

    # 2. Dacă e în trecut, facem restul folosind sub-selecții
    if data_str < "2026-03-30 00:00:00":
        # Inserăm Consultatia legată de ULTIMA programare creată
        run_execute("""
            INSERT INTO Consultatii (id_prog, Diagnostic, Recomandari) 
            VALUES ((SELECT MAX(id_programare) FROM Programari), %s, %s);
        """, (fake.sentence(nb_words=4), "Control obligatoriu"))

        # Inserăm Factura legată de ULTIMA consultație creată
        run_execute("""
            INSERT INTO Facturi (id_consult, Suma, Data_platii) 
            VALUES ((SELECT MAX(id_consult) FROM Consultatii), %s, %s);
        """, (random.choice([150.00, 250.00, 500.00]), data_str.split(' ')[0]))

        # Inserăm Tratamentul legat de ULTIMA consultație creată
        run_execute("""
            INSERT INTO Tratamente_Retete (id_consult, Medicament, Dozaj) 
            VALUES ((SELECT MAX(id_consult) FROM Consultatii), %s, %s);
        """, (fake.word().capitalize(), "1 tableta/zi"))

print("--- 4. Generam Log-uri pentru pacienti ---")
for _ in range(15):
    p_id = random.choice(pacienti_ids)
    run_execute(
        "INSERT INTO user_log (id_pacient, action, detalii) VALUES (%s, %s, %s);",
        (p_id, "LOGIN", "Accesare fisa medicala online")
    )

print("\n[SUCCESS] Baza de date 'clinica_medicala' a fost populata procedural fara erori!")