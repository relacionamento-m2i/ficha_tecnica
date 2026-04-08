import streamlit as st

# 1. Configuração inicial da página (A ÚNICA EM TODO O PROJETO)
st.set_page_config(page_title="Portal de Acesso", page_icon="🔒", layout="wide")

# ==========================================
# ESTILOS E CORES DA TELA DE LOGIN
# ==========================================
COR_CABECALHO = "#7030A0"
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F4F4F9; }}
    div[data-baseweb="input"] > div {{ background-color: #FFFFFF !important; border: 1px solid #888888 !important; border-radius: 8px !important; padding: 2px 8px; }}
    div[data-baseweb="input"] > div:focus-within {{ border-color: {COR_CABECALHO} !important; box-shadow: 0 0 0 2px {COR_CABECALHO} !important; }}
    div[data-testid="stFormSubmitButton"] > button {{ background-color: {COR_CABECALHO} !important; color: white !important; border-radius: 8px !important; font-weight: bold !important; border: none !important; padding: 10px !important; }}
    div[data-testid="stFormSubmitButton"] > button:hover {{ background-color: #5a2680 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERIFICAÇÃO DE SEGURANÇA
# ==========================================
try:
    SENHAS = st.secrets["senhas"]
    ARQUIVOS = st.secrets["arquivos"]
except FileNotFoundError:
    st.error("⚠️ Arquivo secrets.toml não encontrado. Certifique-se de que ele está na pasta '.streamlit/'.")
    st.stop()
except KeyError as e:
    st.error(f"⚠️ A seção {e} não foi encontrada dentro do seu secrets.toml.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Erro ao ler as configurações de segurança: {e}")
    st.stop()

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

# ==========================================
# 3. TELA DE LOGIN (Mostra apenas se não estiver logado)
# ==========================================
if st.session_state["usuario_logado"] is None:
    st.write("<br><br><br>", unsafe_allow_html=True)
    col_esq, col_centro, col_dir = st.columns([1.5, 1.2, 1.5])
    
    with col_centro:
        st.markdown(f"""
        <div style="background-color: {COR_CABECALHO}; padding: 25px; border-radius: 10px 10px 0 0; text-align: center;">
            <h2 style="margin: 0; color: white;">SISTEMA DE PRECIFICAÇÃO</h2>
            <p style="color: #E6E0EC; margin-top: 5px; margin-bottom: 0;">Faça login para acessar seu painel</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_login"):
            st.write("")
            usuario_input = st.text_input("👤 Usuário")
            senha_input = st.text_input("🔑 Senha", type="password")
            st.write("")
            btn_entrar = st.form_submit_button("ENTRAR", use_container_width=True)
            
            if btn_entrar:
                # Verifica se o usuário existe e se a senha confere
                if usuario_input in SENHAS and str(SENHAS[usuario_input]) == str(senha_input):
                    st.session_state["usuario_logado"] = usuario_input
                    st.rerun() 
                else:
                    st.error("❌ Usuário ou senha incorretos.")
    st.stop()

# ==============================================================
# 4. ROTEAMENTO DINÂMICO (Busca a página do cliente)
# ==============================================================
usuario_atual = st.session_state["usuario_logado"]

# Verifica se o arquivo configurado no toml existe nas configurações
if usuario_atual not in ARQUIVOS:
    st.error(f"⚠️ Nenhum painel configurado para o usuário: '{usuario_atual}' dentro de [arquivos] no secrets.toml.")
    st.stop()

caminho_do_arquivo = ARQUIVOS[usuario_atual]

# Botão de Logout fixo na lateral
with st.sidebar:
    st.markdown(f"👤 Logado como: **{usuario_atual}**")
    if st.button("🚪 Sair (Logout)", use_container_width=True):
        st.session_state["usuario_logado"] = None
        st.rerun()

# Roteia para o arquivo do cliente e roda
pagina_exclusiva = st.Page(caminho_do_arquivo, title=f"Painel - {usuario_atual}", icon="📊")
pg = st.navigation([pagina_exclusiva])
pg.run()