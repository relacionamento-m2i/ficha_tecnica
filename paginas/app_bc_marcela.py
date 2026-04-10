import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from supabase import create_client, Client
except ImportError:
    st.error("⚠️ A biblioteca 'supabase' não está instalada no ambiente do Streamlit.")
    st.info("Abra o terminal e digite: pipx inject streamlit supabase (ou pip install supabase)")
    st.stop()

# ==========================================
# 1. IDENTIFICAÇÃO DO CLIENTE / ARQUIVO
# ==========================================
ID_CLIENTE = "BC_Marcela" 

# ==========================================
# 2. CONEXÃO COM A NUVEM (SUPABASE)
# ==========================================
@st.cache_resource
def iniciar_conexao():
    try:
        url = st.secrets["supabase"]["URL"]
        key = st.secrets["supabase"]["KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase: Client = iniciar_conexao()

# ==========================================
# 3. FUNÇÕES MÁGICAS DE SINCRONIZAÇÃO
# ==========================================
def salvar_estado_nuvem():
    if supabase:
        dados = {
            "db_servicos": st.session_state.get("db_servicos", {}),
            "df_lista_equipamentos": st.session_state.get("df_lista_equipamentos", pd.DataFrame()).to_dict(orient="records"),
            "df_lista_insumos": st.session_state.get("df_lista_insumos", pd.DataFrame()).to_dict(orient="records"),
            "df_lista_taxas": st.session_state.get("df_lista_taxas", pd.DataFrame()).to_dict(orient="records"),
            "df_custos_categorias": {k: v.to_dict(orient="records") for k, v in st.session_state.get("df_custos_categorias", {}).items()}
        }
        try:
            supabase.table("app_state").upsert({"cliente_id": ID_CLIENTE, "state_data": dados}).execute()
        except Exception as e:
            st.error(f"Erro ao salvar na nuvem: {e}")

def carregar_estado_nuvem():
    if supabase:
        try:
            res = supabase.table("app_state").select("state_data").eq("cliente_id", ID_CLIENTE).execute()
            if res.data:
                dados = res.data[0]["state_data"]
                st.session_state["db_servicos"] = dados.get("db_servicos", {})
                st.session_state["df_lista_equipamentos"] = pd.DataFrame(dados.get("df_lista_equipamentos", []))
                st.session_state["df_lista_insumos"] = pd.DataFrame(dados.get("df_lista_insumos", []))
                st.session_state["df_lista_taxas"] = pd.DataFrame(dados.get("df_lista_taxas", []))

                custos_raw = dados.get("df_custos_categorias", {})
                st.session_state["df_custos_categorias"] = {k: pd.DataFrame(v) for k, v in custos_raw.items()}
                return True
        except Exception as e:
            st.error(f"Erro ao carregar dados da nuvem: {e}")
    return False

# ==========================================
# CONFIGURAÇÕES GERAIS E ESTILOS
# ==========================================
COR_CABECALHO = "#7030A0"
COR_FUNDO_CLARO = "#E6E0EC"
COR_TEXTO_BRANCO = "#FFFFFF"

# CSS Injetado para Deixar os KPIs Profissionais
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-left: 5px solid #7030A0;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 1px solid #f0f0f0;
        border-right: 1px solid #f0f0f0;
        border-bottom: 1px solid #f0f0f0;
    }
    div[data-testid="stMetric"] > div {
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

def df_maquinas_padrao(): return pd.DataFrame(columns=["nome", "custo"])
def df_insumos_padrao(): return pd.DataFrame(columns=["Material", "QT", "Preço (R$)"])

# ==========================================
# INICIALIZAÇÃO DE DADOS (CASO NUVEM VAZIA)
# ==========================================
def inicializar_padroes_caso_vazio():
    lista_novos_servicos = [
        ("Consulta Ginecologista", 800.00), ("Consulta Nutricionista", 350.00), ("Inserção DIU", 1800.00)
    ]
    st.session_state["db_servicos"] = {
        nome: {
            "tempo_min": 60, "maquinas": [], "repasse_fixo": 0.0, "insumos": [],
            "taxas": {"comissao": 0.0, "cartao": 0.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
            "preco_escolhido": preco
        } for nome, preco in lista_novos_servicos
    }

    st.session_state["df_lista_equipamentos"] = pd.DataFrame({
        "Nome do equipamento": ["USG PHILLIPS"], "Valor de aquisição (R$)": [100000.00], 
        "Tempo de vida útil (anos)": [10.0], "Capacidade de Aplicações / dia (R$)": [800.00], 
        "Aplicações (média diária)": [8.0], "Custo anual de manutenção (R$)": [1000.00]
    })

    st.session_state["df_lista_insumos"] = pd.DataFrame([
        ("Seringa 10mL", 1.0, 0.25), ("Luva de Procedimento", 1.0, 0.50), ("Gaze", 1.0, 4.58)
    ], columns=["Material", "qt", "valor"])

    st.session_state["df_lista_taxas"] = pd.DataFrame({"Taxa": ["Débito", "Crédito 1x", "Crédito 3x"], "Porcentagem (%)": [0.80, 1.20, 3.50]})

    st.session_state["df_custos_categorias"] = {
        "1. Despesa com pessoal": pd.DataFrame([{"ÍTEM": "1.1 Total da folha de pagamento", "MENSAL (R$)": 0.0}]),
        "2. Seguros": pd.DataFrame([{"ÍTEM": "2.1 Seguros do estabelecimento", "MENSAL (R$)": 0.0}]),
        "3. Manutenção e conservação": pd.DataFrame([{"ÍTEM": "3.1 Manutenção de equipamentos", "MENSAL (R$)": 0.0}]),
        "4. Despesas estrutura e de consumo": pd.DataFrame([{"ÍTEM": "4.1 Aluguel", "MENSAL (R$)": 0.0}, {"ÍTEM": "4.3 Energia Elétrica", "MENSAL (R$)": 0.0}]),
        "5. Despesas Administrativas e Licenças": pd.DataFrame([{"ÍTEM": "5.1 Contador", "MENSAL (R$)": 0.0}]),
        "6. Despesas com TI": pd.DataFrame([{"ÍTEM": "6.1 Sistemas de gestão", "MENSAL (R$)": 0.0}]),
        "7. Despesas bancárias": pd.DataFrame([{"ÍTEM": "7.1 Taxa administrativa de contas", "MENSAL (R$)": 0.0}]),
        "8. Marketing e vendas": pd.DataFrame([{"ÍTEM": "8.1 Agência", "MENSAL (R$)": 0.0}])
    }
    salvar_estado_nuvem()

if "dados_carregados" not in st.session_state:
    carregou_nuvem = carregar_estado_nuvem()
    if not carregou_nuvem:
        inicializar_padroes_caso_vazio()
    st.session_state["dados_carregados"] = True

if "dias_uteis_eq" not in st.session_state:
    st.session_state["dias_uteis_eq"] = 22.0

def inicializar_estado_ficha():
    lista_nomes_servicos = list(st.session_state.get("db_servicos", {}).keys())
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
    st.session_state.setdefault("df_ficha_maquinas", pd.DataFrame(dados_iniciais.get("maquinas", [])) if dados_iniciais.get("maquinas") else df_maquinas_padrao())
    st.session_state.setdefault("df_ficha_insumos", pd.DataFrame(dados_iniciais.get("insumos", [])) if dados_iniciais.get("insumos") else df_insumos_padrao())
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
    st.session_state["df_ficha_maquinas"] = pd.DataFrame(dados.get("maquinas", [])) if dados.get("maquinas") else df_maquinas_padrao()
    st.session_state["df_ficha_insumos"] = pd.DataFrame(dados.get("insumos", [])) if dados.get("insumos") else df_insumos_padrao()
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
    if supabase:
        st.success(f"☁️ Nuvem Ativa (Cliente: {ID_CLIENTE})")
    else:
        st.warning("⚠️ Rodando Offline")
    st.divider()

# ==========================================
# MÓDULO 1: FICHA TÉCNICA
# ==========================================
def render_ficha_tecnica():
    with st.sidebar:
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
                salvar_estado_nuvem()
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
                salvar_estado_nuvem()
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
                salvar_estado_nuvem()
                st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODOS", type="primary", use_container_width=True):
            st.session_state["db_servicos"] = {}
            st.session_state["servico_atual"] = ""
            salvar_estado_nuvem()
            st.rerun()

    lista_nomes_servicos = list(st.session_state["db_servicos"].keys())
    if not lista_nomes_servicos:
        st.warning("Nenhum serviço cadastrado no banco. Adicione um serviço acima.")
        return

    if "tempo_min" not in st.session_state or st.session_state["servico_atual"] not in lista_nomes_servicos:
        carregar_servico_para_estado(lista_nomes_servicos[0])

    st.markdown("### Selecione o Serviço para Visualizar/Editar:")
    st.selectbox(
        "Filtro", options=lista_nomes_servicos,
        index=lista_nomes_servicos.index(st.session_state["servico_atual"]) if st.session_state["servico_atual"] in lista_nomes_servicos else 0,
        key="combo_servico", on_change=lambda: carregar_servico_para_estado(st.session_state["combo_servico"]),
        label_visibility="collapsed"
    )

    if st.button("💾 Salvar Alterações DESTE SERVIÇO na Nuvem", type="primary"):
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
        salvar_estado_nuvem()
        st.success("Salvo com sucesso na nuvem!")

    st.divider()
    col_esq, col_dir = st.columns([2, 1])

    with col_esq:
        tempo_min = st.number_input("TEMPO de execução (Minutos):", min_value=0.0, step=5.0, format="%.0f", key="tempo_min")
        custo_execucao = (tempo_min / 60) * st.session_state["valor_hora"] if st.session_state["indireto"] == "Sim" else 0.0

        st.markdown("#### Máquinas / Equipamentos no Serviço")
        df_maq = st.session_state["df_ficha_maquinas"]
        if not df_maq.empty:
            st.dataframe(df_maq.style.format({"custo": "R$ {:.2f}"}), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma máquina cadastrada para este serviço.")

        tab_add_m, tab_ren_m, tab_del_m = st.tabs(["➕ Adicionar", "✏️ Editar / Renomear", "🗑️ Excluir"])
        
        with tab_add_m:
            df_eq_global = st.session_state.get("df_lista_equipamentos", pd.DataFrame())
            opcoes_eq = ["-- Digitar Manualmente --"] + df_eq_global["Nome do equipamento"].tolist() if not df_eq_global.empty else ["-- Digitar Manualmente --"]
            sel_eq = st.selectbox("Buscar Equipamento Cadastrado:", opcoes_eq, key="sel_add_maq_ficha")
            
            default_nome_eq = sel_eq if sel_eq != "-- Digitar Manualmente --" else ""
            default_custo_eq = 0.0
            
            if sel_eq != "-- Digitar Manualmente --":
                row = df_eq_global[df_eq_global["Nome do equipamento"] == sel_eq].iloc[0]
                montante = row["Valor de aquisição (R$)"] + (row["Tempo de vida útil (anos)"] * row.get("Custo anual de manutenção (R$)", 0.0))
                dep = montante / (row["Tempo de vida útil (anos)"] * 12) if row["Tempo de vida útil (anos)"] > 0 else 0
                dias_uteis = st.session_state.get("dias_uteis_eq", 22.0)
                default_custo_eq = dep / (row.get("Aplicações (média diária)", 1) * dias_uteis) if row.get("Aplicações (média diária)", 0) > 0 else 0

            with st.form("form_add_maq", clear_on_submit=True):
                c1, c2, c3 = st.columns([4, 2, 2])
                n_nome = c1.text_input("Nome da Máquina", value=default_nome_eq)
                n_custo = c2.number_input("Custo da Seção (R$)", value=float(default_custo_eq), min_value=0.0, step=10.0, format="%.2f")
                if c3.form_submit_button("Adicionar"):
                    if n_nome:
                        novo_reg = pd.DataFrame([{"nome": n_nome, "custo": float(n_custo)}])
                        st.session_state["df_ficha_maquinas"] = pd.concat([df_maq, novo_reg], ignore_index=True)
                        salvar_estado_nuvem()
                        st.rerun()
                        
        with tab_ren_m:
            if not df_maq.empty:
                c1, c2, c3 = st.columns([2, 2, 1])
                maq_renomear = c1.selectbox("Máquina atual:", options=df_maq["nome"].tolist(), key="sel_ren_maq_ficha")
                custo_atual_maq = df_maq[df_maq["nome"] == maq_renomear]["custo"].iloc[0]
                novo_nome_maq = c1.text_input("Mudar nome para:", value=maq_renomear, key="in_ren_maq_ficha")
                novo_custo_maq = c2.number_input("Mudar custo para (R$):", value=float(custo_atual_maq), min_value=0.0, step=10.0, format="%.2f", key="in_ren_custo_maq_ficha")
                
                st.write("")
                if c3.button("Atualizar", key="btn_salvar_maq", use_container_width=True):
                    if novo_nome_maq:
                        idx = df_maq.index[df_maq["nome"] == maq_renomear].tolist()[0]
                        df_maq.at[idx, "nome"] = novo_nome_maq
                        df_maq.at[idx, "custo"] = novo_custo_maq
                        st.session_state["df_ficha_maquinas"] = df_maq
                        salvar_estado_nuvem()
                        st.rerun()

        with tab_del_m:
            if not df_maq.empty:
                c1, c2, c3 = st.columns([2, 1, 1])
                maq_remover = c1.selectbox("Remover máquina:", options=df_maq["nome"].tolist(), key="sel_rem_maq_ficha")
                st.write("")
                if c2.button("🗑️ Remover", key="btn_rem_maq", use_container_width=True):
                    st.session_state["df_ficha_maquinas"] = df_maq[df_maq["nome"] != maq_remover]
                    salvar_estado_nuvem()
                    st.rerun()
                st.write("")
                if c3.button("⚠️ Excluir TODAS", key="btn_rem_todas_maq", type="primary", use_container_width=True):
                    st.session_state["df_ficha_maquinas"] = df_maquinas_padrao()
                    salvar_estado_nuvem()
                    st.rerun()

        custo_maquinas = pd.to_numeric(st.session_state["df_ficha_maquinas"]["custo"], errors="coerce").fillna(0.0).sum() if not st.session_state["df_ficha_maquinas"].empty else 0.0
        
        st.write("")
        custo_aluguel = st.number_input("Aluguel extra de máquina (hora) R$:", min_value=0.0, step=10.0, format="%.2f", key="custo_aluguel")
        repasse_fixo = st.number_input("Repasse para profissionais (Fixo R$):", min_value=0.0, step=10.0, format="%.2f", key="repasse_fixo")
        st.write("")

        st.markdown("#### Materiais e Insumos no Serviço")
        df_ins = st.session_state["df_ficha_insumos"]
        if not df_ins.empty:
            st.dataframe(df_ins.style.format({"QT": "{:.2f}", "Preço (R$)": "R$ {:.3f}"}), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum insumo cadastrado para este serviço.")

        tab_add_i, tab_ren_i, tab_del_i = st.tabs(["➕ Adicionar", "✏️ Editar / Renomear", "🗑️ Excluir"])

        with tab_add_i:
            df_ins_db = st.session_state.get("df_lista_insumos", pd.DataFrame())
            opcoes_ins = ["-- Digitar Manualmente --"] + df_ins_db["Material"].tolist() if not df_ins_db.empty else ["-- Digitar Manualmente --"]
            sel_ins = st.selectbox("Buscar Insumo Cadastrado:", opcoes_ins, key="sel_add_ins_ficha")
            
            default_mat = sel_ins if sel_ins != "-- Digitar Manualmente --" else ""
            default_preco = 0.0
            if sel_ins != "-- Digitar Manualmente --":
                row_ins = df_ins_db[df_ins_db["Material"] == sel_ins].iloc[0]
                qt_base = float(row_ins.get("qt", 1.0))
                qt_base = qt_base if qt_base > 0 else 1.0
                default_preco = float(row_ins.get("valor", 0.0)) / qt_base

            with st.form("form_add_ins_ficha", clear_on_submit=True):
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                n_mat = c1.text_input("Material", value=default_mat)
                n_qt = c2.number_input("Qtd a usar", value=1.00, min_value=0.01, step=1.0)
                n_preco = c3.number_input("Preço Un. (R$)", value=float(default_preco), min_value=0.0, step=0.10, format="%.3f")
                if c4.form_submit_button("Adicionar"):
                    if n_mat:
                        novo_reg = pd.DataFrame([{"Material": n_mat, "QT": float(n_qt), "Preço (R$)": float(n_preco)}])
                        st.session_state["df_ficha_insumos"] = pd.concat([df_ins, novo_reg], ignore_index=True)
                        salvar_estado_nuvem()
                        st.rerun()

        with tab_ren_i:
            if not df_ins.empty:
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                ins_renomear = c1.selectbox("Insumo atual:", options=df_ins["Material"].tolist(), key="sel_ren_ins_ficha")
                row_atual = df_ins[df_ins["Material"] == ins_renomear].iloc[0]
                
                novo_nome_ins = c1.text_input("Mudar nome para:", value=ins_renomear, key="in_ren_ins_ficha")
                nova_qt_ins = c2.number_input("Mudar Qtd:", value=float(row_atual["QT"]), min_value=0.01, step=1.0, key="in_ren_qt_ins")
                novo_preco_ins = c3.number_input("Mudar Preço Un.:", value=float(row_atual["Preço (R$)"]), min_value=0.0, step=0.1, format="%.3f", key="in_ren_pr_ins")
                
                st.write("")
                if c4.button("Atualizar", key="btn_salvar_ins", use_container_width=True):
                    if novo_nome_ins:
                        idx = df_ins.index[df_ins["Material"] == ins_renomear].tolist()[0]
                        df_ins.at[idx, "Material"] = novo_nome_ins
                        df_ins.at[idx, "QT"] = nova_qt_ins
                        df_ins.at[idx, "Preço (R$)"] = novo_preco_ins
                        st.session_state["df_ficha_insumos"] = df_ins
                        salvar_estado_nuvem()
                        st.rerun()

        with tab_del_i:
            if not df_ins.empty:
                c1, c2, c3 = st.columns([2, 1, 1])
                ins_remover = c1.selectbox("Remover insumo:", options=df_ins["Material"].tolist(), key="sel_rem_ins_ficha")
                st.write("")
                if c2.button("🗑️ Remover", key="btn_rem_ins", use_container_width=True):
                    st.session_state["df_ficha_insumos"] = df_ins[df_ins["Material"] != ins_remover]
                    salvar_estado_nuvem()
                    st.rerun()
                st.write("")
                if c3.button("⚠️ Excluir TODOS", key="btn_rem_todos_ins", type="primary", use_container_width=True):
                    st.session_state["df_ficha_insumos"] = df_insumos_padrao()
                    salvar_estado_nuvem()
                    st.rerun()

        if not st.session_state["df_ficha_insumos"].empty:
            custo_insumos = (pd.to_numeric(st.session_state["df_ficha_insumos"]["QT"], errors="coerce").fillna(0.0) * pd.to_numeric(st.session_state["df_ficha_insumos"]["Preço (R$)"], errors="coerce").fillna(0.0)).sum()
        else:
            custo_insumos = 0.0

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
    
    def atualiza_taxa_cartao():
        sel = st.session_state.get("sel_puxar_taxa_cartao")
        if sel != "-- Digitar Manualmente --":
            df_tx = st.session_state.get("df_lista_taxas", pd.DataFrame())
            if not df_tx.empty and sel in df_tx["Taxa"].values:
                val = float(df_tx[df_tx["Taxa"] == sel]["Porcentagem (%)"].iloc[0])
                st.session_state["taxa_cartao"] = val

    df_taxas_globais = st.session_state.get("df_lista_taxas", pd.DataFrame())
    opcoes_taxas = ["-- Digitar Manualmente --"] + df_taxas_globais["Taxa"].tolist() if not df_taxas_globais.empty else ["-- Digitar Manualmente --"]
    
    st.selectbox("Puxar Taxa Cartão da Base de Dados:", opcoes_taxas, key="sel_puxar_taxa_cartao", on_change=atualiza_taxa_cartao)

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
    st.title("Gestão de Custos Fixos e Hora Clínica")
    
    if st.button("💾 Salvar Alterações de Custos na Nuvem", type="primary"):
        salvar_estado_nuvem()
        st.success("Custos sincronizados com a Nuvem com sucesso!")

    def renderizar_categoria_dinamica(titulo, chave):
        with st.expander(titulo, expanded=False):
            df_atual = st.session_state["df_custos_categorias"][titulo]
            registros = df_atual.to_dict('records')

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
                        salvar_estado_nuvem()
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
                        salvar_estado_nuvem()
                        st.rerun()

            total = sum(float(r["MENSAL (R$)"]) for r in registros) if registros else 0.0
            st.markdown(f"**Total da Categoria:** R$ {total:,.2f}")
            return total

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
                salvar_estado_nuvem()
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
                salvar_estado_nuvem()
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        cat_remover = c1.selectbox("Selecione para remover:", options=opcoes_cat, key="sel_rem_cat")
        st.write("")
        if c2.button("🗑️ Remover Selecionada", use_container_width=True):
            if cat_remover in st.session_state["df_custos_categorias"]:
                del st.session_state["df_custos_categorias"][cat_remover]
                salvar_estado_nuvem()
                st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODAS", type="primary", use_container_width=True):
            st.session_state["df_custos_categorias"] = {}
            salvar_estado_nuvem()
            st.rerun()

    st.divider()

    # Processamento dos Dados das Categorias
    st.subheader("📝 Preenchimento de Custos (Expandir Abaixo)")
    despesa_mensal_media = 0.0
    if not st.session_state["df_custos_categorias"]:
        st.info("Nenhuma categoria. Adicione no menu acima.")
    else:
        for i, categoria in enumerate(st.session_state["df_custos_categorias"].keys()):
            tot_cat = renderizar_categoria_dinamica(categoria, f"cat_dyn_{i}")
            despesa_mensal_media += tot_cat

    st.divider()
    st.subheader("⏱️ Configuração da Hora Clínica")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        horas_diarias = st.number_input("Horas Diárias", value=8.0, step=0.5, format="%.1f")
    with col_p2:
        dias_semana = st.number_input("Dias na semana", value=5.0, step=0.5, format="%.1f")
    with col_p3:
        qtd_salas = st.number_input("Qtd de Salas", value=14.0, step=1.0, format="%.1f")

    horas_semanais = horas_diarias * dias_semana
    horas_mensais = horas_semanais * 4.5
    despesa_anual = despesa_mensal_media * 12

    custo_hora_clinica = despesa_mensal_media / horas_mensais if horas_mensais > 0 else 0.0
    custo_dia_clinica = custo_hora_clinica * horas_diarias
    custo_hora_atendimento = custo_hora_clinica / qtd_salas if qtd_salas > 0 else 0.0
    
    st.caption(f"Total de Horas Mensais da Clínica: **{horas_mensais:.1f}h** | Custo Dia Clínica: **R$ {custo_dia_clinica:,.2f}**")

    # ==========================================
    # NOVO DASHBOARD GERAL PROFISSIONAL
    # ==========================================
    st.divider()
    st.markdown(f"<h3 style='color: {COR_CABECALHO};'>📊 DASHBOARD FINANCEIRO E KPIs</h3>", unsafe_allow_html=True)

    # 1. KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Despesa Mensal", f"R$ {despesa_mensal_media:,.2f}")
    kpi2.metric("Despesa Anual", f"R$ {despesa_anual:,.2f}")
    kpi3.metric("Custo Hora Clínica", f"R$ {custo_hora_clinica:,.2f}")
    kpi4.metric("Custo Hora (por Sala)", f"R$ {custo_hora_atendimento:,.2f}")

    st.write("")
    st.write("")

    # 2. Consolidação de Dados
    dados_completos = []
    for cat, df_cat in st.session_state["df_custos_categorias"].items():
        for _, row in df_cat.iterrows():
            valor = float(row.get("MENSAL (R$)", 0.0))
            if valor > 0:
                dados_completos.append({
                    "Categoria": cat,
                    "Subitem": row["ÍTEM"],
                    "Valor (R$)": valor
                })

    if not dados_completos:
        st.warning("Adicione valores nas categorias acima para ver o Dashboard ganhar vida.")
        return

    df_dash = pd.DataFrame(dados_completos)

    # 3. Controles e Filtros
    st.markdown("#### 🔎 Filtros Dinâmicos")
    c_filtro1, c_filtro2 = st.columns([2, 1])
    todas_categorias = sorted(df_dash["Categoria"].unique().tolist())
    
    categorias_selecionadas = c_filtro1.multiselect(
        "Selecione as categorias que deseja visualizar nos gráficos:", 
        options=todas_categorias, 
        default=todas_categorias,
        label_visibility="collapsed"
    )
    
    if not categorias_selecionadas:
        st.info("Nenhuma categoria selecionada.")
        return

    df_filtrado = df_dash[df_dash["Categoria"].isin(categorias_selecionadas)].copy()
    total_filtrado = df_filtrado["Valor (R$)"].sum()
    
    c_filtro2.metric("Total (Categorias Filtradas)", f"R$ {total_filtrado:,.2f}")
    st.write("")

    # 4. Gráficos Plotly Premium
    col_graf1, col_graf2 = st.columns([1, 1.2])
    
    # Paleta de Cores Profissional (Tons de Roxo/Azul)
    paleta_premium = ['#7030A0', '#9b59b6', '#8e44ad', '#2980b9', '#3498db', '#1abc9c', '#16a085', '#27ae60', '#f39c12']

    with col_graf1:
        st.markdown("<h5 style='text-align: center;'>Distribuição Macro</h5>", unsafe_allow_html=True)
        df_agrupado_cat = df_filtrado.groupby("Categoria", as_index=False)["Valor (R$)"].sum()
        
        fig_donut = px.pie(
            df_agrupado_cat, 
            values='Valor (R$)', 
            names='Categoria', 
            hole=0.65,
            color_discrete_sequence=paleta_premium
        )
        fig_donut.update_traces(
            textinfo='percent', 
            hoverinfo='label+percent+value',
            textfont_size=14, 
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )
        fig_donut.update_layout(
            showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            margin=dict(t=20, b=20, l=20, r=20),
            annotations=[dict(text=f"<b>R$ {total_filtrado:,.0f}</b>", x=0.5, y=0.5, font_size=18, showarrow=False)]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_graf2:
        st.markdown("<h5 style='text-align: center;'>Detalhamento por Despesa</h5>", unsafe_allow_html=True)
        df_bar = df_filtrado.sort_values(by="Valor (R$)", ascending=True)
        max_val = df_bar["Valor (R$)"].max()
        
        fig_bar = px.bar(
            df_bar, 
            x="Valor (R$)", 
            y="Subitem", 
            color="Categoria", 
            orientation="h",
            text="Valor (R$)",
            color_discrete_sequence=paleta_premium
        )
        
        # AQUI ESTÁ A CORREÇÃO PRINCIPAL: Margem extra na direita e limite do eixo X forçado
        fig_bar.update_xaxes(range=[0, max_val * 1.35]) 
        
        fig_bar.update_traces(
            texttemplate='<b>R$ %{text:,.2f}</b>', 
            textposition='outside', # Texto fora da barra, mas agora com espaço
            textfont=dict(size=12)
        )
        
        fig_bar.update_layout(
            xaxis_title="", 
            yaxis_title="",
            xaxis=dict(showgrid=True, gridcolor='#e8e8e8', zeroline=False),
            yaxis=dict(showgrid=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=max(350, len(df_bar) * 35), 
            margin=dict(l=10, r=20, t=20, b=10), # Margens limpas
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # 5. Tabela de Dados Escondida (Sanfona)
    with st.expander("📄 Ver Tabela Detalhada", expanded=False):
        df_tabela = df_filtrado.copy()
        df_tabela = df_tabela.sort_values(by="Valor (R$)", ascending=False)
        df_tabela["% do Total Filtrado"] = (df_tabela["Valor (R$)"] / total_filtrado)
        
        st.dataframe(
            df_tabela.style.format({
                "Valor (R$)": "R$ {:,.2f}",
                "% do Total Filtrado": "{:.1%}"
            }),
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# MÓDULO 3: EQUIPAMENTOS
# ==========================================
def render_equipamentos():
    st.title("Registro de Equipamentos")
    
    if st.button("💾 Salvar Alterações de Equip. na Nuvem", type="primary"):
        salvar_estado_nuvem()
        st.success("Equipamentos sincronizados com a Nuvem com sucesso!")

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
                    salvar_estado_nuvem()
                    st.rerun()

    with tab_ren:
        c1, c2, c3 = st.columns([2, 2, 1])
        eq_renomear = c1.selectbox("Equipamento atual:", options=opcoes_eq, key="sel_ren_eq")
        novo_nome_eq = c2.text_input("Mudar para:", value=eq_renomear if opcoes_eq else "", key="in_ren_eq")
        st.write("")
        if c3.button("Salvar Nome", use_container_width=True):
            if novo_nome_eq and novo_nome_eq != eq_renomear:
                st.session_state["df_lista_equipamentos"].loc[st.session_state["df_lista_equipamentos"]["Nome do equipamento"] == eq_renomear, "Nome do equipamento"] = novo_nome_eq
                salvar_estado_nuvem()
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        eq_remover = c1.selectbox("Selecione para remover:", options=opcoes_eq, key="sel_rem_eq")
        st.write("")
        if c2.button("🗑️ Remover Selecionado", use_container_width=True):
            st.session_state["df_lista_equipamentos"] = df_eq[df_eq["Nome do equipamento"] != eq_remover]
            salvar_estado_nuvem()
            st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODOS", type="primary", use_container_width=True):
            st.session_state["df_lista_equipamentos"] = pd.DataFrame(columns=df_eq.columns)
            salvar_estado_nuvem()
            st.rerun()

    st.divider()
    dias_uteis = st.number_input("Dias úteis no mês para cálculo:", min_value=1.0, value=st.session_state["dias_uteis_eq"], step=1.0, format="%.0f")
    st.session_state["dias_uteis_eq"] = dias_uteis

    df_calc = st.session_state["df_lista_equipamentos"].copy()
    if "Capacidade aplicações/dia" in df_calc.columns:
        df_calc.rename(columns={"Capacidade aplicações/dia": "Capacidade de Aplicações / dia (R$)"}, inplace=True)
        st.session_state["df_lista_equipamentos"] = df_calc.copy()

    if not df_calc.empty:
        df_calc["Montante Investido"] = df_calc["Valor de aquisição (R$)"] + (df_calc["Tempo de vida útil (anos)"] * df_calc.get("Custo anual de manutenção (R$)", 0.0))
        df_calc["Depreciação Mensal"] = df_calc.apply(lambda row: row["Montante Investido"] / (row.get("Tempo de vida útil (anos)", 1) * 12) if row.get("Tempo de vida útil (anos)", 0) > 0 else 0, axis=1)
        df_calc["Custo Seção"] = df_calc.apply(lambda row: row["Depreciação Mensal"] / (row.get("Aplicações (média diária)", 1) * dias_uteis) if row.get("Aplicações (média diária)", 0) > 0 else 0, axis=1)
        
        formato_tabela = {
            "Valor de aquisição (R$)": "R$ {:,.2f}", "Capacidade de Aplicações / dia (R$)": "R$ {:,.2f}",
            "Custo anual de manutenção (R$)": "R$ {:,.2f}", "Montante Investido": "R$ {:,.2f}",
            "Depreciação Mensal": "R$ {:,.2f}", "Custo Seção": "R$ {:,.2f}"
        }
        st.dataframe(df_calc.style.format(formato_tabela, precision=2), use_container_width=True, hide_index=True)

# ==========================================
# MÓDULO 4: INSUMOS
# ==========================================
def render_insumos():
    st.title("Lista de Insumos e Materiais")
    
    if st.button("💾 Salvar Alterações de Insumos na Nuvem", type="primary"):
        salvar_estado_nuvem()
        st.success("Insumos sincronizados com a Nuvem com sucesso!")

    st.subheader("⚙️ Gerenciar Insumos")
    
    tab_add, tab_ren, tab_del = st.tabs(["➕ Adicionar", "✏️ Renomear", "🗑️ Excluir"])
    df_ins = st.session_state["df_lista_insumos"]
    opcoes_ins = df_ins["Material"].tolist()

    with tab_add:
        with st.form("form_add_ins_mod", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
            n_mat = c1.text_input("Nome do Material")
            n_qt = c2.number_input("Quantidade (Embalagem)", min_value=0.01, step=1.0, format="%.2f")
            n_val = c3.number_input("Valor (R$)", min_value=0.0, step=0.10, format="%.3f")
            if c4.form_submit_button("Adicionar"):
                if n_mat:
                    novo_df = pd.DataFrame([{"Material": n_mat, "qt": float(n_qt), "valor": float(n_val)}])
                    st.session_state["df_lista_insumos"] = pd.concat([df_ins, novo_df], ignore_index=True)
                    salvar_estado_nuvem()
                    st.rerun()

    with tab_ren:
        c1, c2, c3 = st.columns([2, 2, 1])
        ins_renomear = c1.selectbox("Insumo atual:", options=opcoes_ins, key="sel_ren_ins")
        novo_nome_ins = c2.text_input("Mudar para:", value=ins_renomear if opcoes_ins else "", key="in_ren_ins")
        st.write("")
        if c3.button("Salvar Nome", use_container_width=True):
            if novo_nome_ins and novo_nome_ins != ins_renomear:
                st.session_state["df_lista_insumos"].loc[st.session_state["df_lista_insumos"]["Material"] == ins_renomear, "Material"] = novo_nome_ins
                salvar_estado_nuvem()
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        ins_remover = c1.selectbox("Selecione para remover:", options=opcoes_ins, key="sel_rem_ins")
        st.write("")
        if c2.button("🗑️ Remover Selecionado", use_container_width=True):
            st.session_state["df_lista_insumos"] = df_ins[df_ins["Material"] != ins_remover]
            salvar_estado_nuvem()
            st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODOS", type="primary", use_container_width=True):
            st.session_state["df_lista_insumos"] = pd.DataFrame(columns=df_ins.columns)
            salvar_estado_nuvem()
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
    st.title("Impostos e Taxas")
    
    if st.button("💾 Salvar Alterações de Taxas na Nuvem", type="primary"):
        salvar_estado_nuvem()
        st.success("Taxas sincronizadas com a Nuvem com sucesso!")

    st.subheader("⚙️ Gerenciar Taxas")
    
    tab_add, tab_ren, tab_del = st.tabs(["➕ Adicionar", "✏️ Renomear", "🗑️ Excluir"])
    df_taxas = st.session_state["df_lista_taxas"]
    opcoes_taxas = df_taxas["Taxa"].tolist()

    with tab_add:
        with st.form("form_add_taxa_mod", clear_on_submit=True):
            c1, c2, c3 = st.columns([4, 2, 2])
            n_taxa = c1.text_input("Nome da Taxa (Ex: Crédito 2x)")
            n_pct = c2.number_input("Porcentagem (%)", min_value=0.0, step=0.10, format="%.2f")
            if c3.form_submit_button("Adicionar"):
                if n_taxa:
                    novo_df = pd.DataFrame([{"Taxa": n_taxa, "Porcentagem (%)": float(n_pct)}])
                    st.session_state["df_lista_taxas"] = pd.concat([df_taxas, novo_df], ignore_index=True)
                    salvar_estado_nuvem()
                    st.rerun()

    with tab_ren:
        c1, c2, c3 = st.columns([2, 2, 1])
        taxa_renomear = c1.selectbox("Taxa atual:", options=opcoes_taxas, key="sel_ren_taxa")
        novo_nome_taxa = c2.text_input("Mudar para:", value=taxa_renomear if opcoes_taxas else "", key="in_ren_taxa")
        st.write("")
        if c3.button("Salvar Nome", use_container_width=True):
            if novo_nome_taxa and novo_nome_taxa != taxa_renomear:
                st.session_state["df_lista_taxas"].loc[st.session_state["df_lista_taxas"]["Taxa"] == taxa_renomear, "Taxa"] = novo_nome_taxa
                salvar_estado_nuvem()
                st.rerun()

    with tab_del:
        c1, c2, c3 = st.columns([2, 1, 1])
        taxa_remover = c1.selectbox("Remover Taxa:", options=opcoes_taxas, key="sel_rem_taxa")
        st.write("")
        if c2.button("🗑️ Remover", use_container_width=True):
            st.session_state["df_lista_taxas"] = df_taxas[df_taxas["Taxa"] != taxa_remover]
            salvar_estado_nuvem()
            st.rerun()
        st.write("")
        if c3.button("⚠️ Excluir TODAS", type="primary", use_container_width=True):
            st.session_state["df_lista_taxas"] = pd.DataFrame(columns=df_taxas.columns)
            salvar_estado_nuvem()
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