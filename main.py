import streamlit as st
import pandas as pd
import json
from banco_servicos import obter_servicos_cadastrados

st.set_page_config(page_title="Sistema de Precificação", layout="wide")

# --- ESTILOS VISUAIS ---
COR_CABECALHO = "#7030A0"
COR_FUNDO_CLARO = "#E6E0EC"
COR_TEXTO_BRANCO = "#FFFFFF"

# --- 1. BANCO DE DADOS ---
db_servicos = obter_servicos_cadastrados()
lista_nomes_servicos = list(db_servicos.keys())

# --- 2. GERENCIAMENTO DE MEMÓRIA (SESSION STATE) ---
# Função que puxa os dados do banco e joga para a memória da tela
def carregar_servico_para_estado(nome_servico):
    dados = db_servicos[nome_servico]
    st.session_state['servico_atual'] = nome_servico
    st.session_state['tempo_min'] = dados['tempo_min']
    st.session_state['repasse_fixo'] = dados['repasse_fixo']
    st.session_state['df_maquinas'] = pd.DataFrame(dados['maquinas']) if dados['maquinas'] else pd.DataFrame({"nome": [""], "custo": [0.0]})
    st.session_state['df_insumos'] = pd.DataFrame(dados['insumos']) if dados['insumos'] else pd.DataFrame({"Material": [""], "QT": [0], "Preço (R$)": [0.0]})
    st.session_state['taxa_comissao'] = float(dados['taxas']['comissao'])
    st.session_state['taxa_cartao'] = float(dados['taxas']['cartao'])
    st.session_state['taxa_imposto'] = float(dados['taxas']['imposto'])
    st.session_state['preco_escolhido'] = float(dados['preco_escolhido'])
    
    # Valores padrão que não vieram do banco
    if 'custo_aluguel' not in st.session_state: st.session_state['custo_aluguel'] = 0.0
    if 'indireto' not in st.session_state: st.session_state['indireto'] = "Sim"
    if 'valor_hora' not in st.session_state: st.session_state['valor_hora'] = 48.14

# Inicializa o primeiro serviço ao abrir o app
if 'servico_atual' not in st.session_state:
    carregar_servico_para_estado(lista_nomes_servicos[0])

# --- 3. BARRA LATERAL: SALVAR E CARREGAR ---
with st.sidebar:
    st.header("💾 Salvar / Carregar Ficha")
    
    arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"])
    if arquivo_upload is not None:
        try:
            dados_json = json.load(arquivo_upload)
            for k, v in dados_json.items():
                if k in ['df_maquinas', 'df_insumos']:
                    st.session_state[k] = pd.DataFrame(v)
                else:
                    st.session_state[k] = v
            st.success("Ficha carregada com sucesso!")
        except Exception as e:
            st.error("Erro ao ler o arquivo.")

    st.divider()

    # Prepara os dados atuais da tela para virarem JSON
    dados_para_salvar = {
        'servico_atual': st.session_state['servico_atual'],
        'tempo_min': st.session_state['tempo_min'],
        'repasse_fixo': st.session_state['repasse_fixo'],
        'df_maquinas': st.session_state['df_maquinas'].to_dict(orient='records'),
        'df_insumos': st.session_state['df_insumos'].to_dict(orient='records'),
        'taxa_comissao': st.session_state['taxa_comissao'],
        'taxa_cartao': st.session_state['taxa_cartao'],
        'taxa_imposto': st.session_state['taxa_imposto'],
        'preco_escolhido': st.session_state['preco_escolhido'],
        'custo_aluguel': st.session_state['custo_aluguel'],
        'indireto': st.session_state['indireto'],
        'valor_hora': st.session_state['valor_hora']
    }

    st.download_button(
        label="📥 Baixar Configuração",
        data=json.dumps(dados_para_salvar, indent=4),
        file_name=f"simulacao_{st.session_state['servico_atual'].replace(' ', '_')}.json",
        mime="application/json"
    )
    
    st.divider()
    
    st.header("⚙️ Parâmetros Globais")
    indireto = st.selectbox("Com Custo Indireto (Hora Clínica)?", ["Sim", "Não"], key='indireto')
    valor_hora = st.number_input("Valor da Hora Clínica (R$)", step=1.0, key='valor_hora')

# --- 4. CABEÇALHO PRINCIPAL ---
st.markdown(f"""
<div style="background-color: {COR_CABECALHO}; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
    <h2 style="margin: 0; color: {COR_TEXTO_BRANCO};">PORTAL DE PRECIFICAÇÃO CLÍNICA</h2>
</div>
""", unsafe_allow_html=True)

# Função para mudar de serviço quando o usuário clica no menu
def mudou_servico():
    novo_servico = st.session_state['combo_servico']
    carregar_servico_para_estado(novo_servico)

