import sqlite3
import csv 

# Define o nome do nosso arquivo de banco de dados
DB_NAME = "trades.db"

def inicializar_banco():
    """
    Cria o banco de dados e a tabela 'trades' se eles não existirem.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            ativo TEXT NOT NULL,
            tipo_operacao TEXT,
            resultado_tipo TEXT NOT NULL,
            resultado_financeiro REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def salvar_trade(trade_data):
    """
    Salva um único registro de trade no banco de dados SQLite.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (data, horario, ativo, tipo_operacao, resultado_tipo, resultado_financeiro)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        trade_data['data'],
        trade_data['horario'],
        trade_data['ativo'],
        trade_data['tipo_operacao'],
        trade_data['resultado_tipo'],
        float(trade_data['resultado_financeiro'])
    ))
    conn.commit()
    conn.close()
    print("Trade salvo com sucesso no banco de dados.")

def carregar_trades(filtro_ativo=None, data_inicio=None, data_fim=None):
    """
    Carrega os trades do banco de dados, com filtros opcionais.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Construção da query dinâmica
    base_query = "SELECT * FROM trades"
    conditions = []
    params = []

    if filtro_ativo:
        conditions.append("ativo = ?")
        params.append(filtro_ativo.upper())

    if data_inicio:
        conditions.append("data >= ?")
        params.append(data_inicio)

    if data_fim:
        conditions.append("data <= ?")
        params.append(data_fim)

    # Se houver alguma condição, monta a cláusula WHERE
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY data, horario"

    cursor.execute(base_query, params)

    trades = cursor.fetchall()
    conn.close()

    return [dict(trade) for trade in trades]

def migrar_do_csv():
    """
    Função de uso único para migrar dados do trades.csv para o trades.db.
    """
    print("Iniciando migração do CSV para o banco de dados...")
    try:
        with open('trades.csv', mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                salvar_trade(row) # Reutiliza a nova função de salvar
        print("Migração concluída com sucesso!")
    except FileNotFoundError:
        print("Arquivo trades.csv não encontrado. Nenhuma migração necessária.")
    except Exception as e:
        print(f"Ocorreu um erro durante a migração: {e}")
        
def deletar_trade(trade_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM trades WHERE id = ?", (trade_id))
    
    conn.commit()
    conn.close()
    print(f"Trade com ID {trade_id} deletado com sucesso.")