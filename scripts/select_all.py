import json
from pathlib import Path
from app.db import run_select

# SQL care uneste Pacienti cu Consultatii si Facturi
sql = """
SELECT 
    p.id_pacient,
    p.nume,
    p.cnp,
    COUNT(DISTINCT c.id_consult) AS nr_consultatii,
    COALESCE(SUM(f.Suma), 0) AS total_incasat
FROM Pacienti p
LEFT JOIN Programari pr ON p.id_pacient = pr.id_pacient
LEFT JOIN Consultatii c ON pr.id_programare = c.id_prog
LEFT JOIN Facturi f ON c.id_consult = f.id_consult
GROUP BY p.id_pacient, p.nume, p.cnp
ORDER BY p.nume;
"""

rows = run_select(sql)

data = []
for r in rows:
    data.append({
        "id": r[0],
        "nume": r[1],
        "cnp": r[2],
        "nr_consultatii": r[3],
        "total_plata": float(r[4]) # Convertim din Decimal in float pentru JSON
    })

# Salvare in folderul outputs
out_path = Path("outputs") / "raport_pacienti.json"
out_path.parent.mkdir(exist_ok=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON raport salvat: {out_path}")