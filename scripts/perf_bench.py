import time
import statistics
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from app.db import run_select, run_execute

# Configurații test
RUNS = 50
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
CHART_FILE = OUTPUT_DIR / "performanta_clinica.png"

# Query-urile pe care vrem să le testăm (cele care pot fi lente fără index)
TEST_QUERIES = [
    {
        "name": "Căutare după CNP (Pacient)",
        "sql": "SELECT * FROM Pacienti WHERE cnp = %s;",
        "params": ("1234567890123",),  # Un CNP de test din seed.py
    },
    {
        "name": "Filtrare Specializare (Medic)",
        "sql": "SELECT * FROM Medici WHERE specializare = %s;",
        "params": ("Cardiologie",),
    }
]

# SQL pentru crearea indexurilor care vor optimiza query-urile de mai sus
INDEX_SQL = [
    "CREATE INDEX idx_pacienti_cnp ON Pacienti(cnp);",
    "CREATE INDEX idx_medici_specializare ON Medici(specializare);",
]


def benchmark_query(sql, params, runs):
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        run_select(sql, params)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convertim în milisecunde
    return times


def run_suite(label):
    results = {}
    for q in TEST_QUERIES:
        times = benchmark_query(q["sql"], q["params"], RUNS)
        avg = statistics.mean(times)
        results[q["name"]] = {"avg": avg}
        print(f"[{label}] {q['name']} -> medie {avg:.4f} ms")
    return results


def generate_chart(before_results, after_results):
    labels = list(before_results.keys())
    before_means = [before_results[name]["avg"] for name in labels]
    after_means = [after_results[name]["avg"] for name in labels]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, before_means, width, label='Fără Index (Lent)', color='#e74c3c')
    ax.bar(x + width / 2, after_means, width, label='Cu Index (Rapid)', color='#2ecc71')

    ax.set_ylabel('Timp mediu (ms)')
    ax.set_title('Impactul Indexării asupra Clinicii Medicale')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    plt.savefig(CHART_FILE)
    print(f"\nGrafic de performanță salvat: {CHART_FILE}")
    plt.show()


def main():
    print("=== START TEST PERFORMANȚĂ CLINICĂ ===\n")

    # 1. Testăm performanța pe baza curată (fără indexuri noi)
    before = run_suite("BEFORE")

    # 2. Aplicăm indexurile pentru optimizare
    print("\nAplicăm optimizările (INDEX)...")
    for stmt in INDEX_SQL:
        try:
            run_execute(stmt)
        except:
            pass  # Ignorăm dacă indexul există deja

    # 3. Testăm din nou să vedem diferența
    after = run_suite("AFTER")

    # 4. Generăm graficul comparativ
    generate_chart(before, after)


if __name__ == "__main__":
    main()