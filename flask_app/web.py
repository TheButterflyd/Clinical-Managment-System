import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Încărcăm variabilele de mediu pentru cheia de criptare
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from app.db import run_select, run_execute

app = Flask(__name__)
app.secret_key = "clinica-secret-key"

# --- CONFIGURARE CRIPTARE ---
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
cipher_suite = Fernet(ENCRYPTION_KEY.encode()) if ENCRYPTION_KEY else None


def safe_decrypt(text):
    """Decriptează textul doar dacă este un șir valid Fernet (începe cu gAAAA)."""
    if not cipher_suite or not text:
        return text
    try:
        if isinstance(text, str) and text.startswith("gAAAA"):
            return cipher_suite.decrypt(text.encode()).decode()
        return text
    except Exception:
        return "Eroare decriptare"


# --- CONFIGURARE CRUD ADAPTATĂ PENTRU SISTEM MEDICAL ---
CRUD_CONFIG = {
    "Pacienti": {
        "pk": "id_pacient",
        "title": "Pacienți",
        "create_fields": ["nume", "cnp", "password_hash"],
        "update_fields": ["nume", "cnp", "password_hash"],
        "list_fields": ["id_pacient", "nume", "cnp", "password_hash"],
        "default_sort": "id_pacient DESC",
        "children": [{"table": "Programari", "fk": "id_pacient"}],
    },
    "Medici": {
        "pk": "id_medic",
        "title": "Medici",
        "create_fields": ["nume", "specializare", "email"],
        "update_fields": ["specializare", "email"],
        "list_fields": ["id_medic", "nume", "specializare", "email"],
        "default_sort": "id_medic DESC",
        "children": [{"table": "Programari", "fk": "id_medic"}],
    },
    "Programari": {
        "pk": "id_programare",
        "title": "Programări",
        "create_fields": ["id_pacient", "id_medic", "data_programare"],
        "update_fields": ["data_programare"],
        "list_fields": ["id_programare", "id_pacient", "id_medic", "data_programare"],
        "default_sort": "data_programare DESC",
        "fk_dropdowns": {
            "id_pacient": ("Pacienti", "id_pacient", "nume"),
            "id_medic": ("Medici", "id_medic", "nume"),
        },
        "children": [{"table": "Consultatii", "fk": "id_prog"}],
    },
    "Consultatii": {
        "pk": "id_consult",
        "title": "Consultații",
        "create_fields": ["id_prog", "Diagnostic", "Recomandari"],
        "update_fields": ["Diagnostic", "Recomandari"],
        "list_fields": ["id_consult", "id_prog", "Diagnostic"],
        "default_sort": "id_consult DESC",
        "fk_dropdowns": {"id_prog": ("Programari", "id_programare", "id_programare")},
        "children": [{"table": "Facturi", "fk": "id_consult"}],
    },
    "Facturi": {
        "pk": "id_factura",
        "title": "Facturi",
        "create_fields": ["id_consult", "Suma", "Data_platii"],
        "update_fields": ["Suma", "Data_platii"],
        "list_fields": ["id_factura", "id_consult", "Suma", "Data_platii"],
        "default_sort": "id_factura DESC",
        "fk_dropdowns": {"id_consult": ("Consultatii", "id_consult", "id_consult")},
    },
    "user_log": {
        "pk": "id",
        "title": "Istoric Activități",
        "create_fields": ["id_pacient", "action", "detalii"],
        "update_fields": [],
        "list_fields": ["id", "id_pacient", "action", "detalii", "created_at"],
        "default_sort": "id DESC",
        "fk_dropdowns": {"id_pacient": ("Pacienti", "id_pacient", "nume")},
    },
}


# --- FUNCȚII SUPORT ---

def ensure_table_allowed(table):
    if table not in CRUD_CONFIG:
        abort(404)
    return CRUD_CONFIG[table]


def has_any_data():
    try:
        rows = run_select("SELECT id_pacient FROM Pacienti LIMIT 1;")
        return bool(rows)
    except Exception:
        return False


def record_exists(table, field, value):
    ensure_table_allowed(table)
    q = f"SELECT 1 FROM {table} WHERE {field}=%s LIMIT 1;"
    return bool(run_select(q, (value,)))


