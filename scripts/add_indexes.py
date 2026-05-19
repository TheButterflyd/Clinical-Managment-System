import time
from app.db import run_execute


def apply_indexes():
    print("=== APLICARE INDEX PENTRU OPTIMIZARE CLINICĂ ===")


    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_pacienti_cnp ON Pacienti(cnp);",
        "CREATE INDEX IF NOT EXISTS idx_medici_specializare ON Medici(specializare);",
        "CREATE INDEX IF NOT EXISTS idx_programari_data ON Programari(data_programare);"
    ]

    for query in index_queries:
        print(f"Rulam: {query}")
        try:
            start_time = time.time()
            run_execute(query)
            end_time = time.time()

            duration = (end_time - start_time) * 1000  # convertim in milisecunde
            print(f"-> Succes! (Durata creare: {duration:.2f} ms)\n")
        except Exception as e:
            print(f"-> Eroare la crearea indexului: {e}\n")

    print("Indexuri clinice aplicate cu succes.")
    print("------------------------------------------")


if __name__ == "__main__":
    apply_indexes()