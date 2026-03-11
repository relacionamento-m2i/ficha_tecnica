# banco_servicos.py

def obter_servicos_cadastrados():
    return {
        "AVALIAÇÃO ESPECIALIZADA DA ESCOLIOSE (À VISTA)": {
            "tempo_min": 120, # 2 horas
            "maquinas": [{"nome": "CÂMERA FOTOGRÁFICA", "custo": 0.0}, {"nome": "SCANNER CORPORAL", "custo": 0.0}],
            "repasse_fixo": 0.0,
            "insumos": [],
            "taxas": {"comissao": 0.0, "cartao": 0.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
            "preco_escolhido": 400.00
        },
        "TRATAMENTO PARA ESCOLIOSE COM PLANO TRIMESTRAL - 10 SESSÕES (PARCELADO)": {
            "tempo_min": 600, # 10 horas
            "maquinas": [],
            "repasse_fixo": 799.20, # Fisioterapeutas
            "insumos": [],
            "taxas": {"comissao": 0.0, "cartao": 3.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
            "preco_escolhido": 1998.00
        },
        "TRATAMENTO PARA ESCOLIOSE COM PLANO TRIMESTRAL - 10 SESSÕES (À VISTA)": {
            "tempo_min": 600,
            "maquinas": [],
            "repasse_fixo": 720.00,
            "insumos": [],
            "taxas": {"comissao": 0.0, "cartao": 0.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
            "preco_escolhido": 1800.00
        },
        "FISIOTERAPIA AVANÇADA - ONDAS DE CHOQUE": {
            "tempo_min": 50,
            "maquinas": [{"nome": "ONDA DE CHOQUE", "custo": 0.0}],
            "repasse_fixo": 133.00,
            "insumos": [],
            "taxas": {"comissao": 0.0, "cartao": 3.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
            "preco_escolhido": 380.00
        },
         "FISIOTERAPIA AVANÇADA 3 SESSÕES (PARCELADO)- ONDAS DE CHOQUE": {
            "tempo_min": 150, # 2h30min
            "maquinas": [{"nome": "ONDA DE CHOQUE", "custo": 0.0}],
            "repasse_fixo": 399.00,
            "insumos": [],
            "taxas": {"comissao": 0.0, "cartao": 3.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
            "preco_escolhido": 1140.00
        },
        "FISIOTERAPIA AVANÇADA - SIS": {
            "tempo_min": 50,
            "maquinas": [{"nome": "SIS (SISTEMA SUPER INDUTIVO)", "custo": 0.0}],
            "repasse_fixo": 147.00,
            "insumos": [],
            "taxas": {"comissao": 0.0, "cartao": 3.0, "imposto": 12.0, "repasse_liq": 0.0, "lucro": 0.0},
            "preco_escolhido": 420.00
        }
    }