import streamlit as st
import pandas as pd
import json
import plotly.express as px

# Fallback caso o arquivo banco_servicos não esteja no mesmo diretório na hora do teste
try:
    from banco_servicos import obter_servicos_cadastrados
except ImportError:
    def obter_servicos_cadastrados(): return {}

# O set_page_config deve ser sempre a primeira instrução
st.set_page_config(page_title="Sistema Integrado de Precificação", layout="wide")

# ==========================================
# CONFIGURAÇÕES GERAIS E ESTILOS
# ==========================================
COR_CABECALHO = "#7030A0"
COR_FUNDO_CLARO = "#E6E0EC"
COR_TEXTO_BRANCO = "#FFFFFF"

# Injeção de CSS para melhorar o contraste dos inputs
st.markdown(f"""
    <style>
    /* Borda escura e fundo branco para os campos de texto e número */
    div[data-baseweb="input"] > div {{
        background-color: #FFFFFF !important;
        border: 1px solid #6C757D !important; /* Cinza escuro para contraste */
        border-radius: 6px !important;
    }}
    
    /* Efeito de foco quando o usuário clica no campo */
    div[data-baseweb="input"] > div:focus-within {{
        border-color: {COR_CABECALHO} !important; 
        box-shadow: 0 0 0 1.5px {COR_CABECALHO} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZAÇÃO DE MEMÓRIA GLOBAL SEGURA
# ==========================================
if "db_servicos" not in st.session_state:
    st.session_state["db_servicos"] = obter_servicos_cadastrados()

def df_maquinas_padrao():
    return pd.DataFrame(columns=["nome", "custo"])

def df_insumos_padrao():
    return pd.DataFrame(columns=["Material", "QT", "Preço (R$)"])

def inicializar_estado_ficha():
    lista_nomes_servicos = list(st.session_state["db_servicos"].keys())
    
    if not lista_nomes_servicos:
        st.session_state.setdefault("servico_atual", "")
        st.session_state.setdefault("tempo_min", 60)
        st.session_state.setdefault("repasse_fixo", 0.0)
        st.session_state.setdefault("df_ficha_maquinas", df_maquinas_padrao())
        st.session_state.setdefault("df_ficha_insumos", df_insumos_padrao())
        st.session_state.setdefault("taxa_comissao", 0.0)   
        st.session_state.setdefault("taxa_cartao", 0.0)     
        st.session_state.setdefault("taxa_imposto", 12.0)   
        st.session_state.setdefault("preco_escolhido", 0.0)
        st.session_state.setdefault("custo_aluguel", 0.0)
        st.session_state.setdefault("indireto", "Sim")
        st.session_state.setdefault("valor_hora", 48.14)
        return

    primeiro_servico = lista_nomes_servicos[0]
    dados_iniciais = st.session_state["db_servicos"][primeiro_servico]

    st.session_state.setdefault("servico_atual", primeiro_servico)
    st.session_state.setdefault("tempo_min", dados_iniciais.get("tempo_min", 60))
    st.session_state.setdefault("repasse_fixo", dados_iniciais.get("repasse_fixo", 0.0))
    st.session_state.setdefault(
        "df_ficha_maquinas",
        pd.DataFrame(dados_iniciais.get("maquinas", [])) if dados_iniciais.get("maquinas") else df_maquinas_padrao()
    )
    st.session_state.setdefault(
        "df_ficha_insumos",
        pd.DataFrame(dados_iniciais.get("insumos", [])) if dados_iniciais.get("insumos") else df_insumos_padrao()
    )
    st.session_state.setdefault("taxa_comissao", float(dados_iniciais.get("taxas", {}).get("comissao", 0.0)))
    st.session_state.setdefault("taxa_cartao", float(dados_iniciais.get("taxas", {}).get("cartao", 0.0)))
    st.session_state.setdefault("taxa_imposto", float(dados_iniciais.get("taxas", {}).get("imposto", 12.0)))
    st.session_state.setdefault("preco_escolhido", float(dados_iniciais.get("preco_escolhido", 0.0)))
    st.session_state.setdefault("custo_aluguel", 0.0)
    st.session_state.setdefault("indireto", "Sim")
    st.session_state.setdefault("valor_hora", 48.14)

def carregar_servico_para_estado(nome_servico):
    if nome_servico not in st.session_state["db_servicos"]: return
    dados = st.session_state["db_servicos"][nome_servico]

    st.session_state["servico_atual"] = nome_servico
    st.session_state["tempo_min"] = dados.get("tempo_min", 60)
    st.session_state["repasse_fixo"] = dados.get("repasse_fixo", 0.0)
    st.session_state["df_ficha_maquinas"] = (
        pd.DataFrame(dados.get("maquinas", [])) if dados.get("maquinas") else df_maquinas_padrao()
    )
    st.session_state["df_ficha_insumos"] = (
        pd.DataFrame(dados.get("insumos", [])) if dados.get("insumos") else df_insumos_padrao()
    )
    st.session_state["taxa_comissao"] = float(dados.get("taxas", {}).get("comissao", 0.0))
    st.session_state["taxa_cartao"] = float(dados.get("taxas", {}).get("cartao", 0.0))
    st.session_state["taxa_imposto"] = float(dados.get("taxas", {}).get("imposto", 12.0))
    st.session_state["preco_escolhido"] = float(dados.get("preco_escolhido", 0.0))

    st.session_state.setdefault("custo_aluguel", 0.0)
    st.session_state.setdefault("indireto", "Sim")
    st.session_state.setdefault("valor_hora", 48.14)

inicializar_estado_ficha()

# ==========================================
# MENU LATERAL
# ==========================================
with st.sidebar:
    st.title("📌 Menu Principal")
    modulo_selecionado = st.radio(
        "Navegue pelas ferramentas:",
        [
            "1. Ficha Técnica (Precificação)",
            "2. Custos Fixos e Hora Clínica",
            "3. Registro de Equipamentos",
            "4. Insumos e Materiais",
            "5. Impostos e Taxas"
        ]
    )
    st.divider()

# ==========================================
# MÓDULO 1: FICHA TÉCNICA
# ==========================================
def render_ficha_tecnica():
    with st.sidebar:
        st.header("💾 Salvar / Carregar Ficha")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_ficha")
        if arquivo_upload is not None:
            try:
                dados_json = json.load(arquivo_upload)
                for k, v in dados_json.items():
                    if k in ["df_ficha_maquinas", "df_ficha_insumos"]:
                        st.session_state[k] = pd.DataFrame(v)
                    else:
                        st.session_state[k] = v

                st.session_state.setdefault("custo_aluguel", 0.0)
                st.session_state.setdefault("indireto", "Sim")
                st.session_state.setdefault("valor_hora", 48.14)
                st.success("Ficha carregada com sucesso!")
            except Exception:
                st.error("Erro ao ler o arquivo.")
        st.divider()

        dados_para_salvar = {
            "servico_atual": st.session_state.get("servico_atual", ""),
            "tempo_min": st.session_state.get("tempo_min", 60),
            "repasse_fixo": st.session_state.get("repasse_fixo", 0.0),
            "df_ficha_maquinas": st.session_state.get("df_ficha_maquinas", df_maquinas_padrao()).to_dict(orient="records"),
            "df_ficha_insumos": st.session_state.get("df_ficha_insumos", df_insumos_padrao()).to_dict(orient="records"),
            "taxa_comissao": st.session_state.get("taxa_comissao", 0.0),
            "taxa_cartao": st.session_state.get("taxa_cartao", 0.0),
            "taxa_imposto": st.session_state.get("taxa_imposto", 12.0),
            "preco_escolhido": st.session_state.get("preco_escolhido", 0.0),
            "custo_aluguel": st.session_state.get("custo_aluguel", 0.0),
            "indireto": st.session_state.get("indireto", "Sim"),
            "valor_hora": st.session_state.get("valor_hora", 48.14)
        }

        st.download_button(
            label="📥 Baixar Configuração",
            data=json.dumps(dados_para_salvar, indent=4),
            file_name=f"simulacao_{st.session_state.get('servico_atual', 'servico').replace(' ', '_')}.json",
            mime="application/json"
        )
        st.divider()
        st.header("⚙️ Parâmetros Globais")
        st.selectbox("Com Custo Indireto?", ["Sim", "Não"], key="indireto")
        st.number_input("Valor da Hora Clínica (R$)", min_value=0.0, step=1.0, format="%.2f", key="valor_hora")

    st.markdown(f"""
    <div style="background-color: {COR_CABECALHO}; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
        <h2 style="margin: 0; color: {COR_TEXTO_BRANCO};">PORTAL DE PRECIFICAÇÃO CLÍNICA</h2>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("⚙️ Gerenciar Serviços")
    tab_add, tab_ren, tab_del = st.tabs(["➕ Adicionar", "✏️ Renomear", "🗑️ Excluir"])
    opcoes_servicos = list(st.session_state["db_servicos"].keys())

    with tab_add:
        c1, c2 = st.columns([2, 1])
        novo_nome = c1.text_input("Nome do Novo Serviço:")
        st.write("")
        if c2.button("Criar Serviço", use_container_width=True):
            if novo_nome and novo_nome not in st.session_state["db_servicos"]:
                st.session_state["db_servicos"][novo_nome] = {
                    "tempo_min": 60, "maquinas": [], "repasse_fixo": 0.0, "insumos": [],
                    "taxas": {"comissao": 0.0, "cartao": 0.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
                    "preco_escolhido": 0.0
                }
                carregar_servico_para_estado(novo_nome)
                st.rerun()
            elif novo_nome in st.session_state["db_servicos"]:
                st.warning("Serviço já existe.")
                
    with tab_ren:
        c1, c2, c3 = st.columns([2, 2, 1])
        servico_renomear = c1.selectbox("Serviço atual:", options=opcoes_servicos, key="sel_ren_serv")
        novo_nome_serv = c2.text_input("Mudar para:", value=servico_renomear if opcoes_servicos else "", key="input_ren_serv")
        st.write("")
        if c3.button("Salvar Nome", use_container_width=True):
            if novo_nome_serv and novo_nome_serv != servico_renomear:
                novo_dict = {}
                for k, v in st.session_state["db_servicos"].items():
                    if k == servico_renomear:
                        novo_dict[novo_nome_serv] = v
                    else:
                        novo_dict[k] = v
                st.session_state["db_servicos"] = novo_dict
                if st.session_state.get("servico_atual") == servico_renomear:
                    st.session_state["servico_atual"] = novo_nome_serv
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        servico_remover = c1.selectbox("Selecione para remover:", options=opcoes_servicos, key="sel_rem_serv")
        st.write("")
        if c2.button("🗑️ Remover Selecionado", use_container_width=True):
            if servico_remover in st.session_state["db_servicos"]:
                del st.session_state["db_servicos"][servico_remover]
                if st.session_state.get("servico_atual") == servico_remover:
                    st.session_state["servico_atual"] = ""
                    if st.session_state["db_servicos"]:
                        carregar_servico_para_estado(list(st.session_state["db_servicos"].keys())[0])
                st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODOS", type="primary", use_container_width=True):
            st.session_state["db_servicos"] = {}
            st.session_state["servico_atual"] = ""
            st.rerun()

    lista_nomes_servicos = list(st.session_state["db_servicos"].keys())
    if not lista_nomes_servicos:
        st.warning("Nenhum serviço cadastrado no banco. Adicione um serviço acima.")
        return

    if "tempo_min" not in st.session_state or st.session_state["servico_atual"] not in lista_nomes_servicos:
        carregar_servico_para_estado(lista_nomes_servicos[0])

    st.markdown("### Selecione o Serviço:")
    st.selectbox(
        "Filtro", options=lista_nomes_servicos,
        index=lista_nomes_servicos.index(st.session_state["servico_atual"]) if st.session_state["servico_atual"] in lista_nomes_servicos else 0,
        key="combo_servico", on_change=lambda: carregar_servico_para_estado(st.session_state["combo_servico"]),
        label_visibility="collapsed"
    )

    if st.button("💾 Atualizar Serviço no Banco", type="primary"):
        st.session_state["db_servicos"][st.session_state["servico_atual"]] = {
            "tempo_min": st.session_state["tempo_min"],
            "maquinas": st.session_state["df_ficha_maquinas"].to_dict(orient="records"),
            "repasse_fixo": st.session_state["repasse_fixo"],
            "insumos": st.session_state["df_ficha_insumos"].to_dict(orient="records"),
            "taxas": {
                "comissao": st.session_state["taxa_comissao"], "cartao": st.session_state["taxa_cartao"],
                "imposto": st.session_state["taxa_imposto"], "repasse_liq": 0.0, "lucro": 0.0
            },
            "preco_escolhido": st.session_state["preco_escolhido"]
        }
        st.success("Salvo com sucesso!")

    st.divider()
    col_esq, col_dir = st.columns([2, 1])

    with col_esq:
        tempo_min = st.number_input("TEMPO de execução (Minutos):", min_value=0.0, step=5.0, format="%.0f", key="tempo_min")
        custo_execucao = (tempo_min / 60) * st.session_state["valor_hora"] if st.session_state["indireto"] == "Sim" else 0.0

        st.markdown("#### Máquinas / Equipamentos no Serviço")
        regs_maq = st.session_state["df_ficha_maquinas"].to_dict('records')
        for i, reg in enumerate(regs_maq):
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(f"• {reg['nome']}")
            c2.write(f"R$ {float(reg['custo']):.2f}")
            if c3.button("🗑️", key=f"del_maq_{i}"):
                regs_maq.pop(i)
                st.session_state["df_ficha_maquinas"] = pd.DataFrame(regs_maq) if regs_maq else df_maquinas_padrao()
                st.rerun()
                
        with st.form("form_add_maq", clear_on_submit=True):
            st.write("➕ Adicionar Máquina ao Serviço")
            c1, c2, c3 = st.columns([4, 2, 2])
            n_nome = c1.text_input("Nome da Máquina")
            n_custo = c2.number_input("Custo (R$)", min_value=0.0, step=10.0, format="%.2f")
            if c3.form_submit_button("Adicionar"):
                if n_nome:
                    regs_maq.append({"nome": n_nome, "custo": float(n_custo)})
                    st.session_state["df_ficha_maquinas"] = pd.DataFrame(regs_maq)
                    st.rerun()

        custo_maquinas = sum(pd.to_numeric(r.get("custo", 0.0)) for r in regs_maq)
        custo_aluguel = st.number_input("Aluguel extra de máquina (hora) R$:", min_value=0.0, step=10.0, format="%.2f", key="custo_aluguel")
        repasse_fixo = st.number_input("Repasse para profissionais (Fixo R$):", min_value=0.0, step=10.0, format="%.2f", key="repasse_fixo")

        st.markdown("#### Materiais e Insumos no Serviço")
        regs_ins = st.session_state["df_ficha_insumos"].to_dict('records')
        for i, reg in enumerate(regs_ins):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"• {reg['Material']}")
            c2.write(f"Qtd: {reg['QT']}")
            c3.write(f"R$ {float(reg['Preço (R$)']):.2f}")
            if c4.button("🗑️", key=f"del_ins_{i}"):
                regs_ins.pop(i)
                st.session_state["df_ficha_insumos"] = pd.DataFrame(regs_ins) if regs_ins else df_insumos_padrao()
                st.rerun()

        with st.form("form_add_ins", clear_on_submit=True):
            st.write("➕ Adicionar Insumo ao Serviço")
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            n_mat = c1.text_input("Material")
            n_qt = c2.number_input("Qtd", min_value=0.01, step=1.0)
            n_preco = c3.number_input("Preço Unitário (R$)", min_value=0.0, step=0.10, format="%.3f")
            if c4.form_submit_button("Adicionar"):
                if n_mat:
                    regs_ins.append({"Material": n_mat, "QT": float(n_qt), "Preço (R$)": float(n_preco)})
                    st.session_state["df_ficha_insumos"] = pd.DataFrame(regs_ins)
                    st.rerun()

        custo_insumos = sum((float(r.get("QT", 0)) * float(r.get("Preço (R$)", 0))) for r in regs_ins)

    custo_total_servico = custo_execucao + custo_maquinas + custo_aluguel + repasse_fixo + custo_insumos

    with col_dir:
        st.markdown(f"<div style='background-color: {COR_FUNDO_CLARO}; padding: 15px; border-radius: 5px;'>", unsafe_allow_html=True)
        st.markdown("#### Resumo de Custos")
        st.write(f"Execução: **R$ {custo_execucao:,.2f}**")
        st.write(f"Máquina(s): **R$ {custo_maquinas:,.2f}**")
        st.write(f"Aluguel: **R$ {custo_aluguel:,.2f}**")
        st.write(f"Repasse Fixo: **R$ {repasse_fixo:,.2f}**")
        st.write(f"Materiais: **R$ {custo_insumos:,.2f}**")
        st.divider()
        st.markdown(f"<h3 style='color: {COR_CABECALHO}; margin:0;'>TOTAL R$ {custo_total_servico:,.2f}</h3>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Taxas e Precificação")
    col_t1, col_t2, col_t3 = st.columns(3)
    taxa_comissao_pct = col_t1.number_input("COMISSÃO (%)", min_value=0.0, step=0.1, format="%.2f", key="taxa_comissao")
    taxa_cartao_pct = col_t2.number_input("TAXA CARTÃO (%)", min_value=0.0, step=0.1, format="%.2f", key="taxa_cartao")
    taxa_imposto_pct = col_t3.number_input("IMPOSTO (%)", min_value=0.0, step=0.1, format="%.2f", key="taxa_imposto")

    preco_escolhido = st.number_input("PREÇO DE TABELA (R$)", min_value=0.0, step=10.0, format="%.2f", key="preco_escolhido")

    liquido = preco_escolhido - (preco_escolhido * (taxa_comissao_pct/100)) - (preco_escolhido * (taxa_cartao_pct/100)) - (preco_escolhido * (taxa_imposto_pct/100))
    lucro = liquido - custo_total_servico
    pct_lucro = (lucro / preco_escolhido) if preco_escolhido > 0 else 0.0

    df_res = pd.DataFrame([{
        "PREÇO FINAL": preco_escolhido, "RESULT. LÍQUIDO": liquido,
        "CUSTO SERVIÇO": custo_total_servico, "LUCRO": lucro, "% LUCRO": pct_lucro
    }])
    estilo = df_res.style.format({"PREÇO FINAL": "R$ {:,.2f}", "RESULT. LÍQUIDO": "R$ {:,.2f}", "CUSTO SERVIÇO": "R$ {:,.2f}", "LUCRO": "R$ {:,.2f}", "% LUCRO": "{:.1%}"}).apply(lambda x: ["background: #7030A0; color: white" for _ in x], axis=1)
    st.dataframe(estilo, use_container_width=True, hide_index=True)


# ==========================================
# MÓDULO 2: CUSTOS FIXOS
# ==========================================
def render_custos_fixos():
    if "df_custos_categorias" not in st.session_state:
        st.session_state["df_custos_categorias"] = {
            "1. Despesa com pessoal": pd.DataFrame([
                {"ÍTEM": "1.1 Total da folha de pagamento", "MENSAL (R$)": 0.0},
                {"ÍTEM": "1.2 Despesas com alimentação e transporte", "MENSAL (R$)": 0.0},
                {"ÍTEM": "1.3 Reserva para recisões", "MENSAL (R$)": 0.0},
                {"ÍTEM": "1.4 Pro-labore", "MENSAL (R$)": 0.0},
                {"ÍTEM": "1.6 Gratificações", "MENSAL (R$)": 0.0},
                {"ÍTEM": "1.7 INSS", "MENSAL (R$)": 0.0},
                {"ÍTEM": "1.8 FGTS", "MENSAL (R$)": 0.0},
                {"ÍTEM": "1.9 Uniformes", "MENSAL (R$)": 0.0}
            ]),
            "2. Seguros": pd.DataFrame([
                {"ÍTEM": "2.1 Seguros do estabelecimento", "MENSAL (R$)": 0.0},
                {"ÍTEM": "2.2 Seguro médico", "MENSAL (R$)": 0.0},
                {"ÍTEM": "2.3 Outros seguros", "MENSAL (R$)": 0.0}
            ]),
            "3. Manutenção e conservação": pd.DataFrame([
                {"ÍTEM": "3.1 Elevadores", "MENSAL (R$)": 0.0},
                {"ÍTEM": "3.2 Manutenção do prédio", "MENSAL (R$)": 0.0},
                {"ÍTEM": "3.3 Coleta de lixo hospitalar", "MENSAL (R$)": 0.0},
                {"ÍTEM": "3.4 Manutenção de equipamentos", "MENSAL (R$)": 0.0},
                {"ÍTEM": "3.5 Pinturas", "MENSAL (R$)": 0.0},
                {"ÍTEM": "3.6 Jardins", "MENSAL (R$)": 0.0},
                {"ÍTEM": "3.7 Extintores", "MENSAL (R$)": 0.0},
                {"ÍTEM": "3.9 Outras despesas", "MENSAL (R$)": 0.0}
            ]),
            "4. Despesas estrutura e de consumo": pd.DataFrame([
                {"ÍTEM": "4.1 Aluguel", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.2 Condomínio", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.3 Energia Elétrica", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.4 Água", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.5 Telefones/Interfones", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.6 Internet", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.7 Faxina", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.8 Material de limpeza", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.9 Material de escritório", "MENSAL (R$)": 0.0},
                {"ÍTEM": "4.10 IPTU", "MENSAL (R$)": 0.0}
            ]),
            "5. Despesas Administrativas e Licenças": pd.DataFrame([
                {"ÍTEM": "5.1 Contador", "MENSAL (R$)": 0.0},
                {"ÍTEM": "5.3 Entidades de Classe", "MENSAL (R$)": 0.0},
                {"ÍTEM": "5.4 Licenças, Alvarás e certidões", "MENSAL (R$)": 0.0},
                {"ÍTEM": "5.5 Outras despesas administrativas", "MENSAL (R$)": 0.0}
            ]),
            "6. Despesas com TI": pd.DataFrame([
                {"ÍTEM": "6.1 Sistemas de gestão", "MENSAL (R$)": 0.0},
                {"ÍTEM": "6.3 Chat bot / recursos de automação", "MENSAL (R$)": 0.0}
            ]),
            "7. Despesas bancárias": pd.DataFrame([
                {"ÍTEM": "7.1 Taxa administrativa de contas", "MENSAL (R$)": 0.0},
                {"ÍTEM": "7.2 Máquinas de cartão", "MENSAL (R$)": 0.0},
                {"ÍTEM": "7.3 Iof / juros", "MENSAL (R$)": 0.0},
                {"ÍTEM": "7.4 Outras despesas", "MENSAL (R$)": 0.0}
            ]),
            "8. Marketing e vendas": pd.DataFrame([
                {"ÍTEM": "8.1 Agência", "MENSAL (R$)": 0.0},
                {"ÍTEM": "8.2 Eventos", "MENSAL (R$)": 0.0},
                {"ÍTEM": "8.3 Social mídia", "MENSAL (R$)": 0.0},
                {"ÍTEM": "8.4 Tráfego Pago e gestão", "MENSAL (R$)": 0.0},
                {"ÍTEM": "8.5 Patrocínio", "MENSAL (R$)": 0.0},
                {"ÍTEM": "8.6 Facebook", "MENSAL (R$)": 0.0},
                {"ÍTEM": "8.7 Outras despesas", "MENSAL (R$)": 0.0}
            ])
        }

    def renderizar_categoria_dinamica(titulo, chave):
        with st.expander(titulo, expanded=False):
            df_atual = st.session_state["df_custos_categorias"][titulo]
            registros = df_atual.to_dict('records')

            # Renderiza inputs para permitir a edição in-line
            if registros:
                for idx, reg in enumerate(registros):
                    c1, c2, c3 = st.columns([5, 3, 1])
                    
                    novo_item = c1.text_input("Descrição", value=reg['ÍTEM'], key=f"edit_item_{chave}_{idx}", label_visibility="collapsed")
                    novo_valor = c2.number_input("Valor", value=float(reg['MENSAL (R$)']), min_value=0.0, step=10.0, format="%.2f", key=f"edit_val_{chave}_{idx}", label_visibility="collapsed")
                    
                    registros[idx]['ÍTEM'] = novo_item
                    registros[idx]['MENSAL (R$)'] = novo_valor
                    
                    if c3.button("🗑️", key=f"del_{chave}_{idx}"):
                        registros.pop(idx)
                        st.session_state["df_custos_categorias"][titulo] = pd.DataFrame(registros) if registros else pd.DataFrame(columns=["ÍTEM", "MENSAL (R$)"])
                        st.rerun()
                        
                st.session_state["df_custos_categorias"][titulo] = pd.DataFrame(registros) if registros else pd.DataFrame(columns=["ÍTEM", "MENSAL (R$)"])
            else:
                st.info("Nenhuma despesa cadastrada.")

            st.markdown("---")
            with st.form(f"form_add_{chave}", clear_on_submit=True):
                st.caption("Adicionar nova despesa:")
                c1, c2, c3 = st.columns([4, 2, 2])
                n_item = c1.text_input("Descrição da Despesa")
                n_valor = c2.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
                if c3.form_submit_button("➕ Adicionar"):
                    if n_item:
                        registros.append({"ÍTEM": n_item, "MENSAL (R$)": float(n_valor)})
                        st.session_state["df_custos_categorias"][titulo] = pd.DataFrame(registros)
                        st.rerun()

            total = sum(float(r["MENSAL (R$)"]) for r in registros) if registros else 0.0
            st.markdown(f"**Total da Categoria:** R$ {total:,.2f}")
            return total

    with st.sidebar:
        st.header("💾 Salvar / Carregar Dados")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_custos")
        if arquivo_upload is not None:
            try:
                dados_salvos = json.load(arquivo_upload)
                if "df_custos_categorias" in dados_salvos:
                    st.session_state["df_custos_categorias"] = {k: pd.DataFrame(v) for k, v in dados_salvos["df_custos_categorias"].items()}
                st.success("Dados carregados!")
            except Exception: st.error("Erro ao ler o arquivo.")
        st.divider()
        dados_salvar = {"df_custos_categorias": {k: v.to_dict(orient="records") for k, v in st.session_state["df_custos_categorias"].items()}}
        st.download_button("📥 Baixar Cenário", data=json.dumps(dados_salvar, indent=4), file_name="custos.json", mime="application/json")

    st.title("Gestão de Custos Fixos e Hora Clínica")

    st.subheader("⚙️ Gerenciar Categorias")
    
    tab_add, tab_ren, tab_del = st.tabs(["➕ Adicionar", "✏️ Renomear", "🗑️ Excluir"])
    opcoes_cat = list(st.session_state["df_custos_categorias"].keys())
    
    with tab_add:
        c1, c2 = st.columns([2, 1])
        nova_cat = c1.text_input("Nome da nova categoria:", placeholder="Ex: 9. Despesas Extras")
        st.write("")
        if c2.button("Criar Categoria", use_container_width=True):
            if nova_cat and nova_cat not in st.session_state["df_custos_categorias"]:
                st.session_state["df_custos_categorias"][nova_cat] = pd.DataFrame(columns=["ÍTEM", "MENSAL (R$)"])
                st.rerun()
                
    with tab_ren:
        c1, c2, c3 = st.columns([2, 2, 1])
        cat_renomear = c1.selectbox("Categoria atual:", options=opcoes_cat, key="sel_ren_cat")
        novo_nome_cat = c2.text_input("Mudar para:", value=cat_renomear if opcoes_cat else "", key="in_ren_cat")
        st.write("")
        if c3.button("Salvar Nome", use_container_width=True):
            if novo_nome_cat and novo_nome_cat != cat_renomear:
                novo_dict = {}
                for k, v in st.session_state["df_custos_categorias"].items():
                    if k == cat_renomear:
                        novo_dict[novo_nome_cat] = v
                    else:
                        novo_dict[k] = v
                st.session_state["df_custos_categorias"] = novo_dict
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        cat_remover = c1.selectbox("Selecione para remover:", options=opcoes_cat, key="sel_rem_cat")
        st.write("")
        if c2.button("🗑️ Remover Selecionada", use_container_width=True):
            if cat_remover in st.session_state["df_custos_categorias"]:
                del st.session_state["df_custos_categorias"][cat_remover]
                st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODAS", type="primary", use_container_width=True):
            st.session_state["df_custos_categorias"] = {}
            st.rerun()

    st.divider()
    col_inputs, col_dashboard = st.columns([1.8, 1])

    with col_inputs:
        despesa_mensal_media = 0.0
        resumo_dados = []
        if not st.session_state["df_custos_categorias"]:
            st.info("Nenhuma categoria. Adicione no menu acima.")
        else:
            for i, categoria in enumerate(st.session_state["df_custos_categorias"].keys()):
                tot_cat = renderizar_categoria_dinamica(categoria, f"cat_dyn_{i}")
                despesa_mensal_media += tot_cat
                resumo_dados.append({"Categoria": categoria, "Média Mensal": tot_cat})

    with col_dashboard:
        st.subheader("Cálculo da Hora Clínica")
        
        despesa_anual = despesa_mensal_media * 12
        
        st.info(f"**Despesa Anual:** R$ {despesa_anual:,.2f}")
        st.success(f"**Despesa Mensal Média:** R$ {despesa_mensal_media:,.2f}")
        st.divider()
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            horas_diarias = st.number_input("Horas Diárias", value=8.0, step=0.5, format="%.1f")
            dias_semana = st.number_input("Dias na semana", value=5.0, step=0.5, format="%.1f")
        with col_p2:
            qtd_salas = st.number_input("Qtd de Salas", value=4.0, step=1.0, format="%.1f")

        horas_semanais = horas_diarias * dias_semana
        horas_mensais = horas_semanais * 4.5
        
        custo_hora_clinica = despesa_mensal_media / horas_mensais if horas_mensais > 0 else 0.0
        custo_dia_clinica = custo_hora_clinica * horas_diarias
        
        custo_hora_atendimento = custo_hora_clinica / qtd_salas if qtd_salas > 0 else 0.0
        custo_dia_atendimento = custo_dia_clinica / qtd_salas if qtd_salas > 0 else 0.0

        st.markdown("#### Índices")
        st.write(f"**Horas Mensais Totais:** {horas_mensais:.1f}h")
        st.write(f"**Custo Hora Clínica:** R$ {custo_hora_clinica:,.2f}")
        st.write(f"**Custo Dia Clínica:** R$ {custo_dia_clinica:,.2f}")
        st.write(f"**Custo Hora Atendimento (por sala):** R$ {custo_hora_atendimento:,.2f}")
        st.write(f"**Custo Dia Atendimento (por sala):** R$ {custo_dia_atendimento:,.2f}")

        with st.expander("ℹ️ Entenda como os índices são calculados"):
            st.markdown("""
            * **Horas Mensais:** `(Horas Diárias x Dias na Semana) x 4,5 semanas`
            * **Custo Hora Clínica:** `Despesa Mensal Média / Horas Mensais`
            * **Custo Dia Clínica:** `Custo Hora Clínica x Horas Diárias`
            * **Custo Hora Atendimento:** `Custo Hora Clínica / Qtd de Salas`
            * **Custo Dia Atendimento:** `Custo Dia Clínica / Qtd de Salas`
            """)

    st.divider()
    
    # -------------------------------------------------------------
    # RESUMO GERAL + GRÁFICO AVANÇADO DE ANÁLISE (PLOTLY)
    # -------------------------------------------------------------
    st.subheader("RESUMO GERAL")
    col_tabela, col_grafico = st.columns([1, 2])
    
    with col_tabela:
        if resumo_dados:
            df_resumo = pd.DataFrame(resumo_dados)
            df_resumo["% de Custo"] = (df_resumo["Média Mensal"] / despesa_mensal_media) if despesa_mensal_media > 0 else 0.0
            st.dataframe(
                df_resumo.style.format({
                    "Média Mensal": "R$ {:,.2f}", 
                    "% de Custo": "{:.1%}"
                }), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.warning("Adicione categorias e valores para ver o resumo geral.")

    with col_grafico:
        dados_grafico = []
        for cat, df_cat in st.session_state["df_custos_categorias"].items():
            total_cat = pd.to_numeric(df_cat["MENSAL (R$)"], errors="coerce").fillna(0.0).sum()
            for _, row in df_cat.iterrows():
                valor = float(row.get("MENSAL (R$)", 0.0))
                if valor > 0:
                    pct_cat = valor / total_cat if total_cat > 0 else 0.0
                    pct_total = valor / despesa_mensal_media if despesa_mensal_media > 0 else 0.0
                    dados_grafico.append({
                        "Categoria": cat,
                        "Subitem": row["ÍTEM"],
                        "Valor (R$)": valor,
                        "% na Categoria": pct_cat,
                        "% no Total": pct_total
                    })

        if dados_grafico:
            df_grafico = pd.DataFrame(dados_grafico)
            df_grafico = df_grafico.sort_values(by="Valor (R$)", ascending=True)

            fig = px.bar(
                df_grafico,
                x="Valor (R$)",
                y="Subitem",
                color="Categoria",
                orientation="h",
                text="Valor (R$)", 
                custom_data=["% na Categoria", "% no Total"],
                title="Despesa Mensal por Subitem"
            )
            
            fig.update_traces(
                texttemplate='R$ %{text:,.2f}', 
                textposition='outside',
                hovertemplate="<b>%{y}</b><br>Valor Mensal: R$ %{x:,.2f}<br>% na Categoria: %{customdata[0]:.1%}<br>% no Total Geral: %{customdata[1]:.1%}<extra></extra>"
            )
            
            altura_grafico = max(400, len(df_grafico) * 35)
            
            fig.update_layout(
                height=altura_grafico,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis_title="",
                xaxis_title="Valor Mensal (R$)",
                legend_title="Categoria",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Preencha valores maiores que zero nas despesas para visualizar o gráfico detalhado.")


# ==========================================
# MÓDULO 3: EQUIPAMENTOS
# ==========================================
def render_equipamentos():
    if "df_lista_equipamentos" not in st.session_state:
        st.session_state["df_lista_equipamentos"] = pd.DataFrame({
            "Nome do equipamento": ["USG PHILLIPS"],
            "Valor de aquisição (R$)": [100000.00], 
            "Tempo de vida útil (anos)": [10.0],
            "Capacidade de Aplicações / dia (R$)": [800.00], 
            "Aplicações (média diária)": [8.0], 
            "Custo anual de manutenção (R$)": [1000.00]
        })

    st.title("Registro de Equipamentos")
    
    st.subheader("⚙️ Gerenciar Equipamentos")
    tab_add, tab_ren, tab_del = st.tabs(["➕ Adicionar", "✏️ Renomear", "🗑️ Excluir"])
    df_eq = st.session_state["df_lista_equipamentos"]
    opcoes_eq = df_eq["Nome do equipamento"].tolist()

    with tab_add:
        with st.form("form_add_eq", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            n_nome = c1.text_input("Nome do Equipamento")
            n_valor = c2.number_input("Valor Aquisição (R$)", min_value=0.0, step=100.0, format="%.2f")
            n_vida = c3.number_input("Vida Útil (Anos)", min_value=1.0, step=1.0, format="%.1f")
            n_cap = c1.number_input("Capacidade de Aplicações / dia (R$)", min_value=0.0, step=10.0, format="%.2f")
            n_apps = c2.number_input("Aplicações (média diária)", min_value=1.0, step=1.0, format="%.1f")
            n_manut = c3.number_input("Manutenção Anual (R$)", min_value=0.0, step=10.0, format="%.2f")
            
            if st.form_submit_button("Adicionar à Lista"):
                if n_nome:
                    novo_df = pd.DataFrame([{
                        "Nome do equipamento": n_nome, 
                        "Valor de aquisição (R$)": float(n_valor),
                        "Tempo de vida útil (anos)": float(n_vida), 
                        "Capacidade de Aplicações / dia (R$)": float(n_cap),
                        "Aplicações (média diária)": float(n_apps), 
                        "Custo anual de manutenção (R$)": float(n_manut)
                    }])
                    st.session_state["df_lista_equipamentos"] = pd.concat([df_eq, novo_df], ignore_index=True)
                    st.rerun()

    with tab_ren:
        c1, c2, c3 = st.columns([2, 2, 1])
        eq_renomear = c1.selectbox("Equipamento atual:", options=opcoes_eq, key="sel_ren_eq")
        novo_nome_eq = c2.text_input("Mudar para:", value=eq_renomear if opcoes_eq else "", key="in_ren_eq")
        st.write("")
        if c3.button("Salvar Nome", use_container_width=True):
            if novo_nome_eq and novo_nome_eq != eq_renomear:
                st.session_state["df_lista_equipamentos"].loc[st.session_state["df_lista_equipamentos"]["Nome do equipamento"] == eq_renomear, "Nome do equipamento"] = novo_nome_eq
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        eq_remover = c1.selectbox("Selecione para remover:", options=opcoes_eq, key="sel_rem_eq")
        st.write("")
        if c2.button("🗑️ Remover Selecionado", use_container_width=True):
            st.session_state["df_lista_equipamentos"] = df_eq[df_eq["Nome do equipamento"] != eq_remover]
            st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODOS", type="primary", use_container_width=True):
            st.session_state["df_lista_equipamentos"] = pd.DataFrame(columns=df_eq.columns)
            st.rerun()

    st.divider()
    dias_uteis = st.number_input("Dias úteis no mês para cálculo:", min_value=1.0, value=22.0, step=1.0, format="%.0f")
    
    df_calc = st.session_state["df_lista_equipamentos"].copy()
    
    # Compatibilidade caso o usuário faça upload de um backup antigo
    if "Capacidade aplicações/dia" in df_calc.columns:
        df_calc.rename(columns={"Capacidade aplicações/dia": "Capacidade de Aplicações / dia (R$)"}, inplace=True)
        st.session_state["df_lista_equipamentos"] = df_calc.copy()

    if not df_calc.empty:
        df_calc["Montante Investido"] = df_calc["Valor de aquisição (R$)"] + (df_calc["Tempo de vida útil (anos)"] * df_calc.get("Custo anual de manutenção (R$)", 0.0))
        df_calc["Depreciação Mensal"] = df_calc.apply(lambda row: row["Montante Investido"] / (row.get("Tempo de vida útil (anos)", 1) * 12) if row.get("Tempo de vida útil (anos)", 0) > 0 else 0, axis=1)
        df_calc["Custo Seção"] = df_calc.apply(lambda row: row["Depreciação Mensal"] / (row.get("Aplicações (média diária)", 1) * dias_uteis) if row.get("Aplicações (média diária)", 0) > 0 else 0, axis=1)
        
        # Formatação bonita da tabela
        formato_tabela = {
            "Valor de aquisição (R$)": "R$ {:,.2f}",
            "Capacidade de Aplicações / dia (R$)": "R$ {:,.2f}",
            "Custo anual de manutenção (R$)": "R$ {:,.2f}",
            "Montante Investido": "R$ {:,.2f}",
            "Depreciação Mensal": "R$ {:,.2f}",
            "Custo Seção": "R$ {:,.2f}"
        }
        st.dataframe(df_calc.style.format(formato_tabela, precision=2), use_container_width=True, hide_index=True)

        with st.expander("ℹ️ Entenda como os índices são calculados"):
            st.markdown("""
            * **Montante Investido:** `Valor de Aquisição + (Vida Útil em Anos x Manutenção Anual)`
            * **Depreciação Mensal:** `Montante Investido / (Vida Útil em Anos x 12 meses)`
            * **Custo por Seção / Aplicação:** `Depreciação Mensal / (Aplicações (média diária) x Dias Úteis no mês)`
            """)

# ==========================================
# MÓDULO 4: INSUMOS
# ==========================================
def render_insumos():
    if "df_lista_insumos" not in st.session_state:
        st.session_state["df_lista_insumos"] = pd.DataFrame({"Material": ["AGULHA"], "qt": [1.0], "valor": [0.56]})

    st.title("Lista de Insumos")
    
    st.subheader("⚙️ Gerenciar Insumos")
    tab_add, tab_ren, tab_del = st.tabs(["➕ Adicionar", "✏️ Renomear", "🗑️ Excluir"])
    df_ins = st.session_state["df_lista_insumos"]
    opcoes_ins = df_ins["Material"].tolist()

    with tab_add:
        with st.form("form_add_ins", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
            n_mat = c1.text_input("Nome do Material")
            n_qt = c2.number_input("Quantidade", min_value=0.01, step=1.0, format="%.2f")
            n_val = c3.number_input("Valor (R$)", min_value=0.0, step=0.10, format="%.3f")
            if c4.form_submit_button("Adicionar"):
                if n_mat:
                    novo_df = pd.DataFrame([{"Material": n_mat, "qt": float(n_qt), "valor": float(n_val)}])
                    st.session_state["df_lista_insumos"] = pd.concat([df_ins, novo_df], ignore_index=True)
                    st.rerun()

    with tab_ren:
        c1, c2, c3 = st.columns([2, 2, 1])
        ins_renomear = c1.selectbox("Insumo atual:", options=opcoes_ins, key="sel_ren_ins")
        novo_nome_ins = c2.text_input("Mudar para:", value=ins_renomear if opcoes_ins else "", key="in_ren_ins")
        st.write("")
        if c3.button("Salvar Nome", use_container_width=True):
            if novo_nome_ins and novo_nome_ins != ins_renomear:
                st.session_state["df_lista_insumos"].loc[st.session_state["df_lista_insumos"]["Material"] == ins_renomear, "Material"] = novo_nome_ins
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        ins_remover = c1.selectbox("Selecione para remover:", options=opcoes_ins, key="sel_rem_ins")
        st.write("")
        if c2.button("🗑️ Remover Selecionado", use_container_width=True):
            st.session_state["df_lista_insumos"] = df_ins[df_ins["Material"] != ins_remover]
            st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODOS", type="primary", use_container_width=True):
            st.session_state["df_lista_insumos"] = pd.DataFrame(columns=df_ins.columns)
            st.rerun()

    st.divider()
    if not df_ins.empty:
        df_show = df_ins.copy()
        df_show["Valor Unitário (R$)"] = df_show["valor"] / df_show["qt"]
        st.dataframe(df_show.style.format({"qt": "{:.2f}", "valor": "R$ {:.3f}", "Valor Unitário (R$)": "R$ {:.3f}"}), use_container_width=True, hide_index=True)

# ==========================================
# MÓDULO 5: TAXAS
# ==========================================
def render_taxas():
    if "df_lista_taxas" not in st.session_state:
        st.session_state["df_lista_taxas"] = pd.DataFrame({"Taxa": ["Débito"], "Porcentagem (%)": [0.80]})

    st.title("Impostos e Taxas")
    
    st.subheader("⚙️ Gerenciar Taxas")
    tab_add, tab_ren, tab_del = st.tabs(["➕ Adicionar", "✏️ Renomear", "🗑️ Excluir"])
    df_taxas = st.session_state["df_lista_taxas"]
    opcoes_taxas = df_taxas["Taxa"].tolist()

    with tab_add:
        with st.form("form_add_taxa", clear_on_submit=True):
            c1, c2, c3 = st.columns([4, 2, 2])
            n_taxa = c1.text_input("Nome da Taxa (Ex: Crédito 2x)")
            n_pct = c2.number_input("Porcentagem (%)", min_value=0.0, step=0.10, format="%.2f")
            if c3.form_submit_button("Adicionar"):
                if n_taxa:
                    novo_df = pd.DataFrame([{"Taxa": n_taxa, "Porcentagem (%)": float(n_pct)}])
                    st.session_state["df_lista_taxas"] = pd.concat([df_taxas, novo_df], ignore_index=True)
                    st.rerun()

    with tab_ren:
        c1, c2, c3 = st.columns([2, 2, 1])
        taxa_renomear = c1.selectbox("Taxa atual:", options=opcoes_taxas, key="sel_ren_taxa")
        novo_nome_taxa = c2.text_input("Mudar para:", value=taxa_renomear if opcoes_taxas else "", key="in_ren_taxa")
        st.write("")
        if c3.button("Salvar Nome", use_container_width=True):
            if novo_nome_taxa and novo_nome_taxa != taxa_renomear:
                st.session_state["df_lista_taxas"].loc[st.session_state["df_lista_taxas"]["Taxa"] == taxa_renomear, "Taxa"] = novo_nome_taxa
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        taxa_remover = c1.selectbox("Remover Taxa:", options=opcoes_taxas, key="sel_rem_taxa")
        st.write("")
        if c2.button("🗑️ Remover", use_container_width=True):
            st.session_state["df_lista_taxas"] = df_taxas[df_taxas["Taxa"] != taxa_remover]
            st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODAS", type="primary", use_container_width=True):
            st.session_state["df_lista_taxas"] = pd.DataFrame(columns=df_taxas.columns)
            st.rerun()

    st.divider()
    if not df_taxas.empty:
        st.dataframe(df_taxas.style.format({"Porcentagem (%)": "{:.2f}%"}), use_container_width=True, hide_index=True)

# ==========================================
# ROTEAMENTO
# ==========================================
if modulo_selecionado == "1. Ficha Técnica (Precificação)": render_ficha_tecnica()
elif modulo_selecionado == "2. Custos Fixos e Hora Clínica": render_custos_fixos()
elif modulo_selecionado == "3. Registro de Equipamentos": render_equipamentos()
elif modulo_selecionado == "4. Insumos e Materiais": render_insumos()
elif modulo_selecionado == "5. Impostos e Taxas": render_taxas()