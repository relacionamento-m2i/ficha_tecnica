# Filtros Necessários

* Usuário seleciona um serviço ou mais e aparece só o selecionado

### Aba Considerando custo Indireto

* Com Custo Indireto ( hora clínica)? Ao optar por SIM, o custo da hora clínica é inserido no custo dos serviços (então tem um botão de sim ou não)

### Aba de Serviço
* Nome do Serviço
* Tempo de Execução
* Uso de Máquina/Equipamento
* Aluguel de Máquina (Hora)
* Repasse para Profissionais
* Custo materiais e insumos

### Aba de Taxas
* Comissão de vendas/ Repasse Bruto
* Taxa de Cartão
* Imposto
* Repasse (Sobre o Líquido)
* % Lucro sobre preço

### Aba Preço de Mercado
 * Preço Final
 * Comissão de Vendas
 * Taxa de Cartão
 * Imposto
 * Resultado Líquido
 * Repasse Médico
 * Custo de Serviço
 * Lucro
 * % Lucro


# Solução 
* A solução profissional e elegante para isso é criar um sistema de Salvar/Carregar (Save/Load): O usuário preenche tudo. Clica em um botão "Baixar Configuração" (gera um arquivinho .json leve com os valores dele). Quando ele voltar amanhã e der F5, basta clicar em "Carregar Configuração", enviar esse arquivinho, e o Streamlit preenche todos os campos magicamente com os valores salvos.