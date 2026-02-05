import sqlite3

conn = sqlite3.connect("invitados.db")

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS guests 
(id INTEGER PRIMARY KEY AUTOINCREMENT, 
nombre_completo TEXT NOT NULL,
telefono TEXT NOT NULL, 
tipo TEXT NOT NULL DEFAULT 'JOVEN' CHECK (tipo IN ('JOVEN', 'ADULTO')), 
genero TEXT NOT NULL DEFAULT 'NO_ESPECIFICADO' CHECK (genero IN ('MASC', 'FEM', 'NO_ESPECIFICADO')),
estado TEXT NOT NULL DEFAULT 'INVITADO' CHECK (estado IN ('INVITADO', 'PRECONFIRMADO', 'CONFIRMADO','NO_ASISTE')), 
token TEXT NOT NULL UNIQUE, token_expires_at DATETIME NOT NULL, 
created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP )
''')

conn.commit()