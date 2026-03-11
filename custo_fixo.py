import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Gestão de Custos Fixos - Clínica", layout="wide")

# --- FUNÇÃO AUXILIAR PARA RENDERIZAR E GERENCIAR A MEMÓRIA (SESSION STATE) ---
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
            
            # Se a chave não existir na memória, cria com o valor padrão
            if chave_input not in st.session_state:
                st.session_state[chave_input] = float(valor_padrao)
                
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.markdown(f"<div style='margin-top: 8px;'>{nome_item}</div>", unsafe_allow_html=True)
            with c2:
                # O input agora está amarrado ao session_state através da 'key'
                val = st.number_input(
                    nome_item, 
                    step=50.0, 
                    key=chave_input, 
                    label_visibility="collapsed"
                )
                total_mensal += val
            with c3:
                st.markdown(f"<div style='margin-top: 8px;'>R$ {val * 12:,.2f}</div>", unsafe_allow_html=True)
                
        st.markdown("<hr style='margin: 0px; padding: 0px;'>", unsafe_allow_html=True)
        ct1, ct2, ct3 = st.columns([3, 2, 2])
        ct1.markdown("**Total**")
        ct2.markdown(f"**R$ {total_mensal:,.2f}**")
        ct3.markdown(f"**R$ {total_mensal * 12:,.2f}**")
        
        return total_mensal

# --- BARRA LATERAL: SISTEMA DE SALVAR / CARREGAR ---
with st.sidebar:
    st.header("💾 Salvar / Carregar Dados")
    st.write("Como a nuvem não salva os dados ao atualizar a página, você pode baixar o seu cenário e carregar depois.")
    
    # 1. Carregar Dados (Upload)
    arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"])
    if arquivo_upload is not None:
        try:
            dados_salvos = json.load(arquivo_upload)
            for chave, valor in dados_salvos.items():
                st.session_state[chave] = float(valor)
            st.success("Dados carregados com sucesso! A página já foi atualizada.")
        except Exception as e:
            st.error("Erro ao ler o arquivo.")

    st.divider()

    # 2. Salvar Dados (Download)
    # Pega tudo que é input nosso (começa com cat_ ou param_) para salvar
    dados_para_salvar = {k: v for k, v in st.session_state.items() if k.startswith("cat_") or k.startswith("param_")}
    json_string = json.dumps(dados_para_salvar, indent=4)
    
    st.download_button(
        label="📥 Baixar Cenário Atual",
        data=json_string,
        file_name="meus_custos_clinica.json",
        mime="application/json"
    )

st.title("Gestão de Custos Fixos e Hora Clínica")

# --- LAYOUT PRINCIPAL ---
col_inputs, col_dashboard = st.columns([1.8, 1])

