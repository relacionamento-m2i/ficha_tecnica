import streamlit as st
import pandas as pd
import json
import plotly.express as px

# Fallback caso o arquivo banco_servicos não esteja no mesmo diretório na hora do teste
try:
    from banco_servicos import obter_servicos_cadastrados
except ImportError:
    def obter_servicos_cadastrados(): return {}

# ==========================================
# CONFIGURAÇÕES GERAIS E ESTILOS
# ==========================================
COR_CABECALHO = "#7030A0"
COR_FUNDO_CLARO = "#E6E0EC"
COR_TEXTO_BRANCO = "#FFFFFF"

# ==========================================
# INICIALIZAÇÃO DE MEMÓRIA GLOBAL SEGURA
# ==========================================
if "db_servicos" not in st.session_state:
    lista_novos_servicos = [
        ("Consulta Ginecologista", 800.00), ("Consulta BC Woman Ginecologia", 600.00),
        ("Pacote com 2 Consultas Gineco", 1400.00), ("Pacote com 3 Consultas Gineco", 1800.00),
        ("BC FAMILY GINECO 6 PARCELADO | 2 membros", 3000.00), ("BC FAMILY GINECO 6 A VISTA | 2 membros", 2900.00),
        ("BC FAMILY GINECO 3 ADICIONAL PARCELADO", 1500.00), ("BC FAMILY GINECO 3 ADICIONAL A VISTA", 1500.00),
        ("Consulta Nutricionista Gineco", 350.00), ("Implante Masculino (6 meses) Standard (Até 5 pellets)", 5000.00),
        ("Implante Masculino (6 meses) Standard 6 pellets", 5500.00), ("Implante Masculino (6 meses) Standard 7 pellets", 6000.00),
        ("Implante Masculino (6 meses) Standard 8 pellets", 6500.00), ("Implante Masculino (6 meses) Standard 9 pellets", 7000.00),
        ("Implante Masculino (6 meses) Standard 10 pellets", 7500.00), ("Implante Feminino Silástico (1 ano) COM Gestrinona G3+ (ACIMA DE 3 GESTRINONAS)", 9200.00),
        ("Implante Feminino Silástico (1 ano) COM Gestrinona G3+ A VISTA", 9000.00), ("Implante Feminino Silástico (1 ano) COM Gestrinona ATÉ G3", 8000.00),
        ("Implante Feminino Silástico (1 ano) COM Gestrinona ATÉ G3 A VISTA", 7800.00), ("Implante Feminino | Silástico (1 ano) SEM Gestrinona", 5500.00),
        ("Implante Feminino | Silástico (1 ano) SEM Gestrinona A VISTA", 5000.00), ("Implante Feminino com Gestrinona | Absorvivel (6 meses) EX: G80, E50, T80", 5000.00),
        ("Implante Feminino com Gestrinona | Absorvivel (6 meses) A VISTA", 4100.00), ("Implante Feminino sem Gestrinona | Absorvivel (6 meses) EX: E50, T80", 3500.00),
        ("Implante Feminino sem Gestrinona | Absorvivel (6 meses) A VISTA", 2750.00), ("Dose testosterona (absorvivel)", 600.00),
        ("Implante NADH 100 mg (antioxidante / Fadiga)", 1000.00), ("Implante NADH 200 mg (antioxidante / Fadiga)", 1200.00),
        ("Implante GINO PLUS (testo + Nadh)", 3000.00), ("Implante GINO PLUS (testo + Nadh) A VISTA", 2800.00),
        ("Inserção DIU Procedimento", 1800.00), ("Inserção DIU Myrena / Kyleena", 3500.00), ("Inserção Diu cobre / prata", 2500.00),
        ("Sessão Laser Intimo", 6000.00), ("Pacote com 3 Sessões Laser Íntimo", 5400.00), ("Ninfoplastia", 10000.00),
        ("Colposcopia", 120.00), ("Vulvoscopia", 120.00), ("Biopsia", 350.00), ("Vaginoscopia", 120.00),
        ("BIÓPSIA DE VULVA / VAGINA / COLO / ENDOMETRIO", 350.00), ("PROCEDIMENTO DIAGNOSTICO EM CITOPATOLOGIA CÉRVICO-VAGINAL ONCÓTICO", 140.00),
        ("BACTERIOSCOPIA (GRAM, ZIEHL, ALBERT ETC.), POR LÂMINA", 30.00), ("EXAME BACTERIOSCÓPICO DE SECREÇÃO VAGINAL", 70.00),
        ("HPV (vírus do papiloma humano) + subtipagem quando necessário PCR - pesquisa", 1280.00), ("CHLAMYDIA TRACHOMATIS, DETECÇÃO DO DNA POR TÉCNICAS DE HIBRIDIZAÇÃO OU PCR", 930.00),
        ("CAPTURA HÍBRIDA - PAINEL", 1770.00), ("GONOCOCO", 60.00)
    ]
    st.session_state["db_servicos"] = {
        nome: {
            "tempo_min": 60, "maquinas": [], "repasse_fixo": 0.0, "insumos": [],
            "taxas": {"comissao": 0.0, "cartao": 0.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
            "preco_escolhido": preco
        } for nome, preco in lista_novos_servicos
    }

if "df_lista_equipamentos" not in st.session_state:
    st.session_state["df_lista_equipamentos"] = pd.DataFrame({
        "Nome do equipamento": ["USG PHILLIPS"],
        "Valor de aquisição (R$)": [100000.00], 
        "Tempo de vida útil (anos)": [10.0],
        "Capacidade de Aplicações / dia (R$)": [800.00], 
        "Aplicações (média diária)": [8.0], 
        "Custo anual de manutenção (R$)": [1000.00]
    })

if "df_lista_insumos" not in st.session_state:
    lista_insumos_padrao = [
        ("ADRENALINA", 1.0, 1.30), ("ÁGUA OXIGENADA (mL)", 1.0, 0.04), ("AGULHA 0,40x12", 1.0, 0.56),
        ("AGULHA 13x0,3", 1.0, 0.10), ("AGULHA 27 G 1/2", 1.0, 2.50), ("AGULHA 30x0,8", 1.0, 0.05),
        ("AGULHA 40x12", 1.0, 0.20), ("AGULHA ASPIRAÇÃO", 1.0, 0.35), ("ÁLCOOL (mL)", 1.0, 0.05),
        ("ÁLCOOL À 70%", 1.0, 0.008), ("ATIVO (mL)", 1.0, 16.00), ("BRINDE", 1.0, 50.00),
        ("CANETA BRANCA DE MARCAÇÃO", 1.0, 1.00), ("CAPA PARA USG", 1.0, 3.00), ("CARTUCHO DA PONTEIRA", 1.0, 200.00),
        ("CLOREXIDINA ALCÓOLICA (mL)", 1.0, 0.02), ("EQUIPO", 1.0, 1.00), ("ESTERILIZAÇÃO (KIT DE ENDOLASER E MICROPORE)", 1.0, 15.00),
        ("FIBRA ÓTICA", 1.0, 750.00), ("GAZE", 1.0, 4.583), ("GEL TRANSDUTOR (g)", 1.0, 0.01),
        ("GLICOSE + LIDOCAÍNA (mL)", 1.0, 2.50), ("INTRODUTOR", 1.0, 38.00), ("JELCO", 1.0, 0.80),
        ("KIT DE CREMES DA LINHA DRA. THACIRA", 3.0, 160.00), ("KIT DESCARTÁVEL", 1.0, 95.00), ("KOMPREX (cm)", 1.0, 0.335),
        ("LANCHE", 1.0, 50.00), ("LENÇOL DESCARTÁVEL ELÁSTICO", 1.0, 6.25), ("LIDOCAÍNA GEL", 1.0, 5.40),
        ("LIDOCAÍNA S/ VASO 20 mL", 1.0, 5.50), ("LUVA (Par)", 1.0, 2.50), ("LUVA ESTÉRIL (Par)", 1.0, 2.00),
        ("LUVAS DE PROCEDIMENTOS", 1.0, 0.50), ("MANTA", 1.0, 35.00), ("MANUAL DO PACIENTE", 1.0, 20.00),
        ("MÁSCARA PARA NITROSO", 1.0, 60.00), ("MEIA DE COMPRESSÃO", 1.0, 85.00), ("MICROPORE", 1.0, 9.00),
        ("MICROPORE (cm)", 1.0, 0.045), ("MOLELAST (cm)", 1.0, 0.036), ("NITROSO", 1.0, 200.00),
        ("ÓXIDO NITROSO", 1.0, 80.00), ("OXIGÊNIO", 1.0, 20.00), ("PAPEL PARA MACA (m)", 1.0, 0.50),
        ("POLIDOCANOL (mL)", 1.0, 3.92), ("POLIDOCANOL VÁRIAS CONCENTRAÇÕES (mL)", 1.0, 2.80), ("POMADA REGENERADORA", 1.0, 58.00),
        ("PRO-PÉ", 1.0, 1.00), ("RIO HANDS (mL)", 1.0, 0.24), ("SCALP", 1.0, 0.21),
        ("SERINGA 10 mL", 1.0, 0.25), ("SERINGA 3 mL", 1.0, 2.50), ("SERINGA 5 mL", 1.0, 4.00),
        ("SHORT DESCARTÁVEL", 1.0, 15.00), ("SORO 1000 mL", 1.0, 9.30), ("SORO 500 mL", 1.0, 5.00),
        ("TAPPING", 1.0, 27.00), ("THREE WAY", 1.0, 0.92), ("ÁCIDO TRANEXÂMICO", 1.0, 5.00),
        ("ALGODÃO ROLO HIDROFILO 500GR", 1.0, 24.33), ("SORO FISIOLOGICO 250ML", 1.0, 6.43), ("GESTRINONA 40 MG - IMPLANTE SILAST", 1.0, 404.67),
        ("FIBROMIALGIA", 1.0, 82.83), ("TESTOSTERONA 200 MG - IMPLANTE", 1.0, 255.82), ("TESTOSTERONA 50 MG - IMPLANTE", 1.0, 105.67),
        ("SORO FISOLOGICO 500 ML", 1.0, 0.81), ("LIDOCAINA XYLESTESIN 2% COM VASO", 1.0, 15.53), ("ÁGUA DESTILADA 10 ML", 1.0, 0.58),
        ("KIT CRESCIMENTO DOS FIOS", 1.0, 98.23), ("KIT HIDRATAÇÃO DOS FIOS", 1.0, 52.80), ("KIT DERMATITE SEBORREICA,CASPA E PRURIDO NO COURO CABELUDO", 1.0, 70.40),
        ("KIT ALOPECIA PADRAO FEMININO", 1.0, 354.60), ("KIT ALOPECIA AREATA EM PLACA", 1.0, 186.23), ("KIT ANTIAGING- ENVELHECIMENTO CAPILAR E CANICE", 1.0, 144.32),
        ("KIT PÓS PRAIA", 1.0, 70.40), ("KIT EFLÚVIO TELÓGENO PÓS PARTO", 1.0, 41.36), ("KIT CRESCIMENTO DE BARBA", 1.0, 125.67),
        ("KIT EFLÚVIOTELÓGENO", 1.0, 134.47), ("KIT ALOPECIA ANDROGENÉTICA MASCULINA", 1.0, 241.86), ("Minoxidil 0,5% (5mg/ml) 2ml", 1.0, 6.82),
        ("DUTASTERIDA 0,1%", 1.0, 11.02), ("bFGF; IGF; VEGF; Copper Peptídeo* 1,2% 2ml", 1.0, 16.02), ("EPINEFRINA 1 MG/ML", 1.0, 2.39),
        ("ATROPINA 0,25 MG/ML 1ML AMP", 1.0, 1.45), ("FOSFATO DISSODICO DE DEXAMETASONA 4 MG/ML SOL INJ CX 100 AMP VD INC X 2,5 ML(EMB HOSP)", 1.0, 3.99),
        ("CLOREXIDINA 2% ALMOT.100ML", 1.0, 15.04), ("TESTE COVID-19", 1.0, 10.40), ("HEPARINA", 1.0, 9.98),
        ("LEVOFLOXACINO 5 MG/ML", 1.0, 14.15), ("FENTANEST 0,05 MG/ML", 1.0, 66.00), ("ADREN 1 MG/ML SOL INJ", 1.0, 2.59),
        ("Trocater masculino", 1.0, 0.0), ("Trocater feminino", 1.0, 0.0), ("Campo operatório estéril", 1.0, 0.0),
        ("Lâmina de bisturir nº 11", 1.0, 0.0), ("seringa de 20 ml", 1.0, 0.0), ("Anestesia sistesin com vaso - mL", 1.0, 0.0),
        ("Anestesia sistesin sem vaso - mL", 1.0, 0.0), ("Agulha Rosa - 40x1,20 mm", 1.0, 0.0), ("Agulha Amarela - 13x0,00 mm", 1.0, 0.0),
        ("Agulha Preta - 30x0,70 mm", 1.0, 0.0), ("Adesivo impermeável", 1.0, 0.0), ("Gaze - pacote", 1.0, 0.0),
        ("Implante Masculino Standard (Até 5 pellets)", 1.0, 0.0), ("Implante Masculino Standard 6 pellets", 1.0, 0.0), 
        ("Implante Masculino Standard 7 pellets", 1.0, 0.0), ("Implante Masculino Standard 8 pellets", 1.0, 0.0), 
        ("Implante Masculino Standard 9 pellets", 1.0, 0.0), ("Implante Masculino Standard 10 pellets", 1.0, 0.0), 
        ("Implante Feminino Silástico com Gestrinona G3 + (ACIMA DE 3 GESTRINONAS)", 1.0, 0.0), 
        ("Implante Feminino Silástico com Gestrinona (ATÉ 3 GESTRINONAS)", 1.0, 0.0), 
        ("Implante Feminino | Silástico sem Gestrinona", 1.0, 0.0), 
        ("Implante Feminino com Gestrinona | Absorvivel G80", 1.0, 0.0), 
        ("Implante Feminino com Gestrinona | Absorvivel E50", 1.0, 0.0), 
        ("Implante Feminino com Gestrinona | Absorvivel T80", 1.0, 0.0), 
        ("Implante Feminino sem Gestrinona | Absorvivel E50", 1.0, 0.0), 
        ("Implante Feminino sem Gestrinona | Absorvivel T80", 1.0, 0.0), 
        ("Implante NADH 100 mg(antioxidante / Fadiga)", 1.0, 0.0), 
        ("Implante NADH 200 mg(antioxidante / Fadiga)", 1.0, 0.0), 
        ("Implante GINO PLUS (testo + Nadh).", 1.0, 0.0), 
        ("Bandeja de Diu", 1.0, 0.0), ("Espéculo Vaginal", 1.0, 0.0), ("Material de ultrasson", 1.0, 0.0), 
        ("Diu - dispositivo", 1.0, 0.0), ("DIU Myrena / Kyleena", 1.0, 0.0), ("Inserção Diu cobre / prata", 1.0, 0.0), 
        ("Tesoura Kerron", 1.0, 0.0), ("Pote coletor", 1.0, 0.0), ("Algodão", 1.0, 0.0), 
        ("Escova Endocervical", 1.0, 0.0), ("Swab de algodão", 1.0, 0.0), ("Luvas de procedimento", 1.0, 0.0), 
        ("Lâmina de microscopia", 1.0, 0.0), ("Porta-lâminas", 1.0, 0.0), ("Espátula de Ayre", 1.0, 0.0), 
        ("Lâmina de vidro com extremidade fosca", 1.0, 0.0)
    ]
    st.session_state["df_lista_insumos"] = pd.DataFrame(lista_insumos_padrao, columns=["Material", "qt", "valor"])

if "df_lista_taxas" not in st.session_state:
    st.session_state["df_lista_taxas"] = pd.DataFrame({"Taxa": ["Débito", "Crédito 1x", "Crédito 3x"], "Porcentagem (%)": [0.80, 1.20, 3.50]})

if "df_custos_categorias" not in st.session_state:
    st.session_state["df_custos_categorias"] = {
        "1. Despesa com pessoal": pd.DataFrame([
            {"ÍTEM": "1.1 Total da folha de pagamento clt (com 13º)", "MENSAL (R$)": 36627.02},
            {"ÍTEM": "1.2 Despesas com alimentação e transporte", "MENSAL (R$)": 1172.38},
            {"ÍTEM": "1.3 Reserva para recisões", "MENSAL (R$)": 3662.70},
            {"ÍTEM": "Plano de Saúde", "MENSAL (R$)": 9000.00},
            {"ÍTEM": "PJ vendas", "MENSAL (R$)": 10000.00},
            {"ÍTEM": "INSS", "MENSAL (R$)": 25000.00},
            {"ÍTEM": "FGTS", "MENSAL (R$)": 7900.00},
            {"ÍTEM": "1.5 Despesa com treinamentos", "MENSAL (R$)": 200.00},
            {"ÍTEM": "Bonificação", "MENSAL (R$)": 8916.67},
            {"ÍTEM": "1.7 Uniformes", "MENSAL (R$)": 763.03}
        ]),
        "2. Seguros": pd.DataFrame([
            {"ÍTEM": "2.1 Seguros do estabelecimento", "MENSAL (R$)": 333.92},
            {"ÍTEM": "2.2 Seguro médico", "MENSAL (R$)": 0.0},
            {"ÍTEM": "2.3 Outros seguros", "MENSAL (R$)": 0.0}
        ]),
        "3. Manutenção e conservação": pd.DataFrame([
            {"ÍTEM": "3.1 Elevadores", "MENSAL (R$)": 0.0},
            {"ÍTEM": "3.2 Manutenção do prédio", "MENSAL (R$)": 2000.00},
            {"ÍTEM": "3.3 Coleta de lixo hospitalar", "MENSAL (R$)": 209.00},
            {"ÍTEM": "3.4 Manutenção de equipamentos", "MENSAL (R$)": 0.0},
            {"ÍTEM": "3.5 Pinturas", "MENSAL (R$)": 1666.67},
            {"ÍTEM": "3.6 jardins", "MENSAL (R$)": 1000.00},
            {"ÍTEM": "3.7 Limpeza de Vidro", "MENSAL (R$)": 389.00},
            {"ÍTEM": "3.8 Reserva compra equipamentos (depreciação)", "MENSAL (R$)": 0.0},
            {"ÍTEM": "3.9 Outras despesas", "MENSAL (R$)": 0.0}
        ]),
        "4. Despesas estrutura e de consumo": pd.DataFrame([
            {"ÍTEM": "4.1 Aluguel", "MENSAL (R$)": 21000.00},
            {"ÍTEM": "4.2 Café", "MENSAL (R$)": 1456.00},
            {"ÍTEM": "4.3 Energia Elétrica", "MENSAL (R$)": 6000.00},
            {"ÍTEM": "4.4 Água", "MENSAL (R$)": 2000.00},
            {"ÍTEM": "4.5 Material Oli Essence", "MENSAL (R$)": 843.00},
            {"ÍTEM": "4.6 Internet", "MENSAL (R$)": 715.00},
            {"ÍTEM": "4.7 Material de limpeza", "MENSAL (R$)": 2000.00},
            {"ÍTEM": "4.8 Material para copa / Experiencia do cliente", "MENSAL (R$)": 2500.00},
            {"ÍTEM": "4.9 Material de escritório", "MENSAL (R$)": 1000.00},
            {"ÍTEM": "4.10 IPTU", "MENSAL (R$)": 1166.67},
            {"ÍTEM": "4.11 Segurança Eletrônica", "MENSAL (R$)": 338.54}
        ]),
        "5. Despesas Administrativas": pd.DataFrame([
            {"ÍTEM": "5.1 Contador", "MENSAL (R$)": 6549.15},
            {"ÍTEM": "5.2 Advogado", "MENSAL (R$)": 5000.00},
            {"ÍTEM": "Consultoria Gestão", "MENSAL (R$)": 10000.00},
            {"ÍTEM": "CRM", "MENSAL (R$)": 537.18},
            {"ÍTEM": "5.3 Outras despesas administrativas (CERT. DIG.)", "MENSAL (R$)": 10.83}
        ]),
        "6. Despesas com TI": pd.DataFrame([
            {"ÍTEM": "Sistemas de gestão Amigo", "MENSAL (R$)": 1821.42},
            {"ÍTEM": "Suporte Técnico Suporte One", "MENSAL (R$)": 1200.00},
            {"ÍTEM": "Adobe", "MENSAL (R$)": 90.00},
            {"ÍTEM": "Hospedagem / site", "MENSAL (R$)": 170.00},
            {"ÍTEM": "Spotify", "MENSAL (R$)": 40.83},
            {"ÍTEM": "Chat bot / recursos de automação", "MENSAL (R$)": 762.00}
        ]),
        "7. Despesas bancárias": pd.DataFrame([
            {"ÍTEM": "7.1 Taxa administrativa de contas", "MENSAL (R$)": 0.0},
            {"ÍTEM": "7.2 Máquinas de cartão", "MENSAL (R$)": 0.0},
            {"ÍTEM": "7.3 Iof / juros", "MENSAL (R$)": 0.0},
            {"ÍTEM": "7.4 Outras despesas", "MENSAL (R$)": 0.0}
        ]),
        "8. Marketing e vendas": pd.DataFrame([
            {"ÍTEM": "8.1 Agência", "MENSAL (R$)": 9475.00},
            {"ÍTEM": "8.2 Tráfego", "MENSAL (R$)": 2000.00},
            {"ÍTEM": "8.3 Impulsionamento", "MENSAL (R$)": 7412.00},
            {"ÍTEM": "8.4 Outras despesas", "MENSAL (R$)": 0.0}
        ])
    }

if "dias_uteis_eq" not in st.session_state:
    st.session_state["dias_uteis_eq"] = 22.0

def df_maquinas_padrao(): return pd.DataFrame(columns=["nome", "custo"])
def df_insumos_padrao(): return pd.DataFrame(columns=["Material", "QT", "Preço (R$)"])

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

    st.markdown("### Selecione o Serviço para Visualizar/Editar:")
    st.selectbox(
        "Filtro", options=lista_nomes_servicos,
        index=lista_nomes_servicos.index(st.session_state["servico_atual"]) if st.session_state["servico_atual"] in lista_nomes_servicos else 0,
        key="combo_servico", on_change=lambda: carregar_servico_para_estado(st.session_state["combo_servico"]),
        label_visibility="collapsed"
    )

    if st.button("💾 Salvar Alterações deste Serviço no Banco", type="primary"):
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
                        st.rerun()
                        
        with tab_ren_m:
            if not df_maq.empty:
                c1, c2, c3 = st.columns([2, 2, 1])
                maq_renomear = c1.selectbox("Máquina atual:", options=df_maq["nome"].tolist(), key="sel_ren_maq_ficha")
                custo_atual_maq = df_maq[df_maq["nome"] == maq_renomear]["custo"].iloc[0]
                novo_nome_maq = c1.text_input("Mudar nome para:", value=maq_renomear, key="in_ren_maq_ficha")
                novo_custo_maq = c2.number_input("Mudar custo para (R$):", value=float(custo_atual_maq), min_value=0.0, step=10.0, format="%.2f", key="in_ren_custo_maq_ficha")
                
                st.write("")
                if c3.button("Salvar", key="btn_salvar_maq", use_container_width=True):
                    if novo_nome_maq:
                        idx = df_maq.index[df_maq["nome"] == maq_renomear].tolist()[0]
                        df_maq.at[idx, "nome"] = novo_nome_maq
                        df_maq.at[idx, "custo"] = novo_custo_maq
                        st.session_state["df_ficha_maquinas"] = df_maq
                        st.rerun()

        with tab_del_m:
            if not df_maq.empty:
                c1, c2, c3 = st.columns([2, 1, 1])
                maq_remover = c1.selectbox("Remover máquina:", options=df_maq["nome"].tolist(), key="sel_rem_maq_ficha")
                st.write("")
                if c2.button("🗑️ Remover", key="btn_rem_maq", use_container_width=True):
                    st.session_state["df_ficha_maquinas"] = df_maq[df_maq["nome"] != maq_remover]
                    st.rerun()
                st.write("")
                if c3.button("⚠️ Excluir TODAS", key="btn_rem_todas_maq", type="primary", use_container_width=True):
                    st.session_state["df_ficha_maquinas"] = df_maquinas_padrao()
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
                if c4.button("Salvar", key="btn_salvar_ins", use_container_width=True):
                    if novo_nome_ins:
                        idx = df_ins.index[df_ins["Material"] == ins_renomear].tolist()[0]
                        df_ins.at[idx, "Material"] = novo_nome_ins
                        df_ins.at[idx, "QT"] = nova_qt_ins
                        df_ins.at[idx, "Preço (R$)"] = novo_preco_ins
                        st.session_state["df_ficha_insumos"] = df_ins
                        st.rerun()

        with tab_del_i:
            if not df_ins.empty:
                c1, c2, c3 = st.columns([2, 1, 1])
                ins_remover = c1.selectbox("Remover insumo:", options=df_ins["Material"].tolist(), key="sel_rem_ins_ficha")
                st.write("")
                if c2.button("🗑️ Remover", key="btn_rem_ins", use_container_width=True):
                    st.session_state["df_ficha_insumos"] = df_ins[df_ins["Material"] != ins_remover]
                    st.rerun()
                st.write("")
                if c3.button("⚠️ Excluir TODOS", key="btn_rem_todos_ins", type="primary", use_container_width=True):
                    st.session_state["df_ficha_insumos"] = df_insumos_padrao()
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
    with st.sidebar:
        st.header("💾 Salvar / Carregar Custos Fixos")
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
        st.download_button("📥 Baixar Cenário", data=json.dumps(dados_salvar, indent=4), file_name="custos_fixos.json", mime="application/json")

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
            qtd_salas = st.number_input("Qtd de Salas", value=14.0, step=1.0, format="%.1f")

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
    st.subheader("RESUMO GERAL")
    col_tabela, col_grafico = st.columns([1, 2])
    
    with col_tabela:
        if resumo_dados:
            df_resumo = pd.DataFrame(resumo_dados)
            df_resumo["% de Custo"] = (df_resumo["Média Mensal"] / despesa_mensal_media) if despesa_mensal_media > 0 else 0.0
            st.dataframe(df_resumo.style.format({"Média Mensal": "R$ {:,.2f}", "% de Custo": "{:.1%}"}), use_container_width=True, hide_index=True)
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
                        "Categoria": cat, "Subitem": row["ÍTEM"], "Valor (R$)": valor,
                        "% na Categoria": pct_cat, "% no Total": pct_total
                    })

        if dados_grafico:
            df_grafico = pd.DataFrame(dados_grafico).sort_values(by="Valor (R$)", ascending=True)
            fig = px.bar(
                df_grafico, x="Valor (R$)", y="Subitem", color="Categoria", orientation="h", text="Valor (R$)", 
                custom_data=["% na Categoria", "% no Total"], title="Despesa Mensal por Subitem"
            )
            fig.update_traces(
                texttemplate='R$ %{text:,.2f}', textposition='outside',
                hovertemplate="<b>%{y}</b><br>Valor Mensal: R$ %{x:,.2f}<br>% na Categoria: %{customdata[0]:.1%}<br>% no Total Geral: %{customdata[1]:.1%}<extra></extra>"
            )
            fig.update_layout(height=max(400, len(df_grafico) * 35), margin=dict(l=10, r=10, t=40, b=10), yaxis_title="", xaxis_title="Valor Mensal (R$)", legend_title="Categoria", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Preencha valores maiores que zero nas despesas para visualizar o gráfico detalhado.")

# ==========================================
# MÓDULO 3: EQUIPAMENTOS
# ==========================================
def render_equipamentos():
    with st.sidebar:
        st.header("💾 Salvar / Carregar Equipamentos")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_eq")
        if arquivo_upload is not None:
            try:
                st.session_state["df_lista_equipamentos"] = pd.DataFrame(json.load(arquivo_upload)["df_lista_equipamentos"])
                st.success("Dados carregados!")
            except Exception: st.error("Erro ao ler o arquivo.")
        st.divider()
        dados_salvar = {"df_lista_equipamentos": st.session_state["df_lista_equipamentos"].to_dict(orient="records")}
        st.download_button("📥 Baixar Cenário", data=json.dumps(dados_salvar, indent=4), file_name="equipamentos.json", mime="application/json")

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
    with st.sidebar:
        st.header("💾 Salvar / Carregar Insumos")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_ins")
        if arquivo_upload is not None:
            try:
                st.session_state["df_lista_insumos"] = pd.DataFrame(json.load(arquivo_upload)["df_lista_insumos"])
                st.success("Dados carregados!")
            except Exception: st.error("Erro ao ler o arquivo.")
        st.divider()
        dados_salvar = {"df_lista_insumos": st.session_state["df_lista_insumos"].to_dict(orient="records")}
        st.download_button("📥 Baixar Cenário", data=json.dumps(dados_salvar, indent=4), file_name="insumos.json", mime="application/json")

    st.title("Lista de Insumos e Materiais")
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
    with st.sidebar:
        st.header("💾 Salvar / Carregar Taxas")
        arquivo_upload = st.file_uploader("Carregar backup (.json)", type=["json"], key="up_taxas")
        if arquivo_upload is not None:
            try:
                st.session_state["df_lista_taxas"] = pd.DataFrame(json.load(arquivo_upload)["df_lista_taxas"])
                st.success("Dados carregados!")
            except Exception: st.error("Erro ao ler o arquivo.")
        st.divider()
        dados_salvar = {"df_lista_taxas": st.session_state["df_lista_taxas"].to_dict(orient="records")}
        st.download_button("📥 Baixar Cenário", data=json.dumps(dados_salvar, indent=4), file_name="taxas.json", mime="application/json")

    st.title("Impostos e Taxas")
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