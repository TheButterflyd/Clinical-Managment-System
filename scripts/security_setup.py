import mariadb
import bcrypt
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Încărcăm variabilele din .env
load_dotenv()

# --- CONFIGURARE SECURITATE ---
# Asigură-te că ai ENCRYPTION_KEY în fișierul .env
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generăm o cheie dacă lipsește, dar trebuie salvată permanent!
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f" ATENȚIE: Salvează această cheie în .env: ENCRYPTION_KEY={ENCRYPTION_KEY}")

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

# --- CONFIGURARE DB ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "rootpass"),
    "database": os.getenv("DB_NAME", "clinica_medicala")
}

def get_connection():
    try:
        return mariadb.connect(**DB_CONFIG)
    except mariadb.Error as e:
        print(f" Eroare la conectare: {e}")
        exit(1)

def hash_password(plain: str) -> str:
    """Hășuire ireversibilă (Bcrypt) - DOAR pentru parole."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def encrypt_reversibil(plain_text: str) -> str:
    """Criptare reversibilă (Fernet/AES) - pentru Email."""
    if not plain_text: return None
    return cipher_suite.encrypt(plain_text.encode()).decode()

def secure_medici_emails():
    """Criptează email-urile medicilor folosind FERNET (Reversibil)."""
    conn = get_connection()
    cur = conn.cursor()
    print("\n🔐 Se criptează email-urile medicilor cu Fernet...")

    try:
        cur.execute("SELECT id_medic, email FROM Medici")
        rows = cur.fetchall()

        count = 0
        for id_m, email in rows:
            # Fernet generează șiruri care încep de obicei cu 'gAAAA'
            # Verificăm să nu fie deja criptat sau deja un hash bcrypt ($2)
            if email and not (str(email).startswith("gAAAA") or str(email).startswith("$2")):
                encrypted_email = encrypt_reversibil(str(email))
                cur.execute(
                    "UPDATE Medici SET email = %s WHERE id_medic = %s",
                    (encrypted_email, id_m)
                )
                count += 1
                print(f"🔒 Email criptat (Fernet) pentru Medic ID: {id_m}")

        conn.commit()
        print(f" Finalizat: {count} email-uri securizate reversibil.")
    except Exception as e:
        print(f" Eroare la Medici: {e}")
    finally:
        conn.close()

def secure_pacienti_passwords():
    """Hășuiește parolele pacienților folosind BCRYPT (Ireversibil)."""
    conn = get_connection()
    cur = conn.cursor()
    print("\n👥 Se securizează parolele pacienților...")

    try:
        cur.execute("SELECT id_pacient, password_hash FROM Pacienti")
        rows = cur.fetchall()

        count = 0
        for id_p, pwd in rows:
            if pwd and not str(pwd).startswith("$2b$"):
                hashed_pwd = hash_password(str(pwd))
                cur.execute(
                    "UPDATE Pacienti SET password_hash = %s WHERE id_pacient = %s",
                    (hashed_pwd, id_p)
                )
                count += 1
                print(f"🔑 Parolă hășuită pentru Pacient ID: {id_p}")

        conn.commit()
        print(f" Finalizat: {count} parole securizate.")
    except Exception as e:
        print(f" Eroare la Pacienți: {e}")
    finally:
        conn.close()

def main():
    print("=" * 55)
    print("   UPGRADE SECURITATE: FERNET (EMAIL) & BCRYPT (PAROLE)")
    print("=" * 55)

    secure_medici_emails()
    secure_pacienti_passwords()

    print("\n🎉 Procesare finalizată cu succes!")

if __name__ == "__main__":
    main()