# --- COLUNA DE INPUTS ---
with col_inputs:
    st.subheader("Lançamento de Despesas")
    
    itens_pessoal = {
        "1.1 Total da folha de pagamento (adm + recepção)": 10263.00, "1.2 Despesas com alimentação e transporte": 0.00,
        "1.3 Reserva para rescisões": 0.00, "1.4 Pro-labore": 1500.00, "1.5 Milena": 4500.00,
        "1.6 Gratificações": 0.00, "1.7 INSS": 2839.04, "1.8 FGTS": 765.46, "1.9 Uniformes": 115.92
    }
    total_1 = renderizar_categoria("1. Despesa com pessoal", itens_pessoal, "cat_1")

    itens_seguros = {"2.1 Seguros do estabelecimento": 0.00, "2.2 Seguro médico": 486.00, "2.3 Outros seguros": 0.00}
    total_2 = renderizar_categoria("2. Seguros", itens_seguros, "cat_2")

    itens_manutencao = {
        "3.1 Elevadores": 0.00, "3.2 Manutenção do prédio": 416.67, "3.3 Coleta de lixo hospitalar": 60.00,
        "3.4 Manutenção de equipamentos (ar cond.)": 175.00, "3.5 Pinturas": 0.00, "3.6 Jardins": 0.00,
        "3.7 Extintores": 0.00, "3.8 Reserva compra equipamentos (depreciação)": 0.00, "3.9 Outras despesas": 100.00
    }
    total_3 = renderizar_categoria("3. Manutenção e conservação", itens_manutencao, "cat_3")

    itens_estrutura = {
        "4.1 Aluguel": 5232.26, "4.2 Condomínio": 0.00, "4.3 Energia Elétrica": 1000.00,
        "4.4 Água": 0.00, "4.5 Telefones/Interfones": 90.00, "4.6 Internet": 204.04,
        "4.7 Faxina": 600.00, "4.8 Material de limpeza": 100.00, "4.9 Material para copa": 150.00,
        "4.10 Material de escritório": 173.03, "4.11 IPTU": 0.00, "4.12 Cartografia vascular": 389.98
    }
    total_4 = renderizar_categoria("4. Despesas estrutura e de consumo", itens_estrutura, "cat_4")

    itens_admin = {
        "5.1 Contador": 800.00, "5.2 Jader Auxiliar SDM": 1000.00, "5.3 Entidades de Classe": 161.19,
        "5.4 Licenças, Alvarás e certidões": 407.11, "5.5 Outras despesas administrativas": 25.00
    }
    total_5 = renderizar_categoria("5. Despesas Administrativas e Licenças", itens_admin, "cat_5")

    itens_ti = {"6.1 Sistemas de gestão | amigo": 1005.74, "6.2 Pacote Office e Antivirus": 0.00, "6.3 Chat bot": 270.00}
    total_6 = renderizar_categoria("6. Despesas com TI", itens_ti, "cat_6")

    itens_bancarias = {"7.1 Taxa admin de contas": 94.73, "7.2 Máquinas de cartão": 0.00, "7.3 Iof / juros": 0.00, "7.4 Outras": 2.37}
    total_7 = renderizar_categoria("7. Despesas bancárias", itens_bancarias, "cat_7")

    itens_marketing = {
        "8.1 Agência": 0.00, "8.2 Eventos": 4723.33, "8.3 Social mídia": 1300.00,
        "8.4 Tráfego Pago": 1800.00, "8.5 Patrocínio": 1000.00, "8.6 Facebook": 0.00, "8.7 Outras": 1706.67
    }
    total_8 = renderizar_categoria("8. Marketing e vendas", itens_marketing, "cat_8")

custo_fixo_mensal = total_1 + total_2 + total_3 + total_4 + total_5 + total_6 + total_7 + total_8
custo_fixo_anual = custo_fixo_mensal * 12

# --- COLUNA DE DASHBOARD E RESULTADOS ---
with col_dashboard:
    st.subheader("Cálculo da Hora Clínica")
    st.info(f"**Despesa Anual:** R$ {custo_fixo_anual:,.2f}")
    st.success(f"**Custo Fixo Mensal:** R$ {custo_fixo_mensal:,.2f}")
    st.divider()
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        # Iniciando parâmetros na memória também para serem salvos
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
    custo_dia_clinica = custo_fixo_mensal / dias_mensais if dias_mensais > 0 else 0
    custo_hora_atendimento = custo_hora_clinica / qtd_salas if qtd_salas > 0 else 0
    custo_dia_atendimento = custo_dia_clinica / qtd_salas if qtd_salas > 0 else 0

    st.markdown("#### Índices")
    st.write(f"**Custo Hora Clínica:** R$ {custo_hora_clinica:,.2f}")
    st.write(f"**Custo Dia Clínica:** R$ {custo_dia_clinica:,.2f}")
    st.write(f"**Custo Hora (Sala):** R$ {custo_hora_atendimento:,.2f}")
    st.write(f"**Custo Dia (Sala):** R$ {custo_dia_atendimento:,.2f}")

st.divider()

# --- ABA DE RESUMO ---
st.subheader("RESUMO GERAL")
df_resumo = pd.DataFrame({
    "RESUMO": ["1. Despesa com pessoal", "2. Seguros", "3. Manutenção", "4. Estrutura", "5. Admin/Licenças", "6. TI", "7. Bancárias", "8. Marketing"],
    "Média Mensal": [total_1, total_2, total_3, total_4, total_5, total_6, total_7, total_8]
})
df_resumo["% Custo"] = (df_resumo["Média Mensal"] / custo_fixo_mensal) if custo_fixo_mensal > 0 else 0

estilo_resumo = df_resumo.style.format({"Média Mensal": "R$ {:,.2f}", "% Custo": "{:.0%}"})
st.dataframe(estilo_resumo, use_container_width=True, hide_index=True)

st.markdown(f"""
<div style="background-color: #4CAF50; padding: 10px; border-radius: 5px; color: white;">
    <h4 style="margin:0; color: white;">Total Despesas Mensais: R$ {custo_fixo_mensal:,.2f}</h4>
</div>
""", unsafe_allow_html=True)