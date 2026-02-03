from flask import Flask, jsonify, request
import os
import sqlite3
from dotenv import load_dotenv
from pathlib import Path
import secrets
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

event_date_str = os.getenv("EVENT_DATE")
event_date = datetime.strptime(event_date_str, "%Y-%m-%d %H:%M:%S")

DB_PATH = os.getenv("GUESTS_DB_PATH")

def get_conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def check_health():
    return jsonify({"message":"Ok"}), 200


@app.route("/admin/guests", methods=["POST",])
def create_guest():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error":"formato invalido"}), 400

    nombre_completo = data.get("nombre_completo")
    telefono = data.get("telefono")
    tipo = data.get("tipo")
    genero = data.get("genero")

    # Verificar campos obligatorios
    campos_obligatorios = ["nombre_completo", "telefono", "tipo", "genero"]

    for campo in campos_obligatorios:
        if campo not in data or not data[campo]:
            return jsonify({"error": f"campo {campo} es obligatorio"}), 400
        
    # Normalizar valores (solo despues de validar)
    nombre_completo = data["nombre_completo"].strip().lower()
    telefono = data["telefono"].strip()
    tipo = data["tipo"].strip().upper()
    genero = data["genero"].strip().upper()

    # Validar valores permitidos
    if tipo not in {"JOVEN", "ADULTO"}:
        return jsonify({"error": "Tipo inválido. Use JOVEN o ADULTO"}), 400
    
    if genero not in {"MASC", "FEM"}:
        return jsonify({"error": "Género inválido. Use MASC o FEM"}), 400

    # Calcular expiracion del token (evento + 1 dia)
    expires_at = event_date + timedelta(days=1)
    token_expires_at = expires_at.strftime("%Y-%m-%d %H:%M:%S") #Convertir de nuevo a string ya que SQLite guarda fechas como texto
    
    # Generar token
    token = secrets.token_urlsafe(16)

    # Insertar en DB
    with get_conn() as conn:

        # Verificar duplicado por telefono
        cur = conn.execute("""SELECT id from guests WHERE telefono = ?
        """, (telefono,))
        row = cur.fetchone()
        # si telefono ya existe -> 409
        if row:
            return jsonify({"error":"el invitado ya existe"}), 409 # Conflict

        cur = conn.execute(
            '''
            INSERT INTO guests 
            (nombre_completo, telefono, tipo, genero, estado ,token, token_expires_at) 
            VALUES (?,?,?,?, 'INVITADO',?,?)
            ''', 
            (nombre_completo, telefono, tipo, genero, token, token_expires_at)
            )
        conn.commit()

    # Respuesta de exito
    return jsonify({"message":"Invitado creado correctamente", "token": token}), 201

@app.route("/admin/guests", methods=["GET"])
def get_guests():

    args =  request.args

    tipo = args.get("tipo")
    genero = args.get("genero")

    query = "SELECT * FROM guests WHERE 1=1"
    condiciones = []
    parametros = []

    if tipo:
        tipo = tipo.strip().upper()
        condiciones.append("tipo = ?")
        parametros.append(tipo)

    if genero:
        genero = genero.strip().upper()
        condiciones.append("genero = ?")
        parametros.append(genero)

    if condiciones:
        query += " AND " + " AND ".join(condiciones)
    
    query += " ORDER BY id DESC"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row       # row_factory permite convertir filas a dict facilmente.
        cur  = conn.execute(query, parametros)
        rows = cur.fetchall()

    # Serializamos filas a lista de dicts apta para jsonify
    response = []
    for r in rows:
        response.append(dict(r))
    
    return jsonify({"data": response}), 200

if __name__ == "__main__":
    app.run(debug=True, port=6789)