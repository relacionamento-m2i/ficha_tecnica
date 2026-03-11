import streamlit as st
import pandas as pd
import json
from banco_servicos import obter_servicos_cadastrados

# O set_page_config deve ser sempre a primeira instrução e só pode ser chamado uma vez
st.set_page_config(page_title="Sistema Integrado de Precificação", layout="wide")

# ==========================================
# CONFIGURAÇÕES GERAIS E ESTILOS
# ==========================================
COR_CABECALHO = "#7030A0"
COR_FUNDO_CLARO = "#E6E0EC"
COR_TEXTO_BRANCO = "#FFFFFF"

# Menu Lateral de Navegação
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
    db_servicos = obter_servicos_cadastrados()
    lista_nomes_servicos = list(db_servicos.keys())

    def carregar_servico_para_estado(nome_servico):
        dados = db_servicos[nome_servico]
        st.session_state['servico_atual'] = nome_servico
        st.session_state['tempo_min'] = dados['tempo_min']
        st.session_state['repasse_fixo'] = dados['repasse_fixo']
        st.session_state['df_ficha_maquinas'] = pd.DataFrame(dados['maquinas']) if dados['maquinas'] else pd.DataFrame({"nome": [""], "custo": [0.0]})
        st.session_state['df_ficha_insumos'] = pd.DataFrame(dados['insumos']) if dados['insumos'] else pd.DataFrame({"Material": [""], "QT": [0], "Preço (R$)": [0.0]})
        st.session_state['taxa_comissao'] = float(dados['taxas']['comissao'])
        st.session_state['taxa_cartao'] = float(dados['taxas']['cartao'])
        st.session_state['taxa_imposto'] = float(dados['taxas']['imposto'])
        st.session_state['preco_escolhido'] = float(dados['preco_escolhido'])
        
        if 'custo_aluguel' not in st.session_state: st.session_state['custo_aluguel'] = 0.0
        if 'indireto' not in st.session_state: st.session_state['indireto'] = "Sim"
        if 'valor_hora' not in st.session_state: st.session_state['valor_hora'] = 48.14

    if 'servico_atual' not in st.session_state:
        carregar_servico_para_estado(lista_nomes_servicos[0])

    with st.sidebar:
        st.header("💾 Salvar / Carregar Ficha")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_ficha")
        if arquivo_upload is not None:
            try:
                dados_json = json.load(arquivo_upload)
                for k, v in dados_json.items():
                    if k in ['df_ficha_maquinas', 'df_ficha_insumos']:
                        st.session_state[k] = pd.DataFrame(v)
                    else:
                        st.session_state[k] = v
                st.success("Ficha carregada com sucesso!")
            except Exception:
                st.error("Erro ao ler o arquivo.")

        st.divider()

        dados_para_salvar = {
            'servico_atual': st.session_state['servico_atual'],
            'tempo_min': st.session_state['tempo_min'],
            'repasse_fixo': st.session_state['repasse_fixo'],
            'df_ficha_maquinas': st.session_state['df_ficha_maquinas'].to_dict(orient='records'),
            'df_ficha_insumos': st.session_state['df_ficha_insumos'].to_dict(orient='records'),
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
        st.selectbox("Com Custo Indireto?", ["Sim", "Não"], key='indireto')
        st.number_input("Valor da Hora Clínica (R$)", step=1.0, key='valor_hora')

    st.markdown(f"""
    <div style="background-color: {COR_CABECALHO}; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
        <h2 style="margin: 0; color: {COR_TEXTO_BRANCO};">PORTAL DE PRECIFICAÇÃO CLÍNICA</h2>
    </div>
    """, unsafe_allow_html=True)

    def mudou_servico():
        carregar_servico_para_estado(st.session_state['combo_servico'])

    st.markdown("### Selecione o Serviço para análise:")
    st.selectbox(
        "Filtro de Serviços", 
        options=lista_nomes_servicos,
        index=lista_nomes_servicos.index(st.session_state['servico_atual']) if st.session_state['servico_atual'] in lista_nomes_servicos else 0,
        key='combo_servico',
        on_change=mudou_servico,
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown(f"#### Ficha Técnica: **{st.session_state['servico_atual']}**")

    col_esq, col_dir = st.columns([2, 1])

    with col_esq:
        tempo_min = st.number_input("2. TEMPO de execução (Minutos):", step=5, key='tempo_min')
        custo_execucao = (tempo_min / 60) * st.session_state['valor_hora'] if st.session_state['indireto'] == "Sim" else 0.0
        
        st.markdown("**3. Uso de máquina / equipamento**")
        df_maq = st.data_editor(st.session_state['df_ficha_maquinas'], num_rows="dynamic", use_container_width=True, hide_index=True)
        st.session_state['df_ficha_maquinas'] = df_maq
        custo_maquinas = df_maq["custo"].sum() if not df_maq.empty and "custo" in df_maq else 0.0

        custo_aluguel = st.number_input("4. Aluguel de máquina (hora) R$:", step=10.0, key='custo_aluguel')
        repasse_fixo = st.number_input("5. Repasse para profissionais (Fixo R$):", step=10.0, key='repasse_fixo')

        st.markdown("**6. Custo materiais e insumos**")
        df_ins = st.data_editor(st.session_state['df_ficha_insumos'], num_rows="dynamic", use_container_width=True, hide_index=True)
        st.session_state['df_ficha_insumos'] = df_ins
        
        if not df_ins.empty and "QT" in df_ins and "Preço (R$)" in df_ins:
            df_ins["Total Linha"] = pd.to_numeric(df_ins["QT"], errors='coerce').fillna(0) * pd.to_numeric(df_ins["Preço (R$)"], errors='coerce').fillna(0)
            custo_insumos = df_ins["Total Linha"].sum()
        else:
            custo_insumos = 0.0

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
    st.markdown("#### Taxas e Precificação")

    col_t1, col_t2, col_t3 = st.columns(3)
    taxa_comissao = col_t1.number_input("COMISSÃO (%)", key='taxa_comissao') / 100
    taxa_cartao = col_t2.number_input("TAXA CARTÃO (%)", key='taxa_cartao') / 100
    taxa_imposto = col_t3.number_input("IMPOSTO (%)", key='taxa_imposto') / 100

    st.write("")
    preco_escolhido = st.number_input("PREÇO DE TABELA ESCOLHIDO (R$)", step=10.0, key='preco_escolhido')

    comissao = preco_escolhido * taxa_comissao
    cartao = preco_escolhido * taxa_cartao
    imposto = preco_escolhido * taxa_imposto
    liquido = preco_escolhido - comissao - cartao - imposto
    lucro = liquido - custo_total_servico
    pct_lucro = (lucro / preco_escolhido) if preco_escolhido > 0 else 0.0

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


# ==========================================
# MÓDULO 2: CUSTOS FIXOS
# ==========================================
def render_custos_fixos():
    def renderizar_categoria(titulo, itens_dict, chave_base):
        with st.expander(titulo, expanded=False):
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.markdown("**ÍTEM**")
            col2.markdown("**MENSAL**")
            col3.markdown("**ANUAL**")
            st.markdown("<hr style='margin: 0px; padding: 0px;'>", unsafe_allow_html=True)
            
            total_mensal = 0.0
            for idx, (nome_item, valor_padrao) in enumerate(itens_dict.items()):
                chave_input = f"{chave_base}_{idx}"
                if chave_input not in st.session_state:
                    st.session_state[chave_input] = float(valor_padrao)
                    
                c1, c2, c3 = st.columns([3, 2, 2])
                with c1: st.markdown(f"<div style='margin-top: 8px;'>{nome_item}</div>", unsafe_allow_html=True)
                with c2:
                    val = st.number_input(nome_item, step=50.0, key=chave_input, label_visibility="collapsed")
                    total_mensal += val
                with c3: st.markdown(f"<div style='margin-top: 8px;'>R$ {val * 12:,.2f}</div>", unsafe_allow_html=True)
                    
            st.markdown("<hr style='margin: 0px; padding: 0px;'>", unsafe_allow_html=True)
            ct1, ct2, ct3 = st.columns([3, 2, 2])
            ct1.markdown("**Total**")
            ct2.markdown(f"**R$ {total_mensal:,.2f}**")
            ct3.markdown(f"**R$ {total_mensal * 12:,.2f}**")
            return total_mensal

    with st.sidebar:
        st.header("💾 Salvar / Carregar Dados")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_custos")
        if arquivo_upload is not None:
            try:
                dados_salvos = json.load(arquivo_upload)
                for chave, valor in dados_salvos.items():
                    st.session_state[chave] = float(valor)
                st.success("Dados carregados com sucesso!")
            except Exception:
                st.error("Erro ao ler o arquivo.")

        st.divider()
        dados_para_salvar = {k: v for k, v in st.session_state.items() if k.startswith("cat_") or k.startswith("param_")}
        st.download_button(
            label="📥 Baixar Cenário Atual",
            data=json.dumps(dados_para_salvar, indent=4),
            file_name="meus_custos_clinica.json",
            mime="application/json"
        )

    st.title("Gestão de Custos Fixos e Hora Clínica")

    col_inputs, col_dashboard = st.columns([1.8, 1])

    with col_inputs:
        st.subheader("Lançamento de Despesas")
        
        total_1 = renderizar_categoria("1. Despesa com pessoal", {"1.1 Total da folha": 10263.00, "1.4 Pro-labore": 1500.00, "1.5 Milena": 4500.00, "1.7 INSS": 2839.04, "1.8 FGTS": 765.46, "1.9 Uniformes": 115.92}, "cat_1")
        total_2 = renderizar_categoria("2. Seguros", {"2.2 Seguro médico": 486.00}, "cat_2")
        total_3 = renderizar_categoria("3. Manutenção e conservação", {"3.2 Manutenção do prédio": 416.67, "3.3 Coleta de lixo": 60.00, "3.4 Manutenção equipamentos": 175.00, "3.9 Outras": 100.00}, "cat_3")
        total_4 = renderizar_categoria("4. Despesas estrutura e de consumo", {"4.1 Aluguel": 5232.26, "4.3 Energia": 1000.00, "4.5 Telefones": 90.00, "4.6 Internet": 204.04, "4.7 Faxina": 600.00, "4.8 Material limpeza": 100.00, "4.9 Copa": 150.00, "4.10 Escritório": 173.03, "4.12 Cartografia": 389.98}, "cat_4")
        total_5 = renderizar_categoria("5. Despesas Administrativas e Licenças", {"5.1 Contador": 800.00, "5.2 Jader SDM": 1000.00, "5.3 Entidades": 161.19, "5.4 Licenças": 407.11, "5.5 Outras admin": 25.00}, "cat_5")
        total_6 = renderizar_categoria("6. Despesas com TI", {"6.1 Sistemas": 1005.74, "6.3 Chat bot": 270.00}, "cat_6")
        total_7 = renderizar_categoria("7. Despesas bancárias", {"7.1 Taxa admin contas": 94.73, "7.4 Outras": 2.37}, "cat_7")
        total_8 = renderizar_categoria("8. Marketing e vendas", {"8.2 Eventos": 4723.33, "8.3 Social mídia": 1300.00, "8.4 Tráfego Pago": 1800.00, "8.5 Patrocínio": 1000.00, "8.7 Outras": 1706.67}, "cat_8")

    custo_fixo_mensal = total_1 + total_2 + total_3 + total_4 + total_5 + total_6 + total_7 + total_8

    with col_dashboard:
        st.subheader("Cálculo da Hora Clínica")
        st.info(f"**Despesa Anual:** R$ {custo_fixo_mensal*12:,.2f}")
        st.success(f"**Custo Fixo Mensal:** R$ {custo_fixo_mensal:,.2f}")
        st.divider()
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if "param_horas" not in st.session_state: st.session_state["param_horas"] = 8.0
            if "param_dias" not in st.session_state: st.session_state["param_dias"] = 5.0
            horas_diarias = st.number_input("Horas Diárias", key="param_horas")
            dias_semana = st.number_input("Dias na semana", key="param_dias")
        with col_p2:
            if "param_salas" not in st.session_state: st.session_state["param_salas"] = 4.0
            if "param_mes" not in st.session_state: st.session_state["param_mes"] = 180.0
            qtd_salas = st.number_input("Qtd de Salas", key="param_salas")
            horas_mensais = st.number_input("Horas Mensais", key="param_mes")

        dias_mensais = horas_mensais / horas_diarias if horas_diarias > 0 else 22.5
        custo_hora_clinica = custo_fixo_mensal / horas_mensais if horas_mensais > 0 else 0
        
        st.markdown("#### Índices")
        st.write(f"**Custo Hora Clínica:** R$ {custo_hora_clinica:,.2f}")
        st.write(f"**Custo Hora (Sala):** R$ {(custo_hora_clinica / qtd_salas if qtd_salas > 0 else 0):,.2f}")

    st.divider()
    st.subheader("RESUMO GERAL")
    df_resumo = pd.DataFrame({
        "RESUMO": ["1. Despesa com pessoal", "2. Seguros", "3. Manutenção", "4. Estrutura", "5. Admin/Licenças", "6. TI", "7. Bancárias", "8. Marketing"],
        "Média Mensal": [total_1, total_2, total_3, total_4, total_5, total_6, total_7, total_8]
    })
    df_resumo["% Custo"] = (df_resumo["Média Mensal"] / custo_fixo_mensal) if custo_fixo_mensal > 0 else 0
    st.dataframe(df_resumo.style.format({"Média Mensal": "R$ {:,.2f}", "% Custo": "{:.0%}"}), use_container_width=True, hide_index=True)


# ==========================================
# MÓDULO 3: EQUIPAMENTOS
# ==========================================
def render_equipamentos():
    def carregar_dados_eq():
        return pd.DataFrame({
            "Nome do equipamento": ["BOMBA PNEUMÁTICA", "USG PHILLIPS CLEARVUE", "MONITOR MULTIPARAMÉTRICO"],
            "Data de Aquisição": ["01/01/2024", "01/01/2025", "06/01/2025"],
            "Valor de aquisição (R$)": [5500.0, 100000.0, 5500.0],
            "Tempo de vida útil (anos)": [5, 10, 10],
            "Capacidade aplicações/dia": [8.0, 8.0, 8.0],
            "Aplicações (média diária)": [1.0, 8.0, 4.0],
            "Custo anual de manutenção (R$)": [0.0, 1000.0, 0.0]
        })

    if "df_lista_equipamentos" not in st.session_state:
        st.session_state["df_lista_equipamentos"] = carregar_dados_eq()

    with st.sidebar:
        st.header("💾 Salvar / Carregar")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_eq")
        if arquivo_upload is not None:
            try:
                st.session_state["df_lista_equipamentos"] = pd.DataFrame(json.load(arquivo_upload))
                st.success("Dados carregados!")
            except Exception:
                st.error("Erro ao ler arquivo.")
        st.divider()
        st.download_button(
            label="📥 Baixar Tabela",
            data=st.session_state["df_lista_equipamentos"].to_json(orient="records", indent=4),
            file_name="equipamentos_clinica.json",
            mime="application/json"
        )

    st.title("Registro e Depreciação de Equipamentos")
    dias_uteis = st.number_input("Dias úteis no mês:", min_value=1, value=22, step=1)

    df_editado = st.data_editor(st.session_state["df_lista_equipamentos"], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state["df_lista_equipamentos"] = df_editado.copy()

    df_calc = df_editado.copy().fillna(0)
    if "Tempo de vida útil (anos)" in df_calc.columns and "Valor de aquisição (R$)" in df_calc.columns:
        df_calc["Montante Investido (R$)"] = df_calc["Valor de aquisição (R$)"] + (df_calc["Tempo de vida útil (anos)"] * df_calc["Custo anual de manutenção (R$)"])
        df_calc["Depreciação Mensal (R$)"] = df_calc.apply(lambda row: row["Montante Investido (R$)"] / (row["Tempo de vida útil (anos)"] * 12) if row["Tempo de vida útil (anos)"] > 0 else 0, axis=1)
        df_calc["Custo Seção (R$)"] = df_calc.apply(lambda row: row["Depreciação Mensal (R$)"] / (row["Aplicações (média diária)"] * dias_uteis) if row["Aplicações (média diária)"] > 0 else 0, axis=1)

        st.subheader("Resultados Consolidados")
        st.dataframe(df_calc[["Nome do equipamento", "Valor de aquisição (R$)", "Montante Investido (R$)", "Depreciação Mensal (R$)", "Custo Seção (R$)"]].style.format({"Valor de aquisição (R$)": "R$ {:,.2f}", "Montante Investido (R$)": "R$ {:,.2f}", "Depreciação Mensal (R$)": "R$ {:,.2f}", "Custo Seção (R$)": "R$ {:,.2f}"}), use_container_width=True, hide_index=True)


# ==========================================
# MÓDULO 4: INSUMOS
# ==========================================
def render_insumos():
    def carregar_dados_in():
        return pd.DataFrame({
            "Material": ["ADRENALINA", "ÁGUA OXIGENADA - ( mL)", "AGULHA 0,40x12"],
            "qt": [1.0, 1.0, 1.0],
            "valor": [1.30, 0.008, 0.56]
        })

    if "df_lista_insumos" not in st.session_state:
        st.session_state["df_lista_insumos"] = carregar_dados_in()

    with st.sidebar:
        st.header("💾 Salvar / Carregar")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_in")
        if arquivo_upload is not None:
            try:
                st.session_state["df_lista_insumos"] = pd.DataFrame(json.load(arquivo_upload))
                st.success("Lista carregada!")
            except Exception:
                st.error("Erro ao ler arquivo.")
        st.divider()
        st.download_button(
            label="📥 Baixar Lista",
            data=st.session_state["df_lista_insumos"].to_json(orient="records", indent=4),
            file_name="lista_insumos_clinica.json",
            mime="application/json"
        )

    st.markdown("<h2 style='color: #6A329F;'>LISTA DE INSUMOS E MATERIAIS</h2>", unsafe_allow_html=True)
    
    df_atual = st.session_state["df_lista_insumos"].copy()
    df_atual["qt"] = df_atual["qt"].apply(lambda x: x if x > 0 else 1.0) 
    df_atual["valor unitário"] = df_atual["valor"] / df_atual["qt"]

    df_editado = st.data_editor(
        df_atual, num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "qt": st.column_config.NumberColumn("qt", min_value=0.01, step=1.0),
            "valor": st.column_config.NumberColumn("valor (R$)", min_value=0.0, step=0.5, format="R$ %.3f"),
            "valor unitário": st.column_config.NumberColumn("valor unitário (R$)", disabled=True, format="R$ %.3f")
        }
    )
    st.session_state["df_lista_insumos"] = df_editado[["Material", "qt", "valor"]].copy()


# ==========================================
# MÓDULO 5: TAXAS
# ==========================================
def render_taxas():
    if "aliquota_imposto" not in st.session_state: st.session_state["aliquota_imposto"] = 12.00
    if "df_lista_taxas" not in st.session_state:
        st.session_state["df_lista_taxas"] = pd.DataFrame({
            "Taxas aplicadas": ["PIX Pessoa Física", "PIX Pessoa Jurídica", "Débito", "Crédito à vista", "Parcelado de 2x a 6x"],
            "Sobre o (%)": [0.0, 0.0, 0.8, 0.9, 2.5]
        })

    with st.sidebar:
        st.header("💾 Salvar / Carregar")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_taxas")
        if arquivo_upload is not None:
            try:
                dados_json = json.load(arquivo_upload)
                st.session_state["aliquota_imposto"] = float(dados_json.get("aliquota_imposto", 12.0))
                st.session_state["df_lista_taxas"] = pd.DataFrame(dados_json.get("df_lista_taxas", []))
                st.success("Dados carregados!")
            except Exception:
                st.error("Erro ao ler arquivo.")
        st.divider()
        st.download_button(
            label="📥 Baixar Taxas",
            data=json.dumps({"aliquota_imposto": st.session_state["aliquota_imposto"], "df_lista_taxas": st.session_state["df_lista_taxas"].to_dict(orient="records")}, indent=4),
            file_name="impostos_e_taxas.json",
            mime="application/json"
        )

    st.markdown("<div style='background-color: #A30000; padding: 10px; border-radius: 5px; color: white;'><h3 style='margin: 0; color: white;'>3. Impostos e taxas</h3></div><br>", unsafe_allow_html=True)
    
    col_centro, _, _ = st.columns([2, 1, 1])
    with col_centro:
        st.markdown("#### 1. Alíquota de imposto da empresa (%)")
        st.session_state["aliquota_imposto"] = st.number_input("Alíquota (%)", value=st.session_state["aliquota_imposto"], min_value=0.0, step=0.5, format="%.2f", label_visibility="collapsed")
        
        st.divider()
        st.markdown("#### 2. Tarifas bancárias para vendas")
        df_editado = st.data_editor(
            st.session_state["df_lista_taxas"], hide_index=True, use_container_width=True,
            column_config={
                "Taxas aplicadas": st.column_config.TextColumn("Taxas aplicadas", disabled=True),
                "Sobre o (%)": st.column_config.NumberColumn("Sobre o (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f %%")
            }
        )
        st.session_state["df_lista_taxas"] = df_editado.copy()


# ==========================================
# ROTEAMENTO DAS PÁGINAS (CONTROLE DO MENU)
# ==========================================
if modulo_selecionado == "1. Ficha Técnica (Precificação)":
    render_ficha_tecnica()
elif modulo_selecionado == "2. Custos Fixos e Hora Clínica":
    render_custos_fixos()
elif modulo_selecionado == "3. Registro de Equipamentos":
    render_equipamentos()
elif modulo_selecionado == "4. Insumos e Materiais":
    render_insumos()
elif modulo_selecionado == "5. Impostos e Taxas":
    render_taxas()