st.markdown("### Selecione o Serviço para análise:")
servico_selecionado = st.selectbox(
    "Filtro de Serviços", 
    options=lista_nomes_servicos,
    index=lista_nomes_servicos.index(st.session_state['servico_atual']) if st.session_state['servico_atual'] in lista_nomes_servicos else 0,
    key='combo_servico',
    on_change=mudou_servico,
    label_visibility="collapsed"
)

st.divider()

# --- 5. FICHA TÉCNICA DINÂMICA ---
st.markdown(f"#### Ficha Técnica: **{st.session_state['servico_atual']}**")

col_esq, col_dir = st.columns([2, 1])

with col_esq:
    tempo_min = st.number_input("2. TEMPO de execução (Minutos):", step=5, key='tempo_min')
    custo_execucao = (tempo_min / 60) * st.session_state['valor_hora'] if st.session_state['indireto'] == "Sim" else 0.0
    
    st.markdown("**3. Uso de máquina / equipamento**")
    df_maq = st.data_editor(st.session_state['df_maquinas'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state['df_maquinas'] = df_maq
    custo_maquinas = df_maq["custo"].sum() if not df_maq.empty and "custo" in df_maq else 0.0

    custo_aluguel = st.number_input("4. Aluguel de máquina (hora) R$:", step=10.0, key='custo_aluguel')
    repasse_fixo = st.number_input("5. Repasse para profissionais (Fixo R$):", step=10.0, key='repasse_fixo')

    st.markdown("**6. Custo materiais e insumos**")
    df_ins = st.data_editor(st.session_state['df_insumos'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state['df_insumos'] = df_ins
    
    if not df_ins.empty and "QT" in df_ins and "Preço (R$)" in df_ins:
        df_ins["Total Linha"] = pd.to_numeric(df_ins["QT"], errors='coerce').fillna(0) * pd.to_numeric(df_ins["Preço (R$)"], errors='coerce').fillna(0)
        custo_insumos = df_ins["Total Linha"].sum()
    else:
        custo_insumos = 0.0

# Totalizador
custo_total_servico = custo_execucao + custo_maquinas + custo_aluguel + repasse_fixo + custo_insumos

with col_dir:
    st.markdown(f"<div style='background-color: {COR_FUNDO_CLARO}; padding: 15px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.markdown("#### Resumo de Custos")
    st.write(f"Custo de Execução: **R$ {custo_execucao:,.2f}**")
    st.write(f"Custo de Máquina(s): **R$ {custo_maquinas:,.2f}**")
    st.write(f"Repasse Fixo: **R$ {repasse_fixo:,.2f}**")
    st.write(f"Materiais: **R$ {custo_insumos:,.2f}**")
    st.divider()
    st.markdown(f"<h3 style='color: {COR_CABECALHO}; margin:0;'>TOTAL R$ {custo_total_servico:,.2f}</h3>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- 6. TAXAS E RESULTADOS ---
st.markdown("#### Taxas e Precificação")

col_t1, col_t2, col_t3 = st.columns(3)
taxa_comissao = col_t1.number_input("COMISSÃO (%)", key='taxa_comissao') / 100
taxa_cartao = col_t2.number_input("TAXA CARTÃO (%)", key='taxa_cartao') / 100
taxa_imposto = col_t3.number_input("IMPOSTO (%)", key='taxa_imposto') / 100

st.write("")
preco_escolhido = st.number_input("PREÇO DE TABELA ESCOLHIDO (R$)", step=10.0, key='preco_escolhido')

# Cálculos Finais
comissao = preco_escolhido * taxa_comissao
cartao = preco_escolhido * taxa_cartao
imposto = preco_escolhido * taxa_imposto
liquido = preco_escolhido - comissao - cartao - imposto
lucro = liquido - custo_total_servico
pct_lucro = (lucro / preco_escolhido) if preco_escolhido > 0 else 0.0

# Tabela de Resultado
df_resultados = pd.DataFrame([{
    "CENÁRIO": "TABELA ESCOLHIDO", "PREÇO FINAL": preco_escolhido,
    "COMISSÃO": comissao, "CARTÃO": cartao, "IMPOSTO": imposto,
    "RESULT. LÍQUIDO": liquido, "CUSTO SERVIÇO": custo_total_servico,
    "LUCRO": lucro, "% LUCRO": pct_lucro
}])

estilo = df_resultados.style.format({
    "PREÇO FINAL": "R$ {:,.2f}", "COMISSÃO": "R$ {:,.2f}", "CARTÃO": "R$ {:,.2f}",
    "IMPOSTO": "R$ {:,.2f}", "RESULT. LÍQUIDO": "R$ {:,.2f}", "CUSTO SERVIÇO": "R$ {:,.2f}",
    "LUCRO": "R$ {:,.2f}", "% LUCRO": "{:.1%}"
}).apply(lambda x: ['background: #7030A0; color: white' for i in x], axis=1)

st.dataframe(estilo, use_container_width=True, hide_index=True)