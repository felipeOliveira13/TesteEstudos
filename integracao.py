import streamlit as st
import gspread
import pandas as pd

# --- CONSTANTES GERAIS ---
ROW_HEIGHT = 35 
HEADER_HEIGHT = 35


# 1. Função de Injeção de CSS (mantida sem alteração)
def inject_custom_css():
    st.markdown(
        """
        <style>
        h1 {
            text-align: center;
        }
        div[data-testid="stCaptionContainer"] {
            text-align: center;
        }
        div.stButton > button:first-child {
            white-space: nowrap; 
        }
        .block-container {
            padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
inject_custom_css()


# --- DADOS DA PLANILHA ---
SHEET_ID = "1fa4HLFfjIFKHjHBuxW_ymHkahVPzeoB_XlHNJMaNCg8"
SHEET_NAME = "Chevrolet Preços"

st.title("🚗 Tabela de Preços Chevrolet (Google Sheets)")
st.caption("Dados carregados diretamente do Google Sheets usando st.secrets.")


# Função de carregamento com cache (mantida sem alteração)
@st.cache_data(ttl=600)  
def load_data_from_sheet():
    try:
        credentials = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(credentials)
        spreadsheet = gc.open_by_key(SHEET_ID)
        worksheet = spreadsheet.worksheet(SHEET_NAME)
        df = pd.DataFrame(worksheet.get_all_records())
        
        # 💡 Dica: Certifique-se de que a coluna 'Ano' é um número inteiro (int)
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(0).astype(int)
        
        return df
    
    except KeyError:
        st.error("❌ Erro de Configuração: O segredo 'gcp_service_account' não foi encontrado.")
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"❌ Erro ao acessar o Google Sheets: {e}")
        st.warning("Verifique se o email de serviço foi adicionado como 'Leitor' na planilha.")
        return pd.DataFrame()


# --- EXECUÇÃO DO APLICATIVO ---
df = load_data_from_sheet()

if not df.empty:
    
    # =============================================================
    # 2. NOVIDADE: SEÇÃO DE FILTROS INTERATIVOS
    # =============================================================
    st.markdown("---")
    st.subheader("Filtros de Dados")
    
    # Cria duas colunas para os filtros ficarem lado a lado
    filter_col1, filter_col2 = st.columns(2)
    
    # --- FILTRO 1: MODELO ---
    with filter_col1:
        # Pega todos os modelos únicos e remove valores vazios (se houver)
        all_models = sorted(df['Modelo'].unique())
        
        # O multiselect permite selecionar vários modelos
        selected_models = st.multiselect(
            "Selecione o(s) Modelo(s) de Carro:",
            options=all_models,
            default=all_models # Padrão: todos selecionados
        )

    # --- FILTRO 2: ANO ---
    with filter_col2:
        # Pega todos os anos únicos e ordena
        all_years = sorted(df['Ano'].unique())
        
        # O multiselect permite selecionar vários anos
        selected_years = st.multiselect(
            "Selecione o(s) Ano(s) de Fabricação:",
            options=all_years,
            default=all_years # Padrão: todos selecionados
        )

    # --- 3. APLICAÇÃO DOS FILTROS ---
    df_filtered = df[
        (df['Modelo'].isin(selected_models)) &
        (df['Ano'].isin(selected_years))
    ]
    
    # =============================================================
    # FIM DA SEÇÃO DE FILTROS
    # =============================================================

    st.markdown("---")
    
    # 4. EXIBIÇÃO DO DATAFRAME FILTRADO
    
    # Exibe o subheader com a contagem de linhas filtradas
    st.subheader(f"Dados da Aba: {SHEET_NAME} (Linhas exibidas: {len(df_filtered)})")
    
    # Recalcula a altura baseada no novo número de linhas (df_filtered)
    calculated_height = (len(df_filtered) * ROW_HEIGHT) + HEADER_HEIGHT

    st.dataframe(df_filtered, 
                 use_container_width=True, 
                 hide_index=True, 
                 height=calculated_height) 
    
    # Linha divisória e Botão de Recarregar (mantidos)
    st.markdown("---") 
    col_left, col_center, col_right = st.columns([3, 4, 3])
    
    with col_center:
        if st.button(
            "🔄 Recarregar Dados", 
            help="Clique para buscar a versão mais recente dos dados da planilha."
        ):
            load_data_from_sheet.clear()
            st.rerun() 
            
else:
    st.warning("Não foi possível carregar os dados. Verifique os logs de erro acima.")