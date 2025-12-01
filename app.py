import streamlit as st
import pandas as pd
import gspread
import json

# Define o título da página e o layout
st.set_page_config(layout="wide", page_title="Dashboard Google Sheets")

st.title("📊 Visualizador de Dados do Google Sheets")
st.markdown("---")

# ==============================================================================
# FUNÇÃO DE CONEXÃO E CARREGAMENTO DE DADOS (USANDO CACHE)
# ==============================================================================

# O cache (@st.cache_data) garante que os dados só serão recarregados
# a cada 2 horas (ttl="2h"), a menos que as credenciais mudem.
@st.cache_data(ttl="2h")
def load_data_from_google_sheets():
    """
    Conecta ao Google Sheets usando as credenciais do Streamlit Secrets, 
    carrega os dados da primeira aba e retorna um DataFrame.
    """
    try:
        # 1. VERIFICAÇÃO DE CREDENCIAIS
        if "gcp_service_account" not in st.secrets:
            st.error("ERRO: Credenciais 'gcp_service_account' não encontradas. Por favor, configure o secrets.toml no Streamlit Cloud.")
            st.stop()
        
        # O Streamlit lê o bloco TOML como um dicionário Python
        credentials_info = st.secrets["gcp_service_account"]

        # 2. TRATAMENTO DA CHAVE PRIVADA
        # Esta linha é crítica: ela substitui '\n' literais por quebras de linha reais
        # para que o gspread possa ler a chave de segurança corretamente.
        if isinstance(credentials_info, dict) and 'private_key' in credentials_info:
             credentials_info['private_key'] = credentials_info['private_key'].replace('\\n', '\n')
        
        # Conecta ao Google usando as credenciais
        gc = gspread.service_account_from_dict(credentials_info)

        # 3. CONEXÃO COM A PLANILHA
        # ID da sua planilha: 1fa4HLFfjIFKHjHBuxW_ymK...
        spreadsheet_id = "1fa4HLFfjIFKHjHBuxW_ymK" 
        
        # Abre a planilha pelo ID
        sh = gc.open_by_key(spreadsheet_id)

        # Seleciona a primeira aba (worksheet).
        worksheet = sh.worksheet(sh.worksheets()[0].title) 

        # 4. LEITURA DOS DADOS
        data = worksheet.get_all_values()

        # Converte para DataFrame: primeira linha como colunas, resto como dados
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Tenta converter todas as colunas para tipos numéricos
        df = df.apply(pd.to_numeric, errors='ignore')

        return df

    except Exception as e:
        # Exibe o erro de forma clara no Streamlit
        st.error(f"Erro ao carregar dados do Google Sheets. Verifique o ID da planilha, o compartilhamento e as credenciais. Detalhes: {e}")
        return pd.DataFrame() 

# ==============================================================================
# EXIBIÇÃO NO STREAMLIT
# ==============================================================================

df = load_data_from_google_sheets()

if not df.empty:
    st.success("Dados carregados com sucesso!")
    
    col1, col2 = st.columns(2)
    col1.metric("Total de Registros", len(df))
    col2.metric("Total de Colunas", len(df.columns))
    
    st.subheader("Visualização dos Dados (Primeiras 10 linhas)")
    st.dataframe(df.head(10), use_container_width=True)
    
else:
    st.warning("Falha ao carregar dados. Verifique o console para mais detalhes do erro.")