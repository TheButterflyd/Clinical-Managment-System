import sys
import time
from pathlib import Path
import subprocess
from datetime import datetime


RUN_EVERY = 5
CYCLES = 5


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports.py"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


LOG_PATH = OUT_DIR / "audit_scheduler.log"


def log(msg):
    """Scrie mesajele de jurnalizare în fișierul de audit cu timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}\n"


    if LOG_PATH.exists():
        current_content = LOG_PATH.read_text(encoding="utf-8")
        LOG_PATH.write_text(current_content + line, encoding="utf-8")
    else:
        LOG_PATH.write_text(line, encoding="utf-8")


def main():
    print("=== START AUTOMATIZARE RAPOARTE CLINICĂ ===")
    print("Script BI țintă:", REPORTS)
    print("Director ieșire:", OUT_DIR)
    print("-------------------------------------------")

    log("=== Pornire Scheduler Automatizare Rapoarte ===")

    for i in range(1, CYCLES + 1):
        print(f"\n[Ciclu {i}/{CYCLES}] Se inițiază generarea raportului...")
        log(f"Ciclu {i} pornit - Generare Raport Activitate Medici")


        res = subprocess.run(
            args=[sys.executable, str(REPORTS)],
            cwd=str(ROOT),
            capture_output=True,
            text=True
        )

        print(f"\n=== Rezultat Consolă Raport (Ciclu {i}) ===")
        if res.stdout:
            print(res.stdout.strip())

        if res.stderr:
            print(f" STDERR:\n{res.stderr.strip()}")

        if res.returncode != 0:
            error_msg = f"Ciclu {i} EȘUAT cu codul {res.returncode}"
            print(f" {error_msg}")
            log(error_msg)
            break
        else:
            success_msg = f"Ciclu {i} FINALIZAT CU SUCCES (OK)"
            print(f" {success_msg}")
            log(success_msg)

        if i < CYCLES:
            print(f"Se așteaptă {RUN_EVERY} secunde până la următorul ciclu...")
            time.sleep(RUN_EVERY)

    print("\n=== SFÂRȘIT PROCES AUTOMATIZARE ===")
    log("=== Oprire Scheduler Automatizare - Toate ciclurile procesate ===")


if __name__ == "__main__":
    main()