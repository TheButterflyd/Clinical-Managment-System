from app.db import run_execute
from scripts.create_tables import create_tables

print("Stergem tabelele existente (daca exista)")

# Atentie la ordine: stergem copiii inaintea parintilor!
# Mai intai user_log si Programari (care depind de medici si pacienti)
run_execute("DROP TABLE IF EXISTS user_log;")
run_execute("DROP TABLE IF EXISTS Programari;")

# Apoi parintii
run_execute("DROP TABLE IF EXISTS Medici;")
run_execute("DROP TABLE IF EXISTS Pacienti;")

print("Creez tabelele din schema sql...")
create_tables()

print("Rebuild gata!")