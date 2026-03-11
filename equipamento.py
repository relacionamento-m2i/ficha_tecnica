import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Registro de Equipamentos", layout="wide")

# --- DADOS PADRÃO (Baseados na sua imagem) ---
def carregar_dados_padrao():
    return pd.DataFrame({
        "Nome do equipamento": [
            "BOMBA PNEUMÁTICA", "USG PHILLIPS CLEARVUE", "MONITOR MULTIPARAMÉTRICO",
            "MISTURADOR DE GASES", "APARELHO DE ENDOLASER PIOON", "VEINVIEWER",
            "LASER TRANSDÉRMICO (VYDENCE)", "RESFRIADOR DE PELE (SIBERIAN OU FREEDO)",
            "MISTURADOR DE GASES (ÓXIDO NITROSO)", "T SCULPTOR", "DINAMÔMETRO", "PTOLOMEU"
        ],
        "Data de Aquisição": [
            "01/01/2024", "01/01/2025", "06/01/2025", "06/01/2025", "06/01/2025", "06/01/2025",
            "01/01/2026", "01/01/2026", "01/01/2024", "11/01/2025", "", "12/01/2025"
        ],
        "Valor de aquisição (R$)": [
            5500.0, 100000.0, 5500.0, 15000.0, 98000.0, 60000.0, 
            230000.0, 25000.0, 15000.0, 80000.0, 0.0, 180000.0
        ],
        "Tempo de vida útil (anos)": [5, 10, 10, 5, 10, 10, 5, 5, 10, 10, 5, 5],
        "Capacidade aplicações/dia": [8.0, 8.0, 8.0, 8.0, 10.0, 8.0, 8.0, 8.0, 8.0, 8.0, 0.0, 8.0],
        "Aplicações (média diária)": [1.0, 8.0, 4.0, 4.0, 1.0, 8.0, 4.0, 4.0, 4.0, 0.2, 0.0, 0.2],
        "Custo anual de manutenção (R$)": [
            0.0, 1000.0, 0.0, 0.0, 5000.0, 0.0, 
            9000.0, 1000.0, 200.0, 2000.0, 0.0, 2000.0
        ],
        "Observações": ["", "", "", "", "", "", "", "", "", "", "", ""]
    })

# Inicializa o session_state se não existir
if "df_equipamentos" not in st.session_state:
    st.session_state["df_equipamentos"] = carregar_dados_padrao()

# --- BARRA LATERAL: SISTEMA DE SALVAR / CARREGAR ---
with st.sidebar:
    st.header("💾 Salvar / Carregar")
    st.write("Exporte seus dados para não perdê-os ao atualizar a página.")
    
    # 1. Carregar Dados
    arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"])
    if arquivo_upload is not None:
        try:
            dados_json = json.load(arquivo_upload)
            st.session_state["df_equipamentos"] = pd.DataFrame(dados_json)
            st.success("Dados carregados com sucesso!")
        except Exception as e:
            st.error("Erro ao ler o arquivo.")

    st.divider()

    # 2. Salvar Dados
    df_para_salvar = st.session_state["df_equipamentos"]
    json_string = df_para_salvar.to_json(orient="records", indent=4)
    
    st.download_button(
        label="📥 Baixar Tabela de Equipamentos",
        data=json_string,
        file_name="equipamentos_clinica.json",
        mime="application/json"
    )

# --- CABEÇALHO ---
st.title("Registro e Depreciação de Equipamentos")
st.markdown("""
Esta ferramenta permite calcular automaticamente o **Custo da Sessão de Depreciação** de cada equipamento. 
Edite as informações na tabela abaixo (você pode adicionar ou deletar linhas usando as opções da própria tabela).
""")

# Parâmetro de dias úteis para o cálculo final
dias_uteis = st.number_input("Dias úteis no mês (para cálculo do custo por sessão):", min_value=1, value=22, step=1)

# --- TABELA EDITÁVEL (Inputs) ---
st.subheader("1. Edição de Dados")

# st.data_editor permite que o usuário interaja com a tabela (adicione/remova linhas)
df_editado = st.data_editor(
    st.session_state["df_equipamentos"],
    num_rows="dynamic", # Permite adicionar novas linhas
    use_container_width=True,
    hide_index=True,
    key="editor_equipamentos"
)

# Atualiza a memória com as edições do usuário
st.session_state["df_equipamentos"] = df_editado.copy()

# --- LÓGICA DE CÁLCULO (Colunas Dinâmicas) ---
df_calculado = df_editado.copy()

# Tratamento para evitar divisão por zero ou dados nulos
df_calculado.fillna(0, inplace=True)

# 1. Montante Investido = Valor de Aquisição + (Vida útil * Custo anual de manutenção)
df_calculado["Montante Investido (R$)"] = df_calculado["Valor de aquisição (R$)"] + (df_calculado["Tempo de vida útil (anos)"] * df_calculado["Custo anual de manutenção (R$)"])

# 2. Depreciação Mensal = Montante Investido / (Vida útil * 12 meses)
df_calculado["Depreciação Mensal (R$)"] = df_calculado.apply(
    lambda row: row["Montante Investido (R$)"] / (row["Tempo de vida útil (anos)"] * 12) 
    if row["Tempo de vida útil (anos)"] > 0 else 0, 
    axis=1
)

# 3. Custo Seção de Depreciação = Depreciação Mensal / (Aplicações Diárias * Dias Úteis no mês)
df_calculado["Custo Seção (R$)"] = df_calculado.apply(
    lambda row: row["Depreciação Mensal (R$)"] / (row["Aplicações (média diária)"] * dias_uteis) 
    if row["Aplicações (média diária)"] > 0 else 0, 
    axis=1
)

st.divider()

# --- TABELA FINAL DE RESULTADOS ---
st.subheader("2. Tabela de Resultados Consolidados")
st.write("Os valores de Montante, Depreciação Mensal e Custo por Sessão são gerados automaticamente abaixo:")

# Selecionar e ordenar as colunas para exibição final
colunas_exibicao = [
    "Nome do equipamento",
    "Valor de aquisição (R$)",
    "Montante Investido (R$)",
    "Depreciação Mensal (R$)",
    "Custo Seção (R$)"
]

df_visualizacao = df_calculado[colunas_exibicao]

# Aplicando estilo de formatação contábil para a tabela final
estilo_resultados = df_visualizacao.style.format({
    "Valor de aquisição (R$)": "R$ {:,.2f}",
    "Montante Investido (R$)": "R$ {:,.2f}",
    "Depreciação Mensal (R$)": "R$ {:,.2f}",
    "Custo Seção (R$)": "R$ {:,.2f}"
})

st.dataframe(estilo_resultados, use_container_width=True, hide_index=True)

# Totalizadores Rápidos
total_investido = df_calculado["Montante Investido (R$)"].sum()
total_depreciacao_mensal = df_calculado["Depreciação Mensal (R$)"].sum()

st.markdown("### Resumo da Depreciação")
col1, col2 = st.columns(2)
col1.metric("Montante Total Investido/Projetado", f"R$ {total_investido:,.2f}")
col2.metric("Total Depreciação Mensal", f"R$ {total_depreciacao_mensal:,.2f}")