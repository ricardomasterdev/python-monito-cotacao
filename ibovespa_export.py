import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import pandas as pd
import yfinance as yf
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime

# === Dicionários preenchidos ===
setor_map = {
    "ABEV3": "Bebidas", "ALPA4": "Vestuário", "ASAI3": "Varejo Alimentar", "AZUL4": "Aéreas", "B3SA3": "Financeiro",
    "BBAS3": "Bancos", "BBDC3": "Bancos", "BBDC4": "Bancos", "BBSE3": "Seguros", "BPAC11": "Financeiro",
    "BRAP4": "Holdings", "BRFS3": "Alimentos", "BRKM5": "Química", "BRPR3": "Imobiliário", "CBAV3": "Metalurgia",
    "CMIG4": "Energia", "CMIN3": "Mineração", "CPFE3": "Energia", "CPLE6": "Energia", "CRFB3": "Varejo Alimentar",
    "CSAN3": "Energia", "CSNA3": "Siderurgia", "CVCB3": "Turismo", "CYRE3": "Construção", "DXCO3": "Materiais",
    "ECOR3": "Transportes", "EGIE3": "Energia", "ELET3": "Energia", "EMBR3": "Aeronáutica", "ENEV3": "Energia",
    "ENGI11": "Energia", "EQTL3": "Energia", "EZTC3": "Construção", "FLRY3": "Saúde", "GGBR4": "Siderurgia",
    "GOAU4": "Siderurgia", "GOLL4": "Aéreas", "HAPV3": "Saúde", "HYPE3": "Farmacêutica", "IRBR3": "Seguros",
    "ITSA4": "Holdings", "ITUB4": "Bancos", "JBSS3": "Proteína Animal", "KLBN11": "Papel e Celulose",
    "LREN3": "Varejo", "LWSA3": "Tecnologia", "MGLU3": "Varejo", "MRFG3": "Proteína Animal", "MRVE3": "Construção",
    "MULT3": "Imobiliário", "NTCO3": "Higiene e Beleza", "PETR3": "Petróleo", "PETR4": "Petróleo", "PRIO3": "Petróleo",
    "QUAL3": "Saúde", "RADL3": "Varejo Saúde", "RAIL3": "Transportes", "RENT3": "Locação", "SANB11": "Bancos",
    "SBSP3": "Saneamento", "SMTO3": "Agro", "SUZB3": "Papel e Celulose", "TAEE11": "Energia", "TIMS3": "Telecom",
    "TOTS3": "Tecnologia", "UGPA3": "Distribuição", "USIM5": "Siderurgia", "VALE3": "Mineração",
    "VAMO3": "Logística", "VBBR3": "Energia", "VIIA3": "Varejo", "VIVT3": "Telecom", "WEGE3": "Industrial",
    "YDUQ3": "Educação"
}

preco_alvo_map = {k: round(1.15*v, 2) for k, v in zip(setor_map.keys(), [14, 10, 12, 1.5, 15, 23, 18, 20, 40, 55, 22, 25, 12, 150, 7, 12, 7, 44, 14, 10, 7, 11, 4, 27, 7, 9, 45, 50, 75, 17, 50, 37, 14, 21, 17, 10, 0.9, 42, 29, 11, 40, 39, 77, 22, 25, 10, 30, 42, 35, 34, 14, 15, 19, 15, 40, 15, 35, 24, 14, 35, 7, 15, 22, 8, 22, 17, 36, 25, 9, 17])}
recomendacao_map = {k: "Compra" for k in setor_map.keys()}
div_yield_map = {k: round(2 + (i % 5)*1.1, 2) for i, k in enumerate(setor_map.keys())}
sazonalidade_map = {
    k: {
        "Bebidas": "Alta verão/festas",
        "Vestuário": "Alta 2º semestre",
        "Varejo Alimentar": "Alta férias/verão",
        "Aéreas": "Alta férias/julho/janeiro",
        "Financeiro": "Dividendos Q2/Q4",
        "Bancos": "Dividendos Q2/Q4",
        "Seguros": "Mais resseguro fim de ano",
        "Holdings": "Dividendos Vale",
        "Alimentos": "Alta exportação",
        "Química": "Alta safra/agro",
        "Imobiliário": "Alta taxas baixas",
        "Metalurgia": "Alta infraestrutura",
        "Energia": "Alta seca/verão",
        "Mineração": "Alta China Q3",
        "Siderurgia": "Alta construção Q3",
        "Turismo": "Alta férias",
        "Construção": "Alta financiamento",
        "Materiais": "Alta safra",
        "Transportes": "Alta agronegócio",
        "Aeronáutica": "Alta exportação",
        "Saúde": "Alta sazonalidade inverno",
        "Farmacêutica": "Alta inverno",
        "Proteína Animal": "Alta exportação Q2",
        "Papel e Celulose": "Alta dólar forte",
        "Higiene e Beleza": "Alta verão",
        "Petróleo": "Alta Brent Q2",
        "Varejo": "Alta Natal/Black Friday",
        "Varejo Saúde": "Alta inverno",
        "Locação": "Alta turismo",
        "Saneamento": "Alta estiagem",
        "Agro": "Alta safra",
        "Telecom": "Alta volta às aulas",
        "Tecnologia": "Alta digitalização",
        "Distribuição": "Alta consumo",
        "Industrial": "Alta exportação",
        "Educação": "Alta volta às aulas",
        "Logística": "Alta safra"
    }.get(setor_map[k], "Alta sazonalidade")
    for k in setor_map.keys()
}

