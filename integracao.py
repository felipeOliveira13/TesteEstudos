import streamlit as st
import gspread
import pandas as pd

# 1. NOVO: Função de Injeção de CSS
def inject_custom_css():
    st.markdown(
        """
        <style>
        /* Centraliza o título principal H1 */
        h1 {
            text-align: center;
        }

        /* REMOVEMOS AQUI O CÓDIGO CSS QUE FORÇAVA A LARGURA DO BOTÃO, 
           permitindo que o Streamlit defina a largura natural para o texto. */
        
        /* Ajusta o padding para que o conteúdo não fique colado no topo (opcional) */
        .block-container {
            padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
# Chamada do CSS
inject_custom_css()
# --- FIM DO CSS ---


# --- DADOS DA PLANILHA ---
SHEET_ID = "1fa4HLFfjIFKHjHBuxW_ymHkahVPzeoB_XlHNJMaNCg8"
SHEET_NAME = "Chevrolet Preços"

# Título do Aplicativo Streamlit (centralizado via CSS)
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
    st.subheader(f"Dados da Aba: {SHEET_NAME} (Total de linhas: {len(df)})")
    
    # Exibe o DataFrame com altura fixa
    st.dataframe(df, height=400, use_container_width=True) 
    
    # Linha divisória
    st.markdown("---") 
    
    # NOVO: USANDO COLUNAS PARA CENTRALIZAR O BOTÃO
    # [3, 2, 3] garante que o espaço vazio na esquerda (3) e na direita (3)
    # seja igual, centralizando o espaço do botão (2)
    col_left, col_center, col_right = st.columns([3, 2, 3])
    
    with col_center:
        # O Streamlit agora ajustará a largura automaticamente para o texto
        if st.button(
            "🔄 Recarregar Dados", 
            help="Clique para buscar a versão mais recente dos dados da planilha."
        ):
            load_data_from_sheet.clear()
            st.rerun() 
            
else:
    st.warning("Não foi possível carregar os dados. Verifique os logs de erro acima.")