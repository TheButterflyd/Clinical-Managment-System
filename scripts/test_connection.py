from app.db import run_select

result = run_select("SELECT DATABASE() AS db_name, 'Conexiunea avut loc cu success!' AS STATUS;")
print(result)

