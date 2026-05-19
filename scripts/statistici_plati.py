import json
from pathlib import Path
from app.db import run_select

# SQL care grupeaza platile pe luni si calculeaza media sumelor
sql = """
SELECT 
    DATE_FORMAT(Data_platii, '%Y-%m') AS luna_platii,
    COUNT(*) AS numar_plati,
    AVG(Suma) AS medie_incasari
FROM Facturi
GROUP BY luna_platii
ORDER BY luna_platii DESC;
"""

rows = run_select(sql)

data = []
for r in rows:
    data.append({
        "luna": r[0],
        "numar_plati": int(r[1]),
        "valoare_medie": float(r[2]) if r[2] is not None else 0.0
    })

# Salvare in folderul outputs sub un nume relevant
out_path = Path("outputs") / "statistici_plati.json"
out_path.parent.mkdir(exist_ok=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON statistici salvat: {out_path}")