def fetch_list(table):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} ORDER BY {cfg.get('default_sort', pk + ' DESC')};"
    rows = run_select(q)

    # Decriptare dinamică pentru tabela Medici
    processed_rows = []
    if table == "Medici" and "email" in cols:
        email_idx = cols.index("email")
        for row in rows:
            r_list = list(row)
            r_list[email_idx] = safe_decrypt(r_list[email_idx])
            processed_rows.append(tuple(r_list))
        return cols, processed_rows

    return cols, rows


def fetch_by_id(table, rec_id):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} WHERE {pk}=%s LIMIT 1;"
    rows = run_select(q, (rec_id,))

    if rows and table == "Medici" and "email" in cols:
        r_list = list(rows[0])
        email_idx = cols.index("email")
        r_list[email_idx] = safe_decrypt(r_list[email_idx])
        return cols, tuple(r_list)

    return cols, (rows[0] if rows else None)


def build_fk_options(cfg):
    options = {}
    for field, spec in cfg.get("fk_dropdowns", {}).items():
        parent_table, parent_pk, label_col = spec
        rows = run_select(f"SELECT {parent_pk}, {label_col} FROM {parent_table} ORDER BY {parent_pk} DESC;")
        options[field] = [(str(r[0]), str(r[1])) for r in rows]
    return options


def insert_record(table, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["create_fields"]
    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Câmp obligatoriu lipsă: {f}")

        # Criptează email-ul medicului înainte de salvare în baza de date
        if table == "Medici" and f == "email" and cipher_suite:
            v = cipher_suite.encrypt(v.encode()).decode()

        values.append(v)
    cols = ", ".join(fields)
    placeholders = ", ".join(["%s"] * len(fields))
    q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders});"
    run_execute(q, tuple(values))