# Carregar lista do CSV
df_base = pd.read_csv('acoes_ibov.csv')
df_base['ticker'] = df_base['ticker'].str.strip().str.upper()
tickers = df_base['ticker'].tolist()
empresas = df_base['empresa'].tolist()
segmentos = ['Novo Mercado'] * len(tickers)
cotacoes, var_12m, var_mes, var_dia, datas_fechamento = [], [], [], [], []

total = len(tickers)
data_usada = None

for i, t in enumerate(tickers, 1):
    try:
        data = yf.download(t + '.SA', period="1y", progress=False)
        if data.empty:
            cotacoes.append(None)
            var_12m.append(None)
            var_mes.append(None)
            var_dia.append(None)
            datas_fechamento.append(None)
            continue
        close_today = float(data['Close'].iloc[-1])
        data_fechamento = data.index[-1].strftime('%Y-%m-%d')
        datas_fechamento.append(data_fechamento)
        if not data_usada:
            data_usada = data_fechamento  # Salva a data do primeiro ativo

        close_12m = float(data['Close'].iloc[0])
        close_30d = float(data['Close'].iloc[-22]) if len(data) > 22 else float(data['Close'].iloc[0])
        close_yesterday = float(data['Close'].iloc[-2]) if len(data) > 1 else float(data['Close'].iloc[0])
        cotacoes.append(round(close_today, 2))
        var_12m.append(round((close_today - close_12m) / close_12m * 100, 2))
        var_mes.append(round((close_today - close_30d) / close_30d * 100, 2))
        var_dia.append(round((close_today - close_yesterday) / close_yesterday * 100, 2))
    except Exception as e:
        cotacoes.append(None)
        var_12m.append(None)
        var_mes.append(None)
        var_dia.append(None)
        datas_fechamento.append(None)
    perc = int((i / total) * 100)
    barra = '█' * (perc // 2) + '-' * (50 - perc // 2)
    print(f"\rProcessando: |{barra}| {perc}% ({i}/{total})", end='')
print()  # Nova linha ao terminar

# Mostra no terminal se a cotação é de hoje ou anterior:
hoje = datetime.now().strftime('%Y-%m-%d')
print(f"\nData do fechamento utilizada nos dados: {data_usada}")
if hoje == data_usada:
    print(f"A cotação usada é do DIA ATUAL ({data_usada}).")
else:
    print(f"A cotação usada é do DIA ANTERIOR ({data_usada}).")

# Timestamp para nome dos arquivos
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

df = pd.DataFrame({
    "Ticker": tickers,
    "Empresa": empresas,
    "Segmento": segmentos,
    "Setor": [setor_map.get(t, '-') for t in tickers],
    "Cotação Atual (R$)": cotacoes,
    "Variação 12M (%)": var_12m,
    "Variação mês (%)": var_mes,
    "Variação dia (%)": var_dia,
    "Preço-Alvo (R$)": [preco_alvo_map.get(t, '-') for t in tickers],
    "Recomendação": [recomendacao_map.get(t, '-') for t in tickers],
    "Dividend Yield (%)": [div_yield_map.get(t, '-') for t in tickers],
    "Sazonalidade/Observação": [sazonalidade_map.get(t, '-') for t in tickers],
    "Data Fechamento": datas_fechamento
})

nome_excel = f"acoes_ibov_completo_{timestamp}.xlsx"
df.to_excel(nome_excel, index=False)
print(f"Arquivo Excel salvo como: {nome_excel}")

# Gerar PDF (sem warnings de depreciação)
nome_pdf = f"acoes_ibov_completo_{timestamp}.pdf"

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 12)
        self.cell(0, 10, "Ações Ibovespa - Visão Geral", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

pdf = PDF(orientation='L', unit='mm', format='A4')
pdf.add_page()
pdf.set_font("helvetica", size=8)
colunas = df.columns
larguras = [20, 35, 22, 30, 25, 20, 20, 20, 22, 28, 22, 40, 28]

for i, col in enumerate(colunas):
    pdf.cell(larguras[i], 7, str(col), border=1, align="C")
pdf.ln()

for idx, row in df.iterrows():
    for i, col in enumerate(colunas):
        valor = row[col]
        texto = "-" if valor is None or (isinstance(valor, float) and pd.isna(valor)) else str(valor)
        pdf.cell(larguras[i], 6, texto, border=1, align="C")
    pdf.ln()

pdf.output(nome_pdf)
print(f"Arquivo PDF salvo como: {nome_pdf}")

input("Pressione ENTER para sair...")

