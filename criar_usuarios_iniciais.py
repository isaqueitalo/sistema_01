# criar_usuarios_iniciais.py
from APP.core.database import conectar
from APP.core.utils import hash_password

usuarios = [
    ("admin_master", "Admin_master@123", "admin_master"),
    ("admin", "Admin@123", "admin"),
    ("vendedor1", "Vendas@123", "vendedor"),
    
]

conn = conectar()
cur = conn.cursor()

for username, senha, role in usuarios:
    cur.execute("SELECT id FROM usuarios WHERE username=?", (username,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(senha), role),
        )
        print(f"✅ Usuário criado: {username} ({role}) — Senha: {senha}")
    else:
        print(f"ℹ️ Usuário '{username}' já existe — ignorado.")

conn.commit()
conn.close()
print("💾 Criação inicial concluída.")