def update_record(table, rec_id, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["update_fields"]
    if not fields:
        raise ValueError("Acest tabel nu permite modificări.")
    pairs = [f"{f}=%s" for f in fields]
    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Câmp obligatoriu lipsă: {f}")

        # Criptează email-ul la modificări
        if table == "Medici" and f == "email" and cipher_suite:
            v = cipher_suite.encrypt(v.encode()).decode()
        values.append(v)
    values.append(rec_id)
    q = f"UPDATE {table} SET {', '.join(pairs)} WHERE {cfg['pk']}=%s;"
    run_execute(q, tuple(values))


def delete_record_safe(table, rec_id):
    cfg = ensure_table_allowed(table)
    for ch in cfg.get("children", []):
        run_execute(f"DELETE FROM {ch['table']} WHERE {ch['fk']}=%s;", (rec_id,))
    run_execute(f"DELETE FROM {table} WHERE {cfg['pk']}=%s;", (rec_id,))


def allowed_fields_for_table(table: str):
    cfg = ensure_table_allowed(table)
    fields = set()
    for k in ("create_fields", "update_fields", "list_fields"):
        for f in cfg.get(k, []):
            fields.add(f)
    fields.add(cfg["pk"])
    for f in cfg.get("fk_dropdowns", {}).keys():
        fields.add(f)
    return sorted(fields)


# --- RUTE (LABORATOR SQLi ȘI CRUD) ---

@app.route("/api/sqli/query", methods=["POST"])
def api_sqli_query():
    table = (request.form.get("table") or "").strip()
    field = (request.form.get("field") or "").strip()
    value = (request.form.get("value") or "").strip()
    mode = (request.form.get("mode") or "safe").strip().lower()

    ensure_table_allowed(table)

    allowed_fields = allowed_fields_for_table(table)
    if field not in allowed_fields:
        return {"ok": False, "error": f"Câmp invalid. Permise: {', '.join(allowed_fields)}"}, 400

    limit = 25

    try:
        if mode == "unsafe":
            sql = f"SELECT * FROM {table} WHERE {field} = '{value}' LIMIT {limit};"
            rows = run_select(sql)
        else:
            sql = f"SELECT * FROM {table} WHERE {field} = %s LIMIT {limit};"
            rows = run_select(sql, (value,))

        cols = [c[0] for c in run_select(f"SHOW COLUMNS FROM {table};")]
        data = [list(r) for r in rows]

        return {
            "ok": True,
            "mode": mode,
            "sql": sql,
            "columns": cols,
            "rows": data,
            "count": len(data),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "mode": mode}, 500


@app.route("/sqli-lab", methods=["GET"])
def sqli_lab():
    tables = []
    for t, cfg in CRUD_CONFIG.items():
        tables.append({
            "name": t,
            "title": cfg.get("title", t),
            "fields": allowed_fields_for_table(t)
        })
    return render_template("sqli_lab.html", site_cfg=CRUD_CONFIG, tables=tables)


@app.before_request
def guard_if_empty():
    allowed = {"/", "/setup", "/seed-initial", "/search"}
    if request.path.startswith("/static/"):
        return
    if not has_any_data() and request.path not in allowed:
        return redirect(url_for("setup_required"))


@app.route("/")
def index():
    counts = {}
    ready = has_any_data()
    for t in CRUD_CONFIG.keys():
        try:
            counts[t] = run_select(f"SELECT COUNT(*) FROM {t};")[0][0] if ready else 0
        except Exception:
            counts[t] = 0
    return render_template("index.html", site_cfg=CRUD_CONFIG, counts=counts, ready=ready)


@app.route("/setup")
def setup_required():
    return render_template("setup_required.html", site_cfg=CRUD_CONFIG)


@app.route("/seed-initial")
def seed_initial():
    if has_any_data():
        flash("Există deja date în sistem.", "info")
        return redirect(url_for("crud_list", table="Pacienti"))
    run_execute("INSERT INTO Pacienti (nume, cnp) VALUES (%s, %s);", ("Popescu Ion", "1234567890123"))
    flash("Pacient demo creat.", "success")
    return redirect(url_for("crud_list", table="Pacienti"))


@app.route("/crud/<table>")
def crud_list(table):
    cfg = ensure_table_allowed(table)
    cols, rows = fetch_list(table)
    return render_template("crud_list.html", site_cfg=CRUD_CONFIG, table=table, table_cfg=cfg, cols=cols, rows=rows)


@app.route("/crud/<table>/create", methods=["GET", "POST"])
def crud_create(table):
    cfg = ensure_table_allowed(table)
    fk_options = build_fk_options(cfg)
    if request.method == "POST":
        try:
            insert_record(table, request.form)
            flash("Înregistrare creată cu succes.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")
    return render_template("crud_form.html", site_cfg=CRUD_CONFIG, table=table, table_cfg=cfg, mode="create",
                           fields=cfg["create_fields"], values={}, fk_options=fk_options)


@app.route("/crud/<table>/edit/<int:rec_id>", methods=["GET", "POST"])
def crud_edit(table, rec_id):
    cfg = ensure_table_allowed(table)
    cols, row = fetch_by_id(table, rec_id)
    if not row:
        abort(404)
    values = dict(zip(cols, row))
    fk_options = build_fk_options(cfg)
    if request.method == "POST":
        try:
            update_record(table, rec_id, request.form)
            flash("Actualizat cu succes.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")
    return render_template("crud_form.html", site_cfg=CRUD_CONFIG, table=table, table_cfg=cfg, mode="edit",
                           fields=cfg["update_fields"], values=values, fk_options=fk_options, rec_id=rec_id)


@app.route("/crud/<table>/delete/<int:rec_id>", methods=["POST"])
def crud_delete(table, rec_id):
    ensure_table_allowed(table)
    try:
        delete_record_safe(table, rec_id)
        flash("Șters cu succes!", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("crud_list", table=table))


@app.route("/search", methods=["GET", "POST"])
def search():
    result = None
    if request.method == "POST":
        table = (request.form.get("table") or "").strip()
        field = (request.form.get("field") or "").strip()
        value = (request.form.get("value") or "").strip()
        try:
            ensure_table_allowed(table)
            exists = record_exists(table, field, value)
            result = {"ok": True, "exists": exists, "table": table, "field": field, "value": value}
        except Exception as e:
            result = {"ok": False, "error": str(e)}
    return render_template("search.html", site_cfg=CRUD_CONFIG, result=result)


if __name__ == "__main__":
    app.run(debug=True)