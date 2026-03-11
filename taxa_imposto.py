import streamlit as st
import pandas as pd
import json

# Configuração da página
st.set_page_config(page_title="Impostos e Taxas", layout="centered")

# --- INICIALIZAÇÃO DOS DADOS NA MEMÓRIA ---
if "aliquota_imposto" not in st.session_state:
    st.session_state["aliquota_imposto"] = 12.00

if "df_taxas" not in st.session_state:
    st.session_state["df_taxas"] = pd.DataFrame({
        "Taxas aplicadas": [
            "PIX Pessoa Física",
            "PIX Pessoa Jurídica",
            "Débito",
            "Crédito à vista",
            "Parcelado de 2x a 6x"
        ],
        "Sobre o (%)": [0.0, 0.0, 0.8, 0.9, 2.5]
    })

# --- BARRA LATERAL: SALVAR E CARREGAR ---
with st.sidebar:
    st.header("💾 Salvar / Carregar")
    
    # 1. Carregar Dados
    arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"])
    if arquivo_upload is not None:
        try:
            dados_json = json.load(arquivo_upload)
            # Restaura a alíquota
            st.session_state["aliquota_imposto"] = float(dados_json.get("aliquota_imposto", 12.0))
            # Restaura a tabela
            st.session_state["df_taxas"] = pd.DataFrame(dados_json.get("df_taxas", []))
            st.success("Dados carregados com sucesso!")
        except Exception as e:
            st.error("Erro ao ler o arquivo.")

    st.divider()

    # 2. Salvar Dados
    dados_para_salvar = {
        "aliquota_imposto": st.session_state["aliquota_imposto"],
        "df_taxas": st.session_state["df_taxas"].to_dict(orient="records")
    }
    json_string = json.dumps(dados_para_salvar, indent=4)
    
    st.download_button(
        label="📥 Baixar Taxas Atuais",
        data=json_string,
        file_name="impostos_e_taxas.json",
        mime="application/json"
    )

# --- LAYOUT PRINCIPAL ---

# Título com o estilo da planilha (fundo vermelho escuro, texto branco)
st.markdown("""
<div style="background-color: #A30000; padding: 10px; border-radius: 5px; color: white;">
    <h3 style="margin: 0; color: white;">3. Impostos e taxas</h3>
</div>
<br>
""", unsafe_allow_html=True)

# 1. Alíquota de imposto
st.markdown("#### 1. Alíquota de imposto da empresa (%)")
col1, col2 = st.columns([1, 3])
with col1:
    aliquota = st.number_input(
        "Alíquota (%)", 
        value=st.session_state["aliquota_imposto"], 
        min_value=0.0, 
        step=0.5,
        format="%.2f",
        label_visibility="collapsed"
    )
    # Atualiza a memória se o usuário mudar o valor
    st.session_state["aliquota_imposto"] = aliquota

st.divider()

# 2. Tarifas Bancárias (Tabela Editável)
st.markdown("#### 2. Tarifas bancárias para vendas")

# Tabela editável com formatação para mostrar o %
df_editado = st.data_editor(
    st.session_state["df_taxas"],
    hide_index=True,
    use_container_width=True,
    column_config={
        "Taxas aplicadas": st.column_config.TextColumn(
            "Taxas aplicadas",
            disabled=True, # Impede o usuário de mudar o nome da taxa (ex: PIX)
            width="large"
        ),
        "Sobre o (%)": st.column_config.NumberColumn(
            "Sobre o (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            format="%.2f %%" # Formata automaticamente com a casa decimal e o símbolo %
        )
    }
)

# Salva as alterações feitas na tabela direto na memória
st.session_state["df_taxas"] = df_editado.copy()