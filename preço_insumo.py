import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Lista de Insumos e Materiais", layout="wide")

# --- DADOS PADRÃO (Baseados na sua imagem) ---
def carregar_dados_padrao():
    return pd.DataFrame({
        "Material": [
            "ADRENALINA", "ÁGUA OXIGENADA - ( mL)", "ÁGUA OXIGENADA - ( mL).",
            "AGULHA 0,40x12", "AGULHA 13x0,3", "AGULHA 27 G 1/2", "AGULHA 30x0,8",
            "AGULHA 40x12", "AGULHA ASPIRAÇÃO", "ÁLCOOL - (mL )", "ÁLCOOL. - (mL )",
            "ÁLCOOL À 70%", "ATIVO (mL)", "BRINDE", "CANETA BRANCA DE MARCAÇÃO",
            "CAPA PARA USG", "CARTUCHO DA PONTEIRA", "CLOREXIDINA ALCÓOLICA (mL)",
            "EQUIPO", "ESTERILIZAÇÃO (KIT DE ENDOLASER E MICROPORE)"
        ],
        "qt": [1.0] * 20, # Inicia tudo com quantidade 1
        "valor": [
            1.30, 0.008, 0.04, 0.56, 0.10, 2.50, 0.05, 0.20, 0.35, 0.01,
            0.05, 0.008, 16.00, 50.00, 1.00, 3.00, 200.00, 0.02, 1.00, 15.00
        ]
    })

# Inicializa o session_state se não existir
if "df_insumos" not in st.session_state:
    st.session_state["df_insumos"] = carregar_dados_padrao()

# --- BARRA LATERAL: SISTEMA DE SALVAR / CARREGAR ---
with st.sidebar:
    st.header("💾 Salvar / Carregar")
    st.write("Exporte sua lista de insumos para não perdê-la ao atualizar a página.")
    
    # 1. Carregar Dados
    arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"])
    if arquivo_upload is not None:
        try:
            dados_json = json.load(arquivo_upload)
            st.session_state["df_insumos"] = pd.DataFrame(dados_json)
            st.success("Lista de Insumos carregada com sucesso!")
        except Exception as e:
            st.error("Erro ao ler o arquivo.")

    st.divider()

    # 2. Salvar Dados
    df_para_salvar = st.session_state["df_insumos"]
    json_string = df_para_salvar.to_json(orient="records", indent=4)
    
    st.download_button(
        label="📥 Baixar Lista de Insumos",
        data=json_string,
        file_name="lista_insumos_clinica.json",
        mime="application/json"
    )

# --- CABEÇALHO ---
# Reproduzindo o título em roxo da sua imagem
st.markdown("""
<h2 style='color: #6A329F; font-family: sans-serif; font-weight: normal;'>LISTA DE INSUMOS E MATERIAIS</h2>
<p>Edite os nomes, quantidades (qt) e os valores totais. O <b>valor unitário</b> será calculado e corrigido automaticamente sem erros.</p>
""", unsafe_allow_html=True)

# --- PREPARAÇÃO DOS DADOS PARA A TABELA ---
df_atual = st.session_state["df_insumos"].copy()

# Prevenindo divisão por zero caso o usuário digite 0 na quantidade
df_atual["qt"] = df_atual["qt"].apply(lambda x: x if x > 0 else 1.0) 

# Calcula o valor unitário (corrigindo o #ERROR! da planilha original)
df_atual["valor unitário"] = df_atual["valor"] / df_atual["qt"]

# --- TABELA INTERATIVA ---
df_editado = st.data_editor(
    df_atual,
    num_rows="dynamic", # Permite adicionar/deletar linhas
    use_container_width=True,
    hide_index=True,
    column_config={
        "Material": st.column_config.TextColumn(
            "Material",
            width="large"
        ),
        "qt": st.column_config.NumberColumn(
            "qt",
            min_value=0.01,
            step=1.0,
            help="Quantidade do pacote ou volume (ex: 1, 100, 500)"
        ),
        "valor": st.column_config.NumberColumn(
            "valor (R$)",
            min_value=0.0,
            step=0.5,
            format="R$ %.3f", # Permite mostrar 3 casas decimais (ex: 0.008)
            help="Valor total pago na quantidade informada"
        ),
        "valor unitário": st.column_config.NumberColumn(
            "valor unitário (R$)",
            disabled=True, # Bloqueia edição (é calculado automaticamente)
            format="R$ %.3f",
            help="Calculado automaticamente: valor / qt"
        )
    }
)

# --- ATUALIZAÇÃO DA MEMÓRIA ---
# Salva apenas as colunas base (sem a calculada) para a memória, mantendo a integridade dos dados
st.session_state["df_insumos"] = df_editado[["Material", "qt", "valor"]].copy()

st.divider()

# Resumo rápido da quantidade de itens cadastrados
st.caption(f"Total de itens cadastrados no banco de dados: **{len(df_editado)} insumos**.")