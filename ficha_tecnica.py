import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Ficha Técnica de Serviços", layout="wide")

# --- CORES ESTILO PLANILHA ---
COR_CABECALHO = "#7030A0" # Roxo escuro
COR_FUNDO_CLARO = "#E6E0EC" # Roxo bem clarinho
COR_TEXTO_BRANCO = "#FFFFFF"

# --- INICIALIZAÇÃO DA MEMÓRIA (SESSION STATE) ---
def inicializar_estado(chave, valor_padrao):
    if chave not in st.session_state:
        st.session_state[chave] = valor_padrao

inicializar_estado("indireto", "Sim")
inicializar_estado("valor_hora", 60.12) # 60.12 * (50/60) = 50.10 (Para bater com sua imagem)
inicializar_estado("nome_servico", "BOMBA PNEUMÁTICA | Sessão")
inicializar_estado("tempo_min", 50)
inicializar_estado("custo_aluguel", 0.0)
inicializar_estado("repasse_fixo", 0.0)

# Taxas
inicializar_estado("taxa_comissao", 5.0)
inicializar_estado("taxa_cartao", 3.0)
inicializar_estado("taxa_imposto", 14.8)
inicializar_estado("taxa_repasse_liq", 0.0)
inicializar_estado("taxa_lucro", 0.0)

# Preços
inicializar_estado("preco_mercado", 0.0)
inicializar_estado("preco_escolhido", 150.0)

# Tabelas Internas
if "df_maquinas_ficha" not in st.session_state:
    st.session_state["df_maquinas_ficha"] = pd.DataFrame({
        "Máquina/Equipamento": ["BOMBA PNEUMÁTICA"],
        "Custo da Máquina (R$)": [4.17]
    })

if "df_insumos_ficha" not in st.session_state:
    st.session_state["df_insumos_ficha"] = pd.DataFrame({
        "Insumo/Material": [""],
        "QT": [0.0],
        "Preço (R$)": [0.0]
    })

# --- BARRA LATERAL: SISTEMA DE SALVAR / CARREGAR ---
with st.sidebar:
    st.header("💾 Salvar / Carregar Ficha")
    
    arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"])
    if arquivo_upload is not None:
        try:
            dados = json.load(arquivo_upload)
            for k, v in dados.items():
                if k in ["df_maquinas_ficha", "df_insumos_ficha"]:
                    st.session_state[k] = pd.DataFrame(v)
                else:
                    st.session_state[k] = v
            st.success("Ficha carregada com sucesso!")
        except Exception:
            st.error("Erro ao ler o arquivo.")

    st.divider()

    dados_salvar = {k: v.to_dict(orient="records") if isinstance(v, pd.DataFrame) else v for k, v in st.session_state.items()}
    st.download_button(
        label="📥 Baixar Ficha Técnica",
        data=json.dumps(dados_salvar, indent=4),
        file_name=f"ficha_{st.session_state['nome_servico'].replace(' ', '_')}.json",
        mime="application/json"
    )

# --- CABEÇALHO ---
st.markdown(f"""
<div style="background-color: {COR_CABECALHO}; padding: 10px; text-align: center;">
    <h3 style="margin: 0; color: {COR_TEXTO_BRANCO};">CÁLCULO DE CUSTOS DOS SERVIÇOS</h3>
</div>
""", unsafe_allow_html=True)
st.write("")

# --- 1. SETUP INICIAL ---
col1, col2 = st.columns([1, 1])
with col1:
    indireto = st.selectbox(
        "Com Custo Indireto (hora clínica)?", 
        ["Sim", "Não"], 
        index=0 if st.session_state["indireto"] == "Sim" else 1,
        key="indireto"
    )
with col2:
    if indireto == "Sim":
        valor_hora = st.number_input("Valor da Hora Clínica (R$)", value=st.session_state["valor_hora"], step=5.0, key="valor_hora")
        st.caption("Ao optar por SIM, o custo da hora clínica é inserido no custo dos serviços.")

st.markdown(f"""
<div style="background-color: {COR_FUNDO_CLARO}; padding: 5px;">
    <b>FICHA TÉCNICA DE SERVIÇOS DE SAÚDE</b>
</div>
""", unsafe_allow_html=True)

# --- 2. CUSTOS DIRETOS (A FICHA) ---
nome_servico = st.text_input("1. Nome do SERVIÇO:", value=st.session_state["nome_servico"], key="nome_servico")

col_esq, col_dir = st.columns([2, 1])

with col_esq:
    tempo_min = st.number_input("2. TEMPO de execução (Minutos):", value=st.session_state["tempo_min"], min_value=0, step=5, key="tempo_min")
    custo_execucao = (tempo_min / 60) * valor_hora if indireto == "Sim" else 0.0
    
    st.markdown("**3. Uso de máquina / equipamento**")
    df_maq = st.data_editor(st.session_state["df_maquinas_ficha"], num_rows="dynamic", use_container_width=True, hide_index=True, key="edit_maq")
    st.session_state["df_maquinas_ficha"] = df_maq
    custo_maquinas = df_maq["Custo da Máquina (R$)"].sum()

    custo_aluguel = st.number_input("4. Aluguel de máquina (hora) R$:", value=st.session_state["custo_aluguel"], step=10.0, key="custo_aluguel")
    repasse_fixo = st.number_input("5. Repasse para profissionais (Fixo R$):", value=st.session_state["repasse_fixo"], step=10.0, key="repasse_fixo")

    st.markdown("**6. Custo materiais e insumos**")
    df_ins = st.data_editor(st.session_state["df_insumos_ficha"], num_rows="dynamic", use_container_width=True, hide_index=True, key="edit_ins")
    st.session_state["df_insumos_ficha"] = df_ins
    
    # Previne erro se o usuário apagar tudo
    df_ins["Total Linha"] = pd.to_numeric(df_ins["QT"], errors='coerce').fillna(0) * pd.to_numeric(df_ins["Preço (R$)"], errors='coerce').fillna(0)
    custo_insumos = df_ins["Total Linha"].sum()

