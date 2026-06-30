import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'db', 'rpg_sistema.db')

def get_connection():
    if not os.path.exists(os.path.join(BASE_DIR, '..', 'db')):
        os.makedirs(os.path.join(BASE_DIR, '..', 'db'))
    # Ativa o suporte a chaves estrangeiras no SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = 1") 
    return conn

def inicializar_banco():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabela Ficha (Já existente)
    cursor.execute('''CREATE TABLE IF NOT EXISTS ficha (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_personagem TEXT,
                    nome_jogador TEXT,
                    vida_maxima INTEGER,
                    vida_atual INTEGER,
                    forca INTEGER,
                    defesa INTEGER)''')
                    
    # 2. Tabela Equipamento (NOVA - Para a Coluna 2 da Calculadora)
    cursor.execute('''CREATE TABLE IF NOT EXISTS equipamento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ficha_id INTEGER,
                    nome_equipamento TEXT,
                    bonus_ataque INTEGER,
                    bonus_defesa INTEGER,
                    FOREIGN KEY(ficha_id) REFERENCES ficha(id) ON DELETE CASCADE)''')
                    
    conn.commit()
    conn.close()