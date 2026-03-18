import streamlit as st
from fpdf import FPDF
import datetime

# --- BANCO DE DADOS DE CUSTOS ---
dados_custo = {
    "limite": [70000, 150000, 300000, 450000, 600000, 850000, 1000000, 3000000],
    12: [2500.0, 2917.8, 11671.2, 14589.0, 17506.8, 23342.4, 26260.2, 29178.0],
    24: [3890.4, 5835.6, 11671.2, 14589.0, 17506.8, 23342.4, 26260.2, 29178.0],
    36: [5835.6, 8753.4, 11671.2, 14589.0, 17506.8, 23342.4, 26260.2, 29178.0],
    48: [7780.8, 11671.2, 15561.6, 19452.0, 23342.4, 31123.2, 35013.6, 38904.0],
    60: [9726.0, 14589.0, 19452.0, 24315.0, 29178.0, 38904.0, 43767.0, 48630.0]
}

st.set_page_config(page_title="Gerador Dr. Fiscal", layout="centered")
st.title("📄 Gerador de Proposta RPC")

# --- ENTRADA DE DADOS ---
st.header("🏢 Dados do Cliente")
razao_social = st.text_input("Razão Social (Cliente)")
cnpj = st.text_input("CNPJ")

st.header("💰 Parâmetros do Cálculo")
col1, col2 = st.columns(2)
valor_credito = col1.number_input("Faixa de Crédito (R$)", min_value=0.0, step=1000.0, format="%.2f")
meses = col2.selectbox("Meses do Diagnóstico", [12, 24, 36, 48, 60])

percentual_unidade = st.slider("Percentual Unidade (%)", 0, 100, 25) / 100
qtd_parcelas = st.number_input("Quantidade de Parcelas", 1, 12, 5)

# --- LÓGICA DE CÁLCULO ---
def calcular_valores(valor, meses_ref):
    # Localiza o índice da faixa de crédito
    idx = next((i for i, lim in enumerate(dados_custo["limite"]) if valor <= lim), -1)
    custo_base = dados_custo[meses_ref][idx]
    # Cálculo do Total: Custo / (1 - Percentual)
    total = custo_base / (1 - percentual_unidade)
    return total, total / qtd_parcelas

if st.button("GERAR PROPOSTA FINAL EM PDF"):
    if not razao_social:
        st.error("Por favor, informe a Razão Social do cliente.")
    else:
        total_final, valor_parc = calcular_valores(valor_credito, meses)
        hoje = datetime.date.today().strftime("%d/%m/%Y")

        pdf = FPDF()
        pdf.add_page()
        
        # Carregamento da Fonte AmpleSoft
        try:
            pdf.add_font('AmpleSoft', '', 'AmpleSoft-Regular.ttf', uni=True)
            pdf.add_font('AmpleSoft', 'B', 'AmpleSoft-Bold.ttf', uni=True)
            font_main = 'AmpleSoft'
        except:
            font_main = 'Arial'

        # Logo (Opcional - Ativar se houver o arquivo logo.png no GitHub)
        # pdf.image('logo.png', x=150, y=10, w=40) 

        # Tabela de Identificação
        pdf.set_font(font_main, 'B', 10)
        pdf.cell(40, 10, "EMPRESA", 1)
        pdf.set_font(font_main, '', 10)
        pdf.cell(0, 10, razao_social.upper(), 1, ln=True)
        
        pdf.set_font(font_main, 'B', 10)
        pdf.cell(40, 10, "SERVIÇO", 1)
        pdf.set_font(font_main, '', 10)
        pdf.cell(0, 10, "Retificações Das Declarações e Compensações Mensais", 1, ln=True)
        
        pdf.set_font(font_main, 'B', 10)
        pdf.cell(40, 10, "EMISSÃO", 1)
        pdf.set_font(font_main, '', 10)
        pdf.cell(0, 10, hoje, 1, ln=True)
        
        # Texto do Escopo
        pdf.ln(10)
        pdf.set_font(font_main, '', 10)
        texto_intro = (f"A {razao_social}, após a identificação das oportunidades apresentadas no trabalho de "
                       "Diagnóstico Tributário apresentado pela Dr. Fiscal, verificou que a habilitação dos créditos "
                       "de PIS, COFINS, IRPJ e CSLL, bem como a correção de débitos de IRPJ e CSLL, dependem da "
                       "retificação das informações constantes da DCTF, ECF e EFD Contribuições.")
        pdf.multi_cell(0, 6, texto_intro)
        
        pdf.ln(5)
        pdf.set_font(font_main, 'B', 11)
        pdf.cell(0, 10, "Objetivo", ln=True)
        pdf.set_font(font_main, '', 10)
        pdf.multi_cell(0, 6, "A Dr. Fiscal prestará serviços de consultoria fiscal, no sentido de retificação das "
                             "obrigações fiscais acessórias, de acordo com as orientações e regulamentações emitidas "
                             "pela Receita Federal do Brasil.")

        # Investimento
        pdf.ln(5)
        pdf.set_font(font_main, 'B', 11)
        pdf.cell(0, 10, "Investimento", ln=True)
        pdf.set_font(font_main, '', 10)
        pdf.cell(0, 8, f"Remuneração: R$ {total_final:,.2f}", ln=True)
        pdf.cell(0, 8, f"Forma de Pagamento: A vista ou em até {qtd_parcelas} parcelas de R$ {valor_parc:,.2f}", ln=True)
        pdf.cell(0, 8, "Prazo para finalização: 60 dias", ln=True)
        
        # Validade
        pdf.ln(10)
        pdf.set_font(font_main, 'I', 9)
        pdf.cell(0, 10, "Esta proposta tem validade de 3 dias úteis.", ln=True)

        # Download
        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.success("✅ Proposta gerada!")
        st.download_button("📥 BAIXAR PROPOSTA EM PDF", data=pdf_bytes, file_name=f"Proposta_RPC_{razao_social}.pdf")