# Totalizador Lateral
custo_total_servico = custo_execucao + custo_maquinas + custo_aluguel + repasse_fixo + custo_insumos

with col_dir:
    st.markdown(f"<div style='background-color: {COR_FUNDO_CLARO}; padding: 15px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.markdown("#### Custo Acumulado")
    st.write(f"Custo de Execução: **R$ {custo_execucao:,.2f}**")
    st.write(f"Custo de Máquina(s): **R$ {custo_maquinas:,.2f}**")
    st.write(f"Aluguel: **R$ {custo_aluguel:,.2f}**")
    st.write(f"Repasse Fixo: **R$ {repasse_fixo:,.2f}**")
    st.write(f"Materiais: **R$ {custo_insumos:,.2f}**")
    st.divider()
    st.markdown(f"<h3 style='color: {COR_CABECALHO}; margin:0;'>TOTAL R$ {custo_total_servico:,.2f}</h3>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- 3. TAXAS E MARGENS ---
st.markdown(f"""
<div style="background-color: {COR_FUNDO_CLARO}; padding: 5px;">
    <b>TAXAS</b>
</div>
""", unsafe_allow_html=True)

col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)
taxa_comissao = col_t1.number_input("COMISSÃO VENDAS (%)", value=st.session_state["taxa_comissao"], key="taxa_comissao") / 100
taxa_cartao = col_t2.number_input("TAXA CARTÃO (%)", value=st.session_state["taxa_cartao"], key="taxa_cartao") / 100
taxa_imposto = col_t3.number_input("IMPOSTO (%)", value=st.session_state["taxa_imposto"], key="taxa_imposto") / 100
taxa_repasse = col_t4.number_input("REPASSE LÍQUIDO (%)", value=st.session_state["taxa_repasse_liq"], key="taxa_repasse_liq") / 100
taxa_lucro = col_t5.number_input("LUCRO ALVO (%)", value=st.session_state["taxa_lucro"], key="taxa_lucro") / 100

st.write("")

# --- 4. CÁLCULO DE PRECIFICAÇÃO E TABELAS FINAIS ---
st.markdown(f"""
<div style="background-color: {COR_FUNDO_CLARO}; padding: 5px;">
    <b>ANÁLISE DE PREÇO</b>
</div>
""", unsafe_allow_html=True)

preco_mercado = st.number_input("PREÇO DE MERCADO (Pesquisa R$)", value=st.session_state["preco_mercado"], step=10.0, key="preco_mercado")
preco_escolhido = st.number_input("PREÇO DE TABELA ESCOLHIDO (R$)", value=st.session_state["preco_escolhido"], step=10.0, key="preco_escolhido")

# Matemática do Preço Calculado (Markup reverso)
deducoes_brutas = taxa_comissao + taxa_cartao + taxa_imposto
margem_repasse_sobre_preco = (1 - deducoes_brutas) * taxa_repasse
denominador = 1 - deducoes_brutas - margem_repasse_sobre_preco - taxa_lucro

preco_calculado = custo_total_servico / denominador if denominador > 0 else 0.0

# Função para gerar a linha da tabela de resultados
def gerar_linha_resultado(nome, preco):
    comissao = preco * taxa_comissao
    cartao = preco * taxa_cartao
    imposto = preco * taxa_imposto
    liquido = preco - comissao - cartao - imposto
    repasse = liquido * taxa_repasse
    lucro = liquido - repasse - custo_total_servico
    pct_lucro = (lucro / preco) if preco > 0 else 0.0
    
    return {
        "CENÁRIO": nome,
        "PREÇO FINAL": preco,
        "COMISSÃO": comissao,
        "CARTÃO": cartao,
        "IMPOSTO": imposto,
        "RESULT. LÍQUIDO": liquido,
        "REPASSE MÉD.": repasse,
        "CUSTO SERVIÇO": custo_total_servico,
        "LUCRO": lucro,
        "% LUCRO": pct_lucro
    }

# Construindo o DataFrame de Resultados Finais
resultados = [
    gerar_linha_resultado("MERCADO", preco_mercado),
    gerar_linha_resultado("FÓRMULA (CALCULADO)", preco_calculado),
    gerar_linha_resultado("TABELA ESCOLHIDO", preco_escolhido)
]

df_resultados = pd.DataFrame(resultados)

# Estilização da Tabela Final
estilo_resultados = df_resultados.style.format({
    "PREÇO FINAL": "R$ {:,.2f}",
    "COMISSÃO": "R$ {:,.2f}",
    "CARTÃO": "R$ {:,.2f}",
    "IMPOSTO": "R$ {:,.2f}",
    "RESULT. LÍQUIDO": "R$ {:,.2f}",
    "REPASSE MÉD.": "R$ {:,.2f}",
    "CUSTO SERVIÇO": "R$ {:,.2f}",
    "LUCRO": "R$ {:,.2f}",
    "% LUCRO": "{:.1%}"
}).apply(lambda x: ['background: #7030A0; color: white' if x.name == 2 else '' for i in x], axis=1) # Pinta a última linha de roxo

st.write("")
st.dataframe(estilo_resultados, use_container_width=True, hide_index=True)