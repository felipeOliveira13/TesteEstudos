import os
import sys
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# --- CAMINHO ABSOLUTO DO ARQUIVO JSON (INSERIDO POR VOCÊ) ---
CREDENTIALS_PATH = r"C:\Users\User\Desktop\integraçao sheets\integracaoSheets\credentials.json"

# --- DADOS DA PLANILHA ---
SHEET_ID = "1fa4HLFfjIFKHjHBuxW_ymHkahVPzeoB_XlHNJMaNCg8"
SHEET_NAME = "Chevrolet Preços"

# 1) Verifica se o arquivo existe
if not os.path.exists(CREDENTIALS_PATH):
    print("❌ Arquivo de credenciais NÃO encontrado!")
    print("Caminho informado:", CREDENTIALS_PATH)
    sys.exit(1)

# 2) Verifica se dá para abrir
try:
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        _ = f.read(50)
except Exception as e:
    print("❌ Não foi possível abrir o arquivo:", e)
    sys.exit(1)

# 3) Autenticação com Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    print("✔ Autenticação OK")
except Exception as e:
    print("❌ Erro na autenticação:", e)
    sys.exit(1)

# 4) Abrir planilha e aba
try:
    spreadsheet = client.open_by_key(SHEET_ID)
    worksheet = spreadsheet.worksheet(SHEET_NAME)
    print("✔ Aba encontrada:", SHEET_NAME)
except Exception as e:
    print("❌ ERRO ao abrir planilha/aba:", e)
    print("\nVerifique:")
    print("  • A planilha foi compartilhada com o 'client_email' do arquivo JSON.")
    print("  • O nome da aba está exatamente igual.")
    sys.exit(1)

# 5) Ler dados da aba
try:
    df = pd.DataFrame(worksheet.get_all_records())
    print("✔ Dados carregados! Total de linhas:", len(df))
    print(df.head())
except Exception as e:
    print("❌ ERRO ao ler dados:", e)
    sys.exit(1)
