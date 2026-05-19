from app.db import run_execute, run_select

print("Inseram medici")

run_execute("INSERT INTO Medici (nume, specializare) VALUES (%s, %s);", param=("Dr. Popescu Ion", "Cardiologie"))
run_execute("INSERT INTO Medici (nume, specializare) VALUES (%s, %s);", param=("Dr. Ionescu Maria", "Pediatrie"))

print("Inseram pacienti")
run_execute("INSERT INTO Pacienti (nume, cnp) VALUES (%s, %s);", param=("Vasile Andrei", "1234567890123"))
run_execute("INSERT INTO Pacienti (nume, cnp) VALUES (%s, %s);", param=("Elena Radu", "2987654321098"))

print("Inseram programari")
# Preluăm ID-urile folosind tot 'param'
m1 = run_select("SELECT id_medic FROM Medici WHERE nume=%s;", param=("Dr. Popescu Ion",))[0][0]
p1 = run_select("SELECT id_pacient FROM Pacienti WHERE nume=%s;", param=("Vasile Andrei",))[0][0]

run_execute("INSERT INTO Programari (id_medic, id_pacient, data_programare) VALUES (%s, %s, %s);",
            param=(m1, p1, "2026-05-20 10:30:00"))

print("Inseram log-uri")
run_execute("INSERT INTO user_log (id_pacient, action, detalii) VALUES (%s, %s, %s);",
            param=(p1, "PROGRAMARE_NOUA", "Pacientul a programat o consultatie la cardiologie"))

print("Datele au fost inserate cu succes!")