import json
from pathlib import Path
from app.db import run_select

# Pragul minim de consultații (echivalentul lui MIN_STOCK)
MIN_CONSULTATIONS = 1

sql = """
SELECT 
    m.id_medic,
    m.nume,
    m.specializare,
    COUNT(c.id_consult) AS total_consultatii
FROM Medici m
LEFT JOIN Programari p ON m.id_medic = p.id_medic
LEFT JOIN Consultatii c ON p.id_programare = c.id_prog
GROUP BY m.id_medic, m.nume, m.specializare
HAVING total_consultatii >= %s
ORDER BY total_consultatii DESC;
"""

rows = run_select(sql, (MIN_CONSULTATIONS,))

# Construim lista de rezultate (lista de dicționare)
results = []
for r in rows:
    results.append({
        "id_medic": r[0],           # Echivalentul lui "sku"
        "nume_medic": r[1],         # Echivalentul lui "name"
        "specializare": r[2],       # Info extra
        "nr_consultatii": int(r[3]) # Echivalentul lui "stock"
    })

# Structura finală a obiectului JSON
final_data = {
    "min_consultations": MIN_CONSULTATIONS,
    "results": results
}

# Salvare în folderul outputs
out_path = Path("outputs") / "medici_performanti_filtered.json"
out_path.parent.mkdir(exist_ok=True)

out_path.write_text(
    json.dumps(final_data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON salvat cu succes în: {out